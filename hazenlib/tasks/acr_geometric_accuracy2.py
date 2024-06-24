"""
ACR Geometric Accuracy

https://www.acraccreditation.org/-/media/acraccreditation/documents/mri/largephantomguidance.pdf

Calculates geometric accuracy for slice 5 of medium ACR phantom using MagNET method; calculates distances between end rods on 3x3 rod object.
Distortion is reported as CoV between 3 horizontal distances and CoV between 3 vertical distances.
H.Richardson June 2024
"""

import os
import sys
import traceback
import numpy as np
import math as math

import skimage.measure
import skimage.transform
import skimage.morphology
from scipy import ndimage
import scipy.optimize as opt
from scipy.interpolate import interp1d
from skimage.measure import regionprops

from hazenlib.HazenTask import HazenTask
from hazenlib.ACRObject import ACRObject
import matplotlib.pyplot as plt
from hazenlib.utils import Rod
from copy import copy, deepcopy
from math import pi
import cv2


class ACRGeometricAccuracy2(HazenTask):
    """Geometric accuracy measurement class for DICOM images of the ACR phantom

    Inherits from HazenTask class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ACR_obj = ACRObject(self.dcm_list,kwargs)
        self.single_dcm = self.ACR_obj.dcms[4]
        self.pixel_size = self.single_dcm.PixelSpacing[0]
        self.img_size = self.single_dcm.Rows
        print(f'img_size is {self.img_size}')
        
    def run(self) -> dict:
        """Main function for performing geometric accuracy measurement
        using the first and fifth slices from the ACR phantom image set

        Returns:
            dict: results are returned in a standardised dictionary structure specifying the task name, input DICOM Series Description + SeriesNumber + InstanceNumber, task measurement key-value pairs, optionally path to the generated images for visualisation
        """

        # Identify relevant slices
#        slice1_dcm = self.ACR_obj.dcms[0]
        slice5_dcm = self.ACR_obj.dcms[4]

        # Initialise results dictionary
        results = self.init_result_dict()
        results["file"] = [self.img_desc(slice5_dcm)]

        arr = slice5_dcm.pixel_array
        sample_spacing = 0.25

        rods, rods_initial = self.get_rods(arr)
        horz_distances, vert_distances = self.get_rod_distances(rods)
        horz_distortion_mm, vert_distortion_mm = self.get_rod_distortions(
            horz_distances, vert_distances
        )
        correction_coefficients_mm = self.get_rod_distortion_correction_coefficients(
            horizontal_distances=horz_distances
        )

        horizontal_linearity_mm = np.mean(horz_distances) * self.pixel_size
        vertical_linearity_mm = np.mean(vert_distances) * self.pixel_size

        # calculate horizontal and vertical distances in mm from distances in pixels, for output

        horz_distances_mm = [round(x * self.pixel_size, 3) for x in horz_distances]

        vert_distances_mm = [round(x * self.pixel_size, 3) for x in vert_distances]

        if self.report:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(
                6, 1, gridspec_kw={"height_ratios": [3, 1, 1, 1, 1, 1]}
            )
            fig.set_size_inches(6, 16)
            fig.tight_layout(pad=1)

            self.plot_rods(axes[0], arr, rods, rods_initial)
            axes[5].axis("off")
            axes[5].table(
                cellText=[
                    [str(x) for x in horz_distances_mm]
                    + [str(np.around(horizontal_linearity_mm, 3))],
                    [str(x) for x in vert_distances_mm]
                    + [str(np.around(vertical_linearity_mm, 3))],
                ],
                rowLabels=["H-distances (S->I)", "V-distances (R->L)"],
                colLabels=["1", "2", "3", "mean/linearity"],
                colWidths=[0.15] * (len(horz_distances) + 1),  # plus one for linearity,
                rowLoc="center",
                loc="center",
            )

            img_path = os.path.realpath(
                os.path.join(self.report_path, f"{self.img_desc(slice5_dcm)}.png")
            )
            fig.savefig(img_path)
            self.report_files.append(img_path)

        # print(f"Series Description: {dcm.SeriesDescription}\nWidth: {dcm.Rows}\nHeight: {dcm.Columns}\nSlice Thickness(
        # mm):" f"{dcm.SliceThickness}\nField of View (mm): {hazenlib.get_field_of_view(dcm)}\nbandwidth (Hz/Px) : {
        # dcm.PixelBandwidth}\n" f"TR  (ms) : {dcm.RepetitionTime}\nTE  (ms) : {dcm.EchoTime}\nFlip Angle  (deg) : {
        # dcm.FlipAngle}\n" f"Horizontal line bottom (mm): {horz_distances[0]}\nHorizontal line middle (mm): {
        # horz_distances[2]}\n" f"Horizontal line top (mm): {horz_distances[2]}\nHorizontal Linearity (mm): {np.mean(
        # horz_distances)}\n" f"Horizontal Distortion: {horz_distortion}\nVertical line left (mm): {vert_distances[0]}\n"
        # f"Vertical line middle (mm): {vert_distances[1]}\nVertical line right (mm): {vert_distances[2]}\n" f"Vertical
        # Linearity (mm): {np.mean(vert_distances)}\nVertical Distortion: {vert_distortion}\n" f"Slice width top (mm): {
        # slice_width['top']['default']}\n" f"Slice width bottom (mm): {slice_width['bottom']['default']}\nPhantom tilt (
        # deg): {phantom_tilt_deg}\n" f"Slice width AAPM geometry corrected (mm): {slice_width['combined'][
        # 'aapm_tilt_corrected']}")

        distortion_values = {
            "vertical mm": round(vert_distortion_mm, 2),
            "horizontal mm": round(horz_distortion_mm, 2),
        }

        linearity_values = {
            "vertical mm": round(vertical_linearity_mm, 2),
            "horizontal mm": round(horizontal_linearity_mm, 2),
        }

        results["measurement"]["distortion"] = {
            "distortion values": distortion_values,
            "linearity values": linearity_values,
            "horizontal distances mm": horz_distances_mm,
            "vertical distances mm": vert_distances_mm,
        }
        return results
#-------------------------------------------------------------



#-----------------------------------------------------------------------------
    def sort_rods(self, rods):
        """Separate matrix of rods into sorted per row

        Args:
            rods (_type_): _description_

        Returns:
            _type_: _description_
        """
        lower_row = sorted(rods, key=lambda rod: rod.y)[-3:]
        lower_row = sorted(lower_row, key=lambda rod: rod.x)
        middle_row = sorted(rods, key=lambda rod: rod.y)[3:6]
        middle_row = sorted(middle_row, key=lambda rod: rod.x)
        upper_row = sorted(rods, key=lambda rod: rod.y)[0:3]
        upper_row = sorted(upper_row, key=lambda rod: rod.x)
        return lower_row + middle_row + upper_row

    def get_rods(self, arr):
        """Locate rods in the pixel array

        Args:
            arr (np.array): DICOM pixel array

        Returns:
            rods : array_like – centroid coordinates of rods
            rods_initial : array_like  – initial guess at rods (center-of mass)
            If fit_gauss_2d_to_rods fails just use the intitial centre_weighted position [HR June 2024]
        Notes:
            The rod indices are ordered as:
                012
                345
                678
        """

        # inverted image for fitting (maximisation)
 #       arr_inv = np.invert(arr)
        arr_inv = np.invert(arr)-65346+np.max(arr) # np.invert is just (65346-img) so adjust to give a normalised, inverted image
        if np.min(arr_inv) < 0:
            arr_inv = arr_inv + abs(
                np.min(arr_inv)
            )  # ensure voxel values positive for maximisation

        """ Initial Center-of-mass Rod Locator """

        #Mask image to central 3x3 rod region, which should be in central square between 30% - 70% of image limits
        #Mask required as thresholding technique sensitive to random noise in background causing lots of spurious thresholds with 10 regions
        mask_low=round(0.3 * self.img_size)
        mask_high=round(0.7 * self.img_size)
        #print(f'mask_low is {mask_low}, mask_high is {mask_high}')
        arr_inv[0:mask_low,:]=0
        arr_inv[mask_high:self.img_size,:]=0
        arr_inv[:,0:mask_low]=0
        arr_inv[:,mask_high:self.img_size]=0

        #Check data:
#        plt.imshow(arr, cmap=plt.cm.bone)  # set the color map to bone 
#        plt.show() 
#        plt.imshow(arr_inv, cmap=plt.cm.bone)  # set the color map to bone 
#        plt.show() 

        # threshold and binaries the image in order to locate the rods.
        img_max = np.max(arr_inv)  #arr # maximum number of img intensity
        #print(f'img_max= {img_max}')
        no_region = [None] * img_max

        img_tmp = arr_inv
        # step over a range of threshold levels from 0 to the max in the image
        # using the ndimage.label function to count the features for each threshold
        for x in range(0, img_max):
            tmp = img_tmp <= x
            labeled_array, num_features = ndimage.label(tmp.astype(int))
            no_region[x] = num_features
#            if num_features > 2:
#                print(f'For threshold = {x} num_features = {num_features}')
#                plt.imshow(tmp, cmap=plt.cm.bone)  # set the color map to bone 
#                plt.show()           

        # find the indices that correspond to 10 regions and pick the **maximum** - was median but this is more prone to error due to range of thresholds yielding 10 regions.
        #Using max should correspond to true rod regions more reliably than median. HR 05.06.24 
        index = [i for i, val in enumerate(no_region) if val == 10]
        new_index = self.find_gaps(index) #Remove data outside of centre continuous range; these outliers may be caused by noise and don't represent 10 true regions.

        #print(f'Indices of 10-labels images are {index}')
        #print(f'Indices of 10-labels images with gaps removed are {new_index}')
        #thres_ind=index[round(len(index)/2)]
        #thres_ind=index[len(new_index)-1]              #Changed threshold to max rather than median as median occasionally failed[HR June 2024]
        thres_ind = np.median(new_index).astype(int)    #Not clear whether median or max value is best. Max sometimes gives wrong positions for some rods.
        #print(f'Max index of 10-labels images is {thres_ind}')

        # Generate the labelled array with the threshold chosen
        img_threshold = img_tmp <= thres_ind
        #plt.imshow(img_threshold, cmap=plt.cm.bone)  # set the color map to bone 
        #plt.show() 
        
        labeled_array, num_features = ndimage.label(img_threshold.astype(int))
        #plt.imshow(labeled_array, cmap=plt.cm.bone)  # set the color map to bone 
        #plt.show()

        # check that we have got the 10 rods!
        if num_features != 10:
        #    print(f'num_features = {num_features}')
            sys.exit("Did not find the 9 rods.")

        # list of tuples of x,y coordinates for the centres
        rod_centres = ndimage.center_of_mass(arr, labeled_array, range(2, 11))

        rods = [Rod(x=x[1], y=x[0]) for x in rod_centres]
        rods = self.sort_rods(rods)
        rods_initial = deepcopy(rods)  # save for later
        #dummy=[np.round(elem,1) for elem in rod_centres]
        #print(dummy)


        """ Gaussian 2D Rod Locator """

        # setup bounding box dict
        # TODO: make these into Rod class properties and functions
        # rather than loop over 9 each time
        bbox = {
            "x_start": [],
            "x_end": [],
            "y_start": [],
            "y_end": [],
        }

        # Get average radius and inverse intensity of rods
        rprops = regionprops(labeled_array, arr_inv)[1:]  # ignore first label

        # get relevant label properties: radius and intensity
        bbox["rod_dia"] = [prop.feret_diameter_max for prop in rprops]
        bbox["intensity_max"] = [prop.intensity_max for prop in rprops]

        # Calculate mean
        radius_of_rods_mean = int(np.mean(bbox["rod_dia"]))
        # inv_intensity_of_rods_mean = int(np.mean(inv_intensity_of_rods))
        bbox["radius"] = int(np.ceil((radius_of_rods_mean * 2) / 2))

        # array extend bounding box regions around rods by radius no. pixels
        for rprop in rprops:
            bbox["x_start"].append(rprop.bbox[0] - bbox["radius"])
            bbox["x_end"].append(rprop.bbox[2] + bbox["radius"])
            bbox["y_start"].append(rprop.bbox[1] - bbox["radius"])
            bbox["y_end"].append(rprop.bbox[3] + bbox["radius"])

            # print(f'Rod {idx} – Bounding Box, x: ({bbox["x_start"][-1]}, {bbox["x_end"][-1]}), y: ({bbox["y_start"][-1]}, {bbox["y_end"][-1]})')

        x0, y0, x0_im, y0_im = ([None] * 9 for i in range(4))

        for idx in range(9):
            #x0[idx]=rods[idx].x         #|
            #y0[idx]=rods[idx].y         #|
            #x0_im[idx]=rods[idx].x      #|
            #y0_im[idx]=rods[idx].y      #| 
            cropped_data = arr_inv[
                bbox["x_start"][idx] : bbox["x_end"][idx],
                bbox["y_start"][idx] : bbox["y_end"][idx],
            ]
            try:
                x0_im[idx], y0_im[idx], x0[idx], y0[idx] = self.fit_gauss_2d_to_rods(
                    cropped_data,
                    bbox["intensity_max"][idx],
                    bbox["rod_dia"][idx],
                    bbox["radius"],
                    bbox["x_start"][idx],
                    bbox["y_start"][idx],
                )
                #print(f'Fitted point {idx} using Gaussian x0= {x0[idx]}, y0={y0[idx]}, x0_im={x0_im[idx]}, y0_im={y0_im[idx]}')
            except:         
                #x0[idx]=rods[idx].x         
                #y0[idx]=rods[idx].y         
                x0_im[idx]=rod_centres[idx][0]      
                y0_im[idx]=rod_centres[idx][1]        
                #print(f'Gaussian failed for point {idx}; centre-weighting x0_im={x0_im[idx]}, y0_im={y0_im[idx]}')
            # note: flipped x/y
            rods[idx].x = y0_im[idx]
            rods[idx].y = x0_im[idx]

        rods = self.sort_rods(rods)

        # save figure
        if self.report:
            fig, axes = plt.subplots(1, 3, figsize=(45, 15))
            fig.tight_layout(pad=1)
            # center-of-mass (original method)
            axes[0].set_title("Initial Estimate")
            axes[0].imshow(arr, cmap="gray")
            for idx in range(9):
                axes[0].plot(rods_initial[idx].x, rods_initial[idx].y, "y.")
            # gauss 2D
            axes[1].set_title("2D Gaussian Fit")
            axes[1].imshow(arr, cmap="gray")
            for idx in range(9):
                axes[1].plot(rods[idx].x, rods[idx].y, "r.")
            # combined
            axes[2].set_title("Initial Estimate vs. 2D Gaussian Fit")
            axes[2].imshow(arr, cmap="gray")
            for idx in range(9):
                axes[2].plot(rods_initial[idx].x, rods_initial[idx].y, "y.")
                axes[2].plot(rods[idx].x, rods[idx].y, "r.")
            img_path = os.path.realpath(
                os.path.join(
                    self.report_path,
                    f"{self.img_desc(self.single_dcm)}_rod_centroids.png",
                )
            )
            fig.savefig(img_path)
            self.report_files.append(img_path)

        return rods, rods_initial

    def plot_rods(self, ax, arr, rods, rods_initial):  # pragma: no cover
        """Plot rods and curve fit graphs

        Args:
            ax (matplotlib.pyplot.axis): image axis
            arr (dcm.pixelarray): pixel array (image of phantom)
            rods (_type_): _description_
            rods_initial (_type_): _description_

        Returns:
            matplotlib.pyplot.axis: _description_
        """
        ax.imshow(arr, cmap="gray")
        for idx, rod in enumerate(rods):
            # ax.plot(rods_initial[idx].x, rods_initial[idx].y, 'y.', markersize=2)  # center-of-mass method
            ax.plot(rod.x, rod.y, "r.", markersize=2)  # gauss 2D
            ax.scatter(
                x=rod.x + 5,
                y=rod.y - 5,
                marker=f"${idx+1}$",
                s=30,
                linewidths=0.4,
                c="w",
            )

        ax.set_title("Rod Centroids")
        return ax

    def get_rod_distances(self, rods):
        """
        Calculates horizontal and vertical distances between adjacent rods in pixels
        Changed this to return x and y distances between point, eg. rod(2).x - rod(0).x instead of abs. distances [HR 2024]

        Parameters
        ----------
        rods : array_like
            rod positions in pixels

        Returns
        -------
        horz_dist, vert_dist : array_like
            horizontal and vertical distances between rods in pixels

        """
        # TODO: move to be a function of the Rod class
        horz_dist = [
            float(rods[2].x - rods[0].x),
            float(rods[5].x - rods[3].x),
            float(rods[8].x - rods[6].x),
        ]    
        '''np.sqrt(
                np.square((rods[2].y - rods[0].y)) + np.square(rods[2].x - rods[0].x)
            ),
            np.sqrt(
                np.square((rods[5].y - rods[3].y)) + np.square(rods[5].x - rods[3].x)
            ),
            np.sqrt(
                np.square((rods[8].y - rods[6].y)) + np.square(rods[8].x - rods[6].x)
            ),
        ]'''

        vert_dist = [
            float(rods[0].y - rods[6].y),
            float(rods[1].y - rods[7].y),
            float(rods[2].y - rods[8].y),
        ]    
        '''np.sqrt(
                np.square((rods[0].y - rods[6].y)) + np.square(rods[0].x - rods[6].x)
            ),
            np.sqrt(
                np.square((rods[1].y - rods[7].y)) + np.square(rods[1].x - rods[7].x)
            ),
            np.sqrt(
                np.square((rods[2].y - rods[8].y)) + np.square(rods[2].x - rods[8].x)
            ),
        ]'''

        # calculate the horizontal and vertical distances
        horz_dist = np.asarray(horz_dist, dtype='float64')
        vert_dist = np.asarray(vert_dist, dtype='float64')
        Pixel_Size = float(self.pixel_size)
        horz_dist_mm = np.multiply(Pixel_Size, horz_dist)
        vert_dist_mm = np.multiply(Pixel_Size, vert_dist)
        return horz_dist, vert_dist#, horz_dist_mm, vert_dist_mm

    def get_rod_distortion_correction_coefficients(self, horizontal_distances) -> dict:
        """
        Removes the effect of geometric distortion from the slice width measurement. Assumes that rod separation is
        120 mm.

        Args:
            horizontal_distances (list): horizontal distances between rods, in pixels

        Returns:
            dict: dictionary containing top and bottom distortion coefficients, in mm
        """
        # TODO: move to be a function of the Rod class

        coefficients = {
            "top": np.mean(horizontal_distances[1:3]) * self.pixel_size / 120,
            "bottom": np.mean(horizontal_distances[0:2]) * self.pixel_size / 120,
        }
        coefficients = {
            "top": np.mean(horizontal_distances[1:3]) * self.pixel_size / 120,
            "bottom": np.mean(horizontal_distances[0:2]) * self.pixel_size / 120,
        }

        return coefficients

    def get_rod_distortions(self, horz_dist_mm, vert_dist_mm):
        """

        Args:
            horz_dist (list): horizontal distances
            vert_dist (list): vertical distances

        Returns:
            tuple of float: horizontal and vertical distortion values, in mm
        """

        horz_distortion = (
            100 * np.std(horz_dist_mm, ddof=1) / np.mean(horz_dist_mm)
        )  # ddof to match MATLAB std
        horz_distortion = (
            100 * np.std(horz_dist_mm, ddof=1) / np.mean(horz_dist_mm)
        )  # ddof to match MATLAB std
        vert_distortion = 100 * np.std(vert_dist_mm, ddof=1) / np.mean(vert_dist_mm)
        return horz_distortion, vert_distortion#, horz_dist_mm, vert_dist_mm


    def gauss_2d(self, xy_tuple, A, x_0, y_0, sigma_x, sigma_y, theta, C):
        """
        Create 2D Gaussian
        Based on code by Siân Culley, UCL/KCL
        See also: https://en.wikipedia.org/wiki/Gaussian_function#Two-dimensional_Gaussian_function

        Parameters
        ----------
        xy_tuple : grid of x-y coordinates
        A : amplitude of 2D Gaussian
        x_0 / y_0 : centre of 2D Gaussian
        sigma_x / sigma_y : widths of 2D Gaussian
        theta : rotation of Gaussian
        C : background/intercept of 2D Gaussian

        Returns
        -------
        gauss : 1-D list of Gaussian intensities

        """
        (x, y) = xy_tuple
        x_0 = float(x_0)
        y_0 = float(y_0)

        cos_theta_2 = np.cos(theta) ** 2
        sin_theta_2 = np.sin(theta) ** 2
        cos_2_theta = np.cos(2 * theta)
        sin_2_theta = np.sin(2 * theta)

        sigma_x_2 = sigma_x**2
        sigma_y_2 = sigma_y**2
        sigma_x_2 = sigma_x**2
        sigma_y_2 = sigma_y**2

        a = cos_theta_2 / (2 * sigma_x_2) + sin_theta_2 / (2 * sigma_y_2)
        b = -sin_2_theta / (4 * sigma_x_2) + sin_2_theta / (4 * sigma_y_2)
        c = sin_theta_2 / (2 * sigma_x_2) + cos_theta_2 / (2 * sigma_y_2)

        gauss = (
            A
            * np.exp(
                -(
                    a * (x - x_0) ** 2
                    + 2 * b * (x - x_0) * (y - y_0)
                    + c * (y - y_0) ** 2
                )
            )
            + C
        )
        gauss = (
            A
            * np.exp(
                -(
                    a * (x - x_0) ** 2
                    + 2 * b * (x - x_0) * (y - y_0)
                    + c * (y - y_0) ** 2
                )
            )
            + C
        )

        return gauss.ravel()

    def fit_gauss_2d_to_rods(
        self, cropped_data, gauss_amp, gauss_radius, box_radius, x_start, y_start
    ):
        """
        Fit 2D Gaussian to Rods
        - Important:
        --- This uses a cropped region around a rod. If the cropped region is too large,
        such that it includes signal with intensity similar to the rods, the fitting may fail.
        --- This is a maximisation function, hence the rods should have higher signal than the surrounding region
        Based on code by Siân Culley, UCL/KCL

        Args:
            cropped_data (np.array): 2D array of magnitude voxels (nb: should be inverted if rods hypointense)
            gauss_amp (float/int): initial estimate of amplitude of 2D Gaussian
            gauss_radius (int): initial estimate of centre of 2D Gaussian
            box_radius (int): 'radius' of box around rod
            x_start / y_start (int, int): coordinates of bounding box in original non-cropped data

        Returns:
            tuple of 4 values corresponding to:
                x0_im / y0_im : rod centroid coordinates in dimensions of original image
                x0 / y0 : rod centroid coordinates in dimensions of cropped image
        """

        # get (x,y) coordinates for fitting
        indices = np.indices(cropped_data.shape)

        # estimate initial conditions for 2d gaussian fit
        dims_crop = cropped_data.shape
        h_crop = dims_crop[0]
        w_crop = dims_crop[1]

        A = gauss_amp  # np.max() # amp of Gaussian
        sigma = gauss_radius / 2  # radius of 2D Gaussian
        C = np.mean(
            [
                cropped_data[0, 0],
                cropped_data[h_crop - 1, 0],
                cropped_data[0, w_crop - 1],
                cropped_data[h_crop - 1, w_crop - 1],
            ]
        )  # background – np.min(outside of rod within cropped_data)
        C = np.mean(
            [
                cropped_data[0, 0],
                cropped_data[h_crop - 1, 0],
                cropped_data[0, w_crop - 1],
                cropped_data[h_crop - 1, w_crop - 1],
            ]
        )  # background – np.min(outside of rod within cropped_data)

        # print("A:", A)
        # print("box_radius:", box_radius)
        # print("sigma:", sigma)
        # print("C:", C, "\n")

        p0 = [A, box_radius, box_radius, sigma, sigma, 0, C]
        # print(f'initial conditions for 2d gaussian fitting: {p0}\n')

        # do 2d gaussian fit to data
        popt_single, pcov_single = opt.curve_fit(
            self.gauss_2d, indices, cropped_data.ravel(), p0=p0
        )

        A = popt_single[0]
        x0 = popt_single[1]
        y0 = popt_single[2]
        sigma_x = popt_single[3]
        sigma_y = popt_single[4]
        theta = popt_single[5]
        C = popt_single[6]

        # print(f'results of 2d gaussian fitting: \n\tamplitude = {A_} \n\tx0 = {x0} \n\ty0 = {y0} \n\tsigma_x = {sigma_x} \n\tsigma_y = {sigma_y} \n\ttheta = {theta} \n\tC = {C} \n')

        # to get image coordinates need to add back on x_start and y_start
        x0_im = x0 + x_start
        y0_im = y0 + y_start

        # print(f'Initial centre was ({rods[idx].x}, {rods[idx].y}). Refined centre is ({x0_im}, {y0_im})\n')

        return x0_im, y0_im, x0, y0

    def find_gaps(self,index):
        new_index = index
        for i in range(len(index),round(len(index)/2),-1):
            if index[i-1]-index[i-2] !=1:
                new_index=new_index[0:i-1]

        for i in range(0,round(len(index)/2),1):
            if index[i+1]-index[i] !=1:
                new_index=new_index[i+1:]
        return new_index