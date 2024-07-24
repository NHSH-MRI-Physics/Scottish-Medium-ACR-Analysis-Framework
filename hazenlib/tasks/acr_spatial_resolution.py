"""
ACR Spatial Resolution (MTF)

https://www.acraccreditation.org/-/media/acraccreditation/documents/mri/largephantomguidance.pdf

Calculates the effective resolution (MTF50) for slice 1 for the ACR phantom. This is done in accordance with the
methodology described in Section 3 of the following paper:

https://opg.optica.org/oe/fulltext.cfm?uri=oe-22-5-6040&id=281325

WARNING: The phantom must be slanted for valid results to be produced. This test is not within the scope of ACR
guidance.

This script first identifies the rotation angle of the ACR phantom using slice 1. It provides a warning if the
slanted angle is less than 3 degrees.

The location of the ramps within the slice thickness are identified and a square ROI is selected around the anterior
edge of the slice thickness insert.

A rudimentary edge response function is generated based on the edge within the ROI to provide initialisation values for
the 2D normal cumulative distribution fit of the ROI.

The edge is then super-sampled in the direction of the bright-dark transition of the edge and binned at right angles
based on the edge slope determined from the 2D Normal CDF fit of the ROI to obtain the edge response function.

This super-sampled ERF is then fitted using a weighted sigmoid function. The raw data and this fit are then used to
determine the LSF and the subsequent MTF. The MTF50 for both raw and fitted data are reported.

The results are also visualised.

Created by Yassine Azma
yassine.azma@rmh.nhs.uk

22/02/2023
"""

import os
import sys
import traceback
import numpy as np

import cv2
import scipy
import skimage.morphology
import skimage.measure

from hazenlib.HazenTask import HazenTask
from hazenlib.ACRObject import ACRObject
from hazenlib.logger import logger

import sys
import matplotlib.pyplot as plt
import scipy.ndimage
import skimage.segmentation
from scipy.optimize import curve_fit
from scipy.interpolate import griddata
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import math
from enum import Enum

class ResOptions(Enum):
    DotMatrixMethod=1
    MTFMethod=2
    ContrastResponseMethod=3
    Manual=4
    

class ACRSpatialResolution(HazenTask):
    """Spatial resolution measurement class for DICOM images of the ACR phantom

    Inherits from HazenTask class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ACR_obj = ACRObject(self.dcm_list,kwargs)
        self.ResOption = ResOptions.MTFMethod
    
    def GetROICrops(self):
        ResSquare,CropsLoc,ROIS = self.GetResSquares(self.ACR_obj.dcms[0])
        ROI_Plots= {
            "1.1mm holes": ROIS[0],
            "1.0mm holes": ROIS[1],
            "0.9mm holes": ROIS[2],
            "0.8mm holes": ROIS[3]
        }
        return ROI_Plots

    def run(self) -> dict:
        """Main function for performing spatial resolution measurement
        using slice 1 from the ACR phantom image set

        Returns:
            dict: results are returned in a standardised dictionary structure specifying the task name, input DICOM Series Description + SeriesNumber + InstanceNumber, task measurement key-value pairs, optionally path to the generated images for visualisation
        """
        rot_ang = self.ACR_obj.rot_angle
        if np.abs(rot_ang) < 3:
            logger.warning(
                f"The estimated rotation angle of the ACR phantom is {np.round(rot_ang, 3)} degrees, which "
                f"is less than the recommended 3 degrees. Results will be unreliable!"
            )

        # Identify relevant slices
        mtf_dcm = self.ACR_obj.dcms[0]

        # Initialise results dictionary
        results = self.init_result_dict()
        results["file"] = self.img_desc(mtf_dcm)

        try:
            if (self.ResOption==ResOptions.DotMatrixMethod):
                res = self.get_dotpairs(mtf_dcm)
                results["measurement"] = {
                    "1.1mm holes": res[0],
                    "1.0mm holes": res[1],
                    "0.9mm holes": res[2],
                    "0.8mm holes": res[3],
                }
            elif(self.ResOption==ResOptions.MTFMethod):
                raw_res, fitted_res = self.get_mtf50(mtf_dcm)
                results["measurement"] = {
                    "estimated rotation angle": round(rot_ang, 2),
                    "raw mtf50": round(raw_res, 2),
                    "fitted mtf50": round(fitted_res, 2),
                }
            elif(self.ResOption==ResOptions.ContrastResponseMethod):
                HorContrastResponse, VertContrastResponse = self.get_ContrastResponse(mtf_dcm)
                sys.exit()
                results["measurement"] = {
                    "1.1mm holes Horizontal": round(HorContrastResponse[0],2),
                    "1.1mm holes Vertical": round(VertContrastResponse[0],2),
                    "1.0mm holes Horizontal": round(HorContrastResponse[1],2),
                    "1.0mm holes Vertical": round(VertContrastResponse[1],2),
                    "0.9mm holes Horizontal": round(HorContrastResponse[2],2),
                    "0.9mm holes Vertical": round(VertContrastResponse[2],2),
                    "0.8mm holes Horizontal": round(HorContrastResponse[3],2),
                    "0.8mm holes Vertical": round(VertContrastResponse[3],2)
                }
                
            elif(self.ResOption==ResOptions.Manual):
                pass
            else:
                raise Exception("Unexpected option in spatial res module.")

        except Exception as e:
            print(
                f"Could not calculate the spatial resolution for {self.img_desc(mtf_dcm)} because of : {e}"
            )
            traceback.print_exc(file=sys.stdout)
            raise Exception(e)

        # only return reports if requested
        if self.report:
            results["report_image"] = self.report_files

        return results

    def y_position_for_ramp(self, res, img, cxy):
        """Identify the y coordinate of the ramp

        Args:
            res (int or float): dcm.PixelSpacing
            img (np.ndarray): dcm.pixelarray
            cxy (tuple): x,y coordinates of the object centre

        Returns:
            float: y coordinate of the ramp min
        """
        investigate_region = int(np.ceil(5.5 / res[1]).item())

        if np.mod(investigate_region, 2) == 0:
            investigate_region = investigate_region + 1

        line_profile_y = skimage.measure.profile_line(
            img,
            (cxy[1] - 2 * investigate_region, cxy[0]),
            (cxy[1] + 2 * investigate_region, cxy[1]),
            mode="constant",
        ).flatten()

        abs_diff_y_profile = np.absolute(np.diff(line_profile_y))
        y_peaks = scipy.signal.find_peaks(abs_diff_y_profile, height=1)
        pk_heights = y_peaks[1]["peak_heights"]
        pk_ind = y_peaks[0]
        highest_y_peaks = pk_ind[(-pk_heights).argsort()[:2]]
        y_locs = highest_y_peaks - 1

        height_pts = cxy[1] - 2 * investigate_region - 1 + y_locs

        y = np.min(height_pts) + 2

        return y

    def crop_image(self, img, x, y, width):
        """Return a rectangular subset of a pixel array

        Args:
            img (np.ndarray): dcm.pixelarray
            x (int): x coordinate of centre
            y (int): y coordinate of centre
            width (int): size of the array top subset

        Returns:
            np.ndarray: subset of a pixel array with given width
        """
        crop_x, crop_y = (x - width // 2, x + width // 2), (
            y - width // 2,
            y + width // 2,
        )
        crop_img = img[crop_y[0] : crop_y[1], crop_x[0] : crop_x[1]]

        return crop_img

    def get_edge_type(self, crop_img):
        """Determine direction of ramp edge

        Args:
            crop_img (np.ndarray): cropped pixel array ~ subset of the image

        Returns:
            tuple of string: vertical/horizontal and up/down or left/rigtward
        """
        edge_sum_rows = np.sum(crop_img, axis=1).astype(np.int_)
        edge_sum_cols = np.sum(crop_img, axis=0).astype(np.int_)

        _, pk_rows_height = self.ACR_obj.find_n_highest_peaks(
            np.abs(np.diff(edge_sum_rows)), 1
        )
        _, pk_cols_height = self.ACR_obj.find_n_highest_peaks(
            np.abs(np.diff(edge_sum_cols)), 1
        )

        edge_type = "vertical" if pk_rows_height > pk_cols_height else "horizontal"

        thresh_roi_crop = crop_img > 0.6 * np.max(crop_img)
        edge_dir = (
            np.sum(thresh_roi_crop, axis=0)
            if edge_type == "vertical"
            else np.sum(thresh_roi_crop, axis=1)
        )
        if edge_type == "vertical":
            direction = "downward" if edge_dir[-1] > edge_dir[0] else "upward"
        else:
            direction = "leftward" if edge_dir[-1] > edge_dir[0] else "rightward"

        return edge_type, direction

    def edge_location_for_plot(self, crop_img, edge_type):
        """Determine the location of the edge so it can be visualised

        Args:
            crop_img (np.array): cropped pixel array ~ subset of the image
            edge_type (tuple): vertical/horizontal and up/down or left/rigtward

        Returns:
            np.array: mask array for edge location
        """
        thresh_roi_crop = crop_img > 0.6 * np.max(crop_img)

        naive_lsf = (
            np.abs(np.diff(np.sum(thresh_roi_crop, 1))) > 1
            if edge_type == "vertical"
            else np.abs(np.diff(np.sum(thresh_roi_crop, 0)))
        )
        edge_test = np.diff(np.where(naive_lsf == 0))[0]
        edge_begin = np.where(edge_test > 1)
        edge_loc = np.array(
            [edge_begin, edge_begin + edge_test[edge_begin] - 1]
        ).flatten()

        return edge_loc

    def fit_normcdf_surface(self, crop_img, edge_type, direction):
        """Fit normalised CDF? to surface

        Args:
            crop_img (np.array): cropped pixel array ~ subset of the image
            edge_type (string): vertical/horizontal
            direction (string): up/down or left/rigtward

        Returns:
            tuple of floats: slope, surface
        """
        thresh_roi_crop = crop_img > 0.6 * np.max(crop_img)
        temp_x = np.linspace(1, thresh_roi_crop.shape[1], thresh_roi_crop.shape[1])
        temp_y = np.linspace(1, thresh_roi_crop.shape[0], thresh_roi_crop.shape[0])
        x, y = np.meshgrid(temp_x, temp_y)

        bright = max(crop_img[thresh_roi_crop])
        dark = 20 + np.min(crop_img[~thresh_roi_crop])

        def func(x, slope, mu, bright, dark):
            """Maths function

            Args:
                x (_type_): _description_
                slope (_type_): _description_
                mu (_type_): _description_
                bright (_type_): _description_
                dark (_type_): _description_

            Returns:
                _type_: _description_
            """
            norm_cdf = (bright - dark) * scipy.stats.norm.cdf(
                x[0], mu + slope * x[1], 0.5
            ) + dark

            return norm_cdf

        sign = 1 if direction in ("downward", "leftward") else -1
        x_data = (
            np.vstack((sign * x.ravel(), y.ravel()))
            if edge_type == "vertical"
            else np.vstack((sign * y.ravel(), x.ravel()))
        )

        popt, pcov = scipy.optimize.curve_fit(
            func, x_data, crop_img.ravel(), p0=[0, 0, bright, dark], maxfev=1500
        )
        surface = func(x_data, popt[0], popt[1], popt[2], popt[3]).reshape(
            crop_img.shape
        )

        slope = 1 / popt[0] if direction in ("leftward", "upward") else -1 / popt[0]

        return slope, surface

    def sample_erf(self, crop_img, slope, edge_type):
        """_summary_

        Args:
            crop_img (np.array): cropped pixel array ~ subset of the image
            slope (float): value of slope of edge
            edge_type (string): vertical/horizontal

        Returns:
            np.array: _description_
        """
        resamp_factor = 8
        if edge_type == "horizontal":
            resample_crop_img = cv2.resize(
                crop_img, (crop_img.shape[0] * resamp_factor, crop_img.shape[1])
            )
        else:
            resample_crop_img = cv2.resize(
                crop_img, (crop_img.shape[0], crop_img.shape[1] * resamp_factor)
            )

        mid_loc = [i / 2 for i in resample_crop_img.shape]

        temp_x = np.linspace(1, resample_crop_img.shape[1], resample_crop_img.shape[1])
        temp_y = np.linspace(1, resample_crop_img.shape[0], resample_crop_img.shape[0])
        x_resample, y_resample = np.meshgrid(temp_x, temp_y)

        erf = []
        n_inside_roi = []
        if edge_type == "horizontal":
            diffY = (y_resample - 1) - mid_loc[0]
            x_prime = x_resample + resamp_factor * diffY * slope

            x_min, x_max = np.min(x_prime).astype(int), np.max(x_prime).astype(int)

            for k in range(x_min, x_max):
                erf_val = np.mean(resample_crop_img[(x_prime >= k) & (x_prime < k + 1)])
                erf.append(erf_val)
                number_nonzero = np.count_nonzero(
                    resample_crop_img[(x_prime >= k) & (x_prime < k + 1)]
                )
                n_inside_roi.append(number_nonzero)
        else:
            diffX = (x_resample.shape[0] - 1) - x_resample - mid_loc[1]
            y_prime = np.flipud(y_resample) + resamp_factor * diffX * slope

            y_min, y_max = np.min(y_prime).astype(int), np.max(y_prime).astype(int)

            for k in range(y_min, y_max):
                erf_val = np.mean(resample_crop_img[(y_prime >= k) & (y_prime < k + 1)])
                erf.append(erf_val)
                number_nonzero = np.count_nonzero(
                    resample_crop_img[(y_prime >= k) & (y_prime < k + 1)]
                )
                n_inside_roi.append(number_nonzero)

        erf = np.array(erf)
        n_inside_roi = np.array(n_inside_roi)

        erf = erf[n_inside_roi == np.max(n_inside_roi)]

        return erf

    def fit_erf(self, erf):
        """Fit ERF

        Args:
            erf (np.array): _description_

        Returns:
            _type_: _description_
        """
        true_erf = np.diff(erf) > 0.2 * np.max(np.diff(erf))
        turning_points = np.where(true_erf)[0][0], np.where(true_erf)[0][-1]
        weights = 0.5 * np.ones((len(true_erf) + 1))
        weights[turning_points[0] : turning_points[1]] = 1

        def func(x, a, b, c, d, e):
            """Maths function for sigmoid curve equation

            Args:
                x (_type_): _description_
                a (_type_): _description_
                b (_type_): _description_
                c (_type_): _description_
                d (_type_): _description_
                e (_type_): _description_

            Returns:
                _type_: _description_
            """
            sigmoid = a + b / (1 + np.exp(c * (x - d))) ** e

            return sigmoid

        popt, pcov = scipy.optimize.curve_fit(
            func,
            np.arange(1, len(erf) + 1),
            erf,
            sigma=(1 / weights),
            p0=[np.min(erf), np.max(erf), 0, sum(turning_points) / 2, 1],
            maxfev=5000,
        )
        erf_fit = func(
            np.arange(1, len(erf) + 1), popt[0], popt[1], popt[2], popt[3], popt[4]
        )

        return erf_fit

    def calculate_MTF(self, erf, res):
        """Calculate MTF

        Args:
            erf (np.array): array of ?
            res (float): dcm.PixelSpacing

        Returns:
            tuple: freq, lsf, MTF
        """
        lsf = np.diff(erf)
        N = len(lsf)
        n = (
            np.arange(-N / 2, N / 2)
            if N % 2 == 0
            else np.arange(-(N - 1) / 2, (N + 1) / 2)
        )

        resamp_factor = 8
        Fs = 1 / (np.sqrt(np.mean(np.square(res))) * (1 / resamp_factor))
        freq = n * Fs / N
        MTF = np.abs(np.fft.fftshift(np.fft.fft(lsf)))
        MTF = MTF / np.max(MTF)

        zero_freq = np.where(freq == 0)[0][0]
        freq = freq[zero_freq:]
        MTF = MTF[zero_freq:]

        return freq, lsf, MTF

    def identify_MTF50(self, freq, MTF):
        """Calculate effective resolution

        Args:
            freq (float or int): _description_
            MTF (float or int): _description_

        Returns:
            float: _description_
        """
        freq_interp = np.arange(0, 1.005, 0.005)
        MTF_interp = np.interp(
            freq_interp, freq, MTF, left=None, right=None, period=None
        )
        equivalent_linepairs = freq_interp[np.argmin(np.abs(MTF_interp - 0.5))]
        eff_res = 1 / (equivalent_linepairs * 2)

        return eff_res

    def get_mtf50(self, dcm):
        """_summary_

        Args:
            dcm (pydicom.Dataset): DICOM image object

        Returns:
            tuple: _description_
        """
        img = dcm.pixel_array
        res = dcm.PixelSpacing
        cxy = self.ACR_obj.centre

        ramp_x = int(cxy[0])
        ramp_y = self.y_position_for_ramp(res, img, cxy)
        
        width = int(13 * img.shape[0] / 256)
        crop_img = self.crop_image(img, ramp_x, ramp_y, width)
        edge_type, direction = self.get_edge_type(crop_img)
        slope, surface = self.fit_normcdf_surface(crop_img, edge_type, direction)
        erf = self.sample_erf(crop_img, slope, edge_type)
        erf_fit = self.fit_erf(erf)

        freq, lsf_raw, MTF_raw = self.calculate_MTF(erf, res)
        _, lsf_fit, MTF_fit = self.calculate_MTF(erf_fit, res)

        eff_raw_res = self.identify_MTF50(freq, MTF_raw)
        eff_fit_res = self.identify_MTF50(freq, MTF_fit)

        if self.report:
            edge_loc = self.edge_location_for_plot(crop_img, edge_type)
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches

            fig, axes = plt.subplots(5, 1)
            fig.set_size_inches(8, 40)
            fig.tight_layout(pad=4)

            axes[0].imshow(img, interpolation="none")
            rect = patches.Rectangle(
                (ramp_x - width // 2 - 1, ramp_y - width // 2 - 1),
                width,
                width,
                linewidth=1,
                edgecolor="w",
                facecolor="none",
            )
            axes[0].add_patch(rect)
            #axes[0].axis("off")
            axes[0].set_title("Segmented Edge")

            axes[1].imshow(crop_img)
            if edge_type == "vertical":
                axes[1].plot(
                    np.arange(0, width - 1),
                    np.mean(edge_loc) - slope * np.arange(0, width - 1),
                    color="r",
                )
            else:
                axes[1].plot(
                    np.mean(edge_loc) + slope * np.arange(0, width - 1),
                    np.arange(0, width - 1),
                    color="r",
                )
            

        
            axes[1].axis("off")
            axes[1].set_title("Cropped Edge", fontsize=14)

            axes[2].plot(erf, "rx", ms=5, label="Raw Data")
            axes[2].plot(erf_fit, "k", lw=3, label="Fitted Data")
            axes[2].set_ylabel("Signal Intensity")
            axes[2].set_xlabel("Pixel")
            axes[2].grid()
            axes[2].legend(fancybox="true")
            axes[2].set_title("ERF", fontsize=14)

            axes[3].plot(lsf_raw, "rx", ms=5, label="Raw Data")
            axes[3].plot(lsf_fit, "k", lw=3, label="Fitted Data")
            axes[3].set_ylabel(r"$\Delta$" + " Signal Intensity")
            axes[3].set_xlabel("Pixel")
            axes[3].grid()
            axes[3].legend(fancybox="true")
            axes[3].set_title("LSF", fontsize=14)

            axes[4].plot(
                freq,
                MTF_raw,
                "rx",
                ms=8,
                label=f"Raw Data - {round(eff_raw_res, 2)}mm @ 50%",
            )
            axes[4].plot(
                freq,
                MTF_fit,
                "k",
                lw=3,
                label=f"Weighted Sigmoid Fit of ERF - {round(eff_fit_res, 2)}mm @ 50%",
            )
            axes[4].set_xlabel("Spatial Frequency (lp/mm)")
            axes[4].set_ylabel("Modulation Transfer Ratio")
            axes[4].set_xlim([-0.05, 1])
            axes[4].set_ylim([0, 1.05])
            axes[4].grid()
            axes[4].legend(fancybox="true")
            axes[4].set_title("MTF", fontsize=14)

            img_path = os.path.realpath(
                os.path.join(self.report_path, f"{self.img_desc(dcm)}_MTF.png")
            )
            fig.savefig(img_path)
            self.report_files.append(img_path)

        return eff_raw_res, eff_fit_res


    #Function to extract the squares we are interested in
    def GetResSquares(self,dcm):
        PixelArray = dcm.pixel_array
        res = dcm.PixelSpacing
        
        Centre = self.ACR_obj.centre
        radius = self.ACR_obj.radius
        BottomPoint = [Centre[0],Centre[1]+radius]
        leftCorner = [ BottomPoint[0] -int(round(57/res[0],0)),
                       BottomPoint[1] -int(round(26/res[1],0))]

        #Crop the ROI we need
        ROISize = [int(round(114/res[0],0)),int(round(37/res[1],0))]
        Crop = PixelArray[leftCorner[1]-ROISize[1]:leftCorner[1],leftCorner[0]:leftCorner[0]+ROISize[0]]
        Binary_Crop = Crop > np.max(Crop)*0.1

        #This line gets rid of anything touching the border edge, super handy!
        Binary_Crop=skimage.segmentation.clear_border(Binary_Crop)
        #Close any gaps within the footprint
        Binary_Crop=skimage.morphology.binary_closing(Binary_Crop,skimage.morphology.square(3))
        label_image = skimage.morphology.label(Binary_Crop)

        ResSquares=[]
        Xpos=[]
        CropsBB = []
        ROIS=[]

        regions = skimage.measure.regionprops(label_image)
        for region in regions[:]:
            if region.area >= 40:
                minr, minc, maxr, maxc = region.bbox
                #maxr+=1
                #maxc+=1
                #minc-=1
                bx = (minc, maxc, maxc, minc, minc)
                by = (minr, minr, maxr, maxr, minr)
                #[0.976599991322, 0.976599991322]
                plt.plot(bx, by, linewidth=0.5)
                plt.plot([region.centroid[1]],[region.centroid[0]], marker="x",linestyle="")

                ROI = Crop[minr:maxr,minc:maxc]
                ResSquares.append(ROI)
                Xpos.append(region.centroid[1])
                CropsBB.append([minr+leftCorner[1]-ROISize[1], maxr+leftCorner[1]-ROISize[1], minc+leftCorner[0], maxc+leftCorner[0]])
                ROIS.append(ROI)           
        plt.imshow(Crop)
        plt.savefig("test.png", dpi=300)
        plt.close("all")

        #take the 4 most right objects, ignoring anything after that. If the blocks on the left get seperated then this can cause issues which is solved by this appraoch.
        OrderedXpos = sorted(Xpos, reverse=True)
        OrderedXIdx= []
        for x in OrderedXpos:
            OrderedXIdx.append(Xpos.index(x))
        IndexsToRemove = OrderedXIdx[4:]

        for idx in IndexsToRemove:
            ResSquares[idx]=None
            CropsBB[idx]=None
            ROIS[idx]=None

        ResSquares=[x for x in ResSquares if x is not None]
        CropsBB=[x for x in CropsBB if x is not None]
        ROIS=[x for x in ROIS if x is not None]
        
        if (len(ROIS)!=4):
            raise Exception("Error: The number of found resolution square does not equal exactly 4.")

        return ResSquares,CropsBB,ROIS

    def get_dotpairs(self,dcm):
        ResSquare,CropsLoc,ROIS = self.GetResSquares(dcm)
        import matplotlib.pyplot as plt
        plt.imshow(ROIS[0])
        plt.savefig("test.png")


        Results = []
        for square in ResSquare:
            var = round(cv2.Laplacian(square, cv2.CV_64F).var(),2)
            Results.append(var)
        
        if self.report:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches

            img = dcm.pixel_array
            fig, axes = plt.subplots(5, 1)
            fig.set_size_inches(8, 40)
            fig.tight_layout(pad=4)

            axes[0].imshow(img, interpolation="none",vmin=0,vmax=np.max(img))
            axes[0].set_title("Phantom Image")
            colors = ["blue","orange","green","red"]
            Titles = ["1.1 mm holes","1.0 mm holes","0.9 mm holes","0.8 mm holes"]
            for i in range(0,len(CropsLoc)):
                minr = CropsLoc[i][0]
                maxr = CropsLoc[i][1]
                minc = CropsLoc[i][2]
                maxc = CropsLoc[i][3]
                bx = (minc, maxc, maxc, minc, minc)
                by = (minr, minr, maxr, maxr, minr)
                axes[0].plot(bx, by,color=colors[i], linewidth=2.5)

                axes[i+1].imshow(ROIS[i],vmin=0,vmax=np.max(img))
                axes[i+1].set_title(Titles[i] + " Res Score: " + str("{:0.3e}".format(Results[i])))
                for axis in ['top','bottom','left','right']:
                    axes[i+1].spines[axis].set_linewidth(6)
                    axes[i+1].spines[axis].set_color(colors[i])

            img_path = os.path.realpath(
            os.path.join(self.report_path, f"{self.img_desc(dcm)}_DotPairs.png"))
            fig.savefig(img_path)
            self.report_files.append(img_path)

        return Results
    

    def get_ContrastResponse(self,dcm):
        def GetContrastResponseFactor(Lines,PixelSteps,CurrentHole):
            #All this below should be in a fuunction
            if PixelSteps >= 1:
                Peaks, PeakProperties = scipy.signal.find_peaks(Lines,distance=PixelSteps)
                Troughs, TroughsProperties = scipy.signal.find_peaks(-Lines,distance=PixelSteps)
            else:
                Peaks, PeakProperties = scipy.signal.find_peaks(Lines)
                Troughs, TroughsProperties = scipy.signal.find_peaks(-Lines)  

            x_values = np.arange(len(Lines))
            y_interp = scipy.interpolate.interp1d(x_values, Lines)

            PeaksandTroughs = list(Peaks)+list(Troughs)        
            
            def Sin(x, phase):
                return np.sin(2*np.pi*x * 1/(PixelSteps*2) + phase) * np.max(Lines)/2 + np.mean(Lines)
            p0=[0]
            if len(PeaksandTroughs) >0:
                fit = curve_fit(Sin, PeaksandTroughs, Lines[PeaksandTroughs], p0=p0)
            else:
                fit = curve_fit(Sin, x_values, Lines, p0=p0) # if we find no peaks/troughs just go ahead and fit to the whole line 
            x=np.arange(0,xCutoff,0.0001)
            data_fit = Sin(x,*fit[0])

            PreicatedPeaks=[]
            PreicatedTroughs=[]

            i=0
            while(len(PreicatedPeaks)<4):
                Prediction = ((np.pi/2+i*2*np.pi) - fit[0][0] )/(2*np.pi*(1/(PixelSteps*2)))
                if Prediction >=0 and Prediction < max(x_values):
                    PreicatedPeaks.append(Prediction)
                if Prediction > max(x_values):
                    PreicatedPeaks.append(max(x_values))
                i+=1

            i=0
            while(len(PreicatedTroughs)<4):
                Prediction = ((3*np.pi/2+i*2*np.pi) - fit[0][0] )/(2*np.pi*(1/(PixelSteps*2)))
                if Prediction >=0 and Prediction < max(x_values):
                    PreicatedTroughs.append(Prediction)
                if Prediction > max(x_values):
                    PreicatedTroughs.append(max(x_values))
                i+=1

            #Organise the peaks to check for any gaps or false peaks
            PeakOrgArray = [None,None,None,None]
            for peak in Peaks:
                diff = np.abs(np.array(PreicatedPeaks)-peak)
                Idx = np.argmin(diff)
                if PeakOrgArray[Idx]==None:
                    PeakOrgArray[Idx] = peak
                else:
                    if diff[Idx] < PeakOrgArray[Idx]: #If two peaks get slotted into the same region then take the one that best matches the expected position. 
                        PeakOrgArray[Idx] = peak

            FinalPeaks = [None,None,None,None]
            for OrgIdx in range(0,len(PeakOrgArray)):
                if PeakOrgArray[OrgIdx]!=None:
                    FinalPeaks[OrgIdx] = PeakOrgArray[OrgIdx]
                else:
                    print("Warning: Peak number " + str(OrgIdx+1) +" is predicted in hole size " +str(CurrentHole) +" mm")
                    FinalPeaks[OrgIdx] = PreicatedPeaks[OrgIdx]

            #Maybe this should be treated the same way as above but al leave it as it is for now
            TrothOrgArray = [None,None,None]
            for trough in Troughs:
                for I in range(3):
                    if trough >= FinalPeaks[I] and trough < FinalPeaks[I+1]:
                        TrothOrgArray[I] = trough
            
            FinalTroughs=[None,None,None]
            for OrgIdx in range(0,len(FinalTroughs)):
                if TrothOrgArray[OrgIdx]!=None:
                    FinalTroughs[OrgIdx] = TrothOrgArray[OrgIdx]
                else:
                    print("Warning: Trough number " + str(OrgIdx+1) +" is predicted in hole size " +str(CurrentHole) +" mm")
                    FinalTroughs[OrgIdx] = PreicatedTroughs[OrgIdx]

            PeaksTroughsX = []
            PeaksTroughsY=[]
            MeanPeak = 0
            for peak in FinalPeaks:
                MeanPeak+=y_interp(peak)
                PeaksTroughsX.append(peak)
                PeaksTroughsY.append(y_interp(peak))
            MeanPeak/=4

            MeanTrough=0
            for Troughs in FinalTroughs:
                MeanTrough+=y_interp(Troughs)
                PeaksTroughsX.append(Troughs)
                PeaksTroughsY.append(y_interp(Troughs))

            MeanTrough/=3
            Amplitude = MeanPeak-MeanTrough
            return Amplitude/MeanPeak,MeanPeak,MeanTrough,PeaksTroughsX,PeaksTroughsY

        def ExtractLines(Rect,points,values,img):
            Vertical=False
            if Rect.get_width() < Rect.get_height():
                Vertical=True

            StartPoint = list(Rect.get_xy())
            EndPoint = [Rect.get_xy()[0]+Rect.get_width(),Rect.get_xy()[1]+Rect.get_height()]
            IterationAxis = 1 #This is going to determine if we iterate along x or y (horizontal or verticlal lines)
            if Vertical==True:
                IterationAxis=0

            if IterationAxis==1 and StartPoint[IterationAxis] <0:
                StartPoint[IterationAxis]=0
            if IterationAxis==0 and EndPoint[IterationAxis] >=img.shape[1]-1:
                EndPoint[IterationAxis]=img.shape[1]-1

            #The number of samples we do should be equal to the number of pixels, its all the data we have so this makes sense i think?
            NumberOfPixelsInRange = math.ceil(EndPoint[IterationAxis]-StartPoint[IterationAxis]) 

            if Vertical==False:
                xvalues=np.linspace(0,xCutoff,math.ceil(xCutoff),endpoint=True)
                IterRange = np.linspace(StartPoint[IterationAxis],EndPoint[IterationAxis],NumberOfPixelsInRange,endpoint=False)
                Lines=np.zeros(xvalues.shape[0])
            else:
                yvalues=np.linspace(yCutoff,img.shape[0]-1,math.ceil(img.shape[0]-yCutoff-1),endpoint=True)
                IterRange = np.linspace(EndPoint[IterationAxis],StartPoint[IterationAxis],NumberOfPixelsInRange,endpoint=False)
                Lines=np.zeros(yvalues.shape[0])
            ##Checking iterRang and x range are right
            for IterValue in IterRange:
                if Vertical==False:
                    yvalues=[IterValue]*len(xvalues)
                else:
                    xvalues=[IterValue]*len(yvalues)
                Line = griddata(points, values, (yvalues, xvalues), method='linear')
                Lines += Line
            return Lines

        def GetCutOffs(img):
            
            import matplotlib
            matplotlib.use('TkAgg')
            Thresh = 0
            for i in range(img.shape[1]):
                Thresh+=np.mean(img[i,:])
            Thresh /= img.shape[1]


            GapplessROI = img>=Thresh
            #fig, ax = plt.subplots(nrows=1, ncols=1)
            plt.imshow(img)
            plt.imshow(GapplessROI,alpha=0.5)
            plt.show()
            num = 0
            count =0
            while num != 3:
                GapplessROI=skimage.morphology.binary_dilation(GapplessROI)
                label_image,num = skimage.morphology.label(GapplessROI+1,return_num=True,connectivity=2)
                count+=1
                print(num)
                #fig, ax = plt.subplots(nrows=1, ncols=1)
                plt.imshow(img)
                plt.imshow(GapplessROI,alpha=0.5)
                plt.show()

            for i in range(0,count):
                GapplessROI=skimage.morphology.binary_erosion(GapplessROI)
                fig, ax = plt.subplots(nrows=1, ncols=1)
                #fig, ax = plt.subplots(nrows=1, ncols=1)
                plt.imshow(img)
                plt.imshow(GapplessROI,alpha=0.5)
                plt.show()

            #fig, ax = plt.subplots(nrows=1, ncols=1)
            plt.imshow(img)
            plt.imshow(GapplessROI,alpha=0.5)
            plt.show()

            

            return 0,0

        Crops = self.GetROICrops()
        imgs = [Crops["1.1mm holes"],Crops["1.0mm holes"],Crops["0.9mm holes"],Crops["0.8mm holes"]]
        HoleSize = [1.1,1.0,0.9,0.8]

        if self.report:
            fig = plt.figure(figsize=(15, 10))
            gs = gridspec.GridSpec(nrows=4, ncols=4,height_ratios=[3, 1,1,1])
            gridspec_kw={'width_ratios': [1, 3]}


        ContrastResponsesHorAllRes=[]
        ContrastResponsesVertAllRes=[]
        ProcessedSizes=[]

        LineTest=[]

        for I in range(0,1):
            img = imgs[I]
            
            PixelSteps = HoleSize[I]/self.ACR_obj.pixel_spacing[0]
            StepSize = PixelSteps
            colors = ['r','g','b','y']
            ProcessedSizes.append(HoleSize[I])

            yCutoff = None
            xCutoff = None

            y= -PixelSteps*0.5
            x = img.shape[0]-PixelSteps*1.5



            xCutoff,yCutoff = GetCutOffs(img)

            yCutoff = y + (PixelSteps*2)*3
            xCutoff = (x- PixelSteps*6) + (PixelSteps*2)


            if self.report:
                ax0 = fig.add_subplot(gs[0, I])
                ax0.imshow(img)
                ax0.set_title("Hole Size: " + str(HoleSize[I])+" mm")
            
            MiddlesHor = []
            MiddlesVert= []

            y = -PixelSteps*0.5
            x = img.shape[0]-PixelSteps*1.5

            AllLinesAndResultsHor = []
            ContrastResponseResultsHor = []
            AllLinesAndResultsVert = []
            ContrastResponseResultsVert = []

            points=[]
            values=[]
            #Set up Interpolation, im sure there is a far better way of doing this in a more python way...
            for X in range(img.shape[1]):
                for Y in range(img.shape[0]):
                    points.append([Y,X])
                    values.append(img[Y,X])

            for i in range(4):
                rect = patches.Rectangle((0, y), xCutoff, PixelSteps*2, linewidth=1, edgecolor=colors[i], facecolor='none', linestyle="-")
                MiddlesHor.append( (y+(y+PixelSteps*2.0))/2.0)
                if self.report:
                    ax0.add_patch(rect)
                
                Lines = ExtractLines(rect,points,values,img)
                LineTest.append(Lines)
                y += PixelSteps*2

                AllLinesAndResultsHor.append([Lines,None,None,None,None])
                ContrastResponseResultsHor.append(None)
                ContrastResponseResultsHor[-1], AllLinesAndResultsHor[-1][1], AllLinesAndResultsHor[-1][2], AllLinesAndResultsHor[-1][3], AllLinesAndResultsHor[-1][4] = GetContrastResponseFactor(Lines,PixelSteps,HoleSize[I])
                
                rect = patches.Rectangle((x, yCutoff), PixelSteps*2, img.shape[0]-1-yCutoff, linewidth=1, edgecolor=colors[i], facecolor='none', linestyle="--")
                MiddlesVert.append( (x+(x+PixelSteps*2.0))/2.0)
                if self.report:
                    ax0.add_patch(rect)
                x -= PixelSteps*2

                Lines = ExtractLines(rect,points,values,img)
                AllLinesAndResultsVert.append([Lines,None,None,None,None])
                ContrastResponseResultsVert.append(None)
                ContrastResponseResultsVert[-1], AllLinesAndResultsVert[-1][1], AllLinesAndResultsVert[-1][2], AllLinesAndResultsVert[-1][3], AllLinesAndResultsVert[-1][4] = GetContrastResponseFactor(Lines,PixelSteps,HoleSize[I])

            BestHorIndex=ContrastResponseResultsHor.index(max(ContrastResponseResultsHor))
            BestVertIndex=ContrastResponseResultsVert.index(max(ContrastResponseResultsVert))
            
            if self.report:
                ax_hor = fig.add_subplot(gs[1, I])
                ax_hor.plot(AllLinesAndResultsHor[BestHorIndex][0],color="g",linestyle="-")
                ax_hor.axhline(y=AllLinesAndResultsHor[BestHorIndex][1], color='r', linestyle='-')
                ax_hor.axhline(y=AllLinesAndResultsHor[BestHorIndex][2], color='b', linestyle='-')
                ax_hor.plot(AllLinesAndResultsHor[BestHorIndex][3],AllLinesAndResultsHor[BestHorIndex][4],marker="x", color="orange",linestyle="")
                #ax_hor.get_yaxis().set_visible(False)
                #ax0.plot([0,xCutoff],[MiddlesHor[BestHorIndex],MiddlesHor[BestHorIndex]],linestyle = "-",color="g")

                ax_vert = fig.add_subplot(gs[2, I])
                ax_vert.plot(AllLinesAndResultsVert[BestVertIndex][0],color="g",linestyle="--")
                ax_vert.axhline(y=AllLinesAndResultsVert[BestVertIndex][1], color='r', linestyle='-')
                ax_vert.axhline(y=AllLinesAndResultsVert[BestVertIndex][2], color='b', linestyle='-')
                ax_vert.plot(AllLinesAndResultsVert[BestVertIndex][3],AllLinesAndResultsVert[BestVertIndex][4],marker="x", color="orange",linestyle="")
                #ax_vert.get_yaxis().set_visible(False)
                #ax0.plot([MiddlesVert[BestVertIndex],MiddlesVert[BestVertIndex]],[yCutoff,len(img)-1],linestyle = "--",color="g")

                ContrastResponsesHorAllRes.append(max(ContrastResponseResultsHor))
                ContrastResponsesVertAllRes.append(max(ContrastResponseResultsVert))


        if self.report:
            AxOverall = fig.add_subplot(gs[3,:])
            AxOverall.plot(ProcessedSizes,ContrastResponsesHorAllRes,marker="x",linestyle="-",label="Horizontal Contrast Response")
            AxOverall.plot(ProcessedSizes,ContrastResponsesVertAllRes,marker="x",linestyle="-",label="Vertical Contrast Response")
            AxOverall.set_xlim(1.2,0.7)
            AxOverall.legend()
            AxOverall.set_ylabel("Contrast Response")
            AxOverall.set_xlabel("Resolution")
            img_path = os.path.realpath(
            os.path.join(self.report_path, f"{self.img_desc(dcm)}_ContrastResponse.png"))
            plt.savefig(img_path)
            self.report_files.append(img_path)

        return ContrastResponsesHorAllRes,ContrastResponsesVertAllRes