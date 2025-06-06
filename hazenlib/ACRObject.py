import cv2
import scipy
import scipy.version
import skimage
import numpy as np
from pydicom import dcmread
import sys
import matplotlib.pyplot as plt 
from hazenlib.utils import get_image_orientation
from pydicom.pixel_data_handlers.util import apply_modality_lut
import os 


class ACRObject:
    def __init__(self, dcm_list,kwargs={}):
        
        #Added in a medium ACR phantom flag, not sure if this is the best way of doing this but will leave it for now..
        self.MediumACRPhantom = False
        if "MediumACRPhantom" in kwargs.keys():
            self.MediumACRPhantom = kwargs["MediumACRPhantom"]

        import MedACROptions
        self.ParamaterOverrideHolder=MedACROptions.ParamaterOveride()
        if "Paramater_overide" in kwargs.keys():
            self.ParamaterOverrideHolder = kwargs["Paramater_overide"]
            
        #Added in a flag to make use of the dot matrix instead of MTF for spatial res
        #self.UseDotMatrix=False
        #if "UseDotMatrix" in kwargs.keys():
        #    self.UseDotMatrix =kwargs["UseDotMatrix"]

        # Initialise an ACR object from a stack of images of the ACR phantom
        self.dcm_list = dcm_list
        # Load files as DICOM and their pixel arrays into 'images'
        self.images, self.dcms = self.sort_images()
        # Store the pixel spacing value from the first image (expected to be the same for all)

        if 'PixelSpacing' in self.dcms[0]:
            self.pixel_spacing = self.dcms[0].PixelSpacing
        else:
            for elem in self.dcms[0].iterall():
                if elem.tag == (0x28,0x30):
                    self.pixel_spacing = elem.value
        
        # Check whether images of the phantom are the correct orientation
        self.orientation_checks()
        # Determine whether image rotation is necessary
        self.rot_angle = self.determine_rotation()
        # Store the DCM object of slice 7 as it is used often
        self.slice7_dcm = self.dcms[6]
        # Find the centre coordinates of the phantom (circle)
        if self.ParamaterOverrideHolder.CentreOverride != None and self.ParamaterOverrideHolder.RadiusOverride != None:
            self.centre = self.ParamaterOverrideHolder.CentreOverride
            self.radius = self.ParamaterOverrideHolder.RadiusOverride
        else:
            self.centre, self.radius = self.find_phantom_center()
            
        # Store a mask image of slice 7 for reusability
        if self.ParamaterOverrideHolder.MaskingOverride[6].any() != None:
            self.mask_image = self.ParamaterOverrideHolder.MaskingOverride[6]
        else:
            self.mask_image = self.get_mask_image(self.images[6])

        if "Localiser" in kwargs.keys():
            self.LocalisierDCM=dcmread(kwargs["Localiser"])
        else:
            self.LocalisierDCM = None

        for i in range(0,len(self.ParamaterOverrideHolder.MaskingOverride)):
            if self.ParamaterOverrideHolder.MaskingOverride[i].any() != None:
                if self.ParamaterOverrideHolder.MaskingOverride[i][self.centre[1],self.centre[0]] == 0:
                    raise Exception("Radius not within the mask in slice " + str(i+1))

        self.kwargs = kwargs
        

    def sort_images(self):
        """
        Sort a stack of images based on slice position.

        Returns
        -------
        img_stack : np.array
            A sorted stack of images, where each image is represented as a 2D numpy array.
        dcm_stack : pyd
            A sorted stack of dicoms
        """

        if "ImageOrientationPatient" in self.dcm_list[0]:
            ImageOrientationPatient = self.dcm_list[0].ImageOrientationPatient
        else:
            for elem in self.dcm_list[0].iterall():
                if elem.tag == (0x20,0x37):
                    ImageOrientationPatient = elem.value
        
        #orientation=get_image_orientation(self.dcm_list[0].ImageOrientationPatient)
        orientation=get_image_orientation(ImageOrientationPatient)
        
        if "ImagePositionPatient" in self.dcm_list[0]:
            x = np.array([dcm.ImagePositionPatient[0] for dcm in self.dcm_list])
            y = np.array([dcm.ImagePositionPatient[1] for dcm in self.dcm_list])
            z = np.array([dcm.ImagePositionPatient[2] for dcm in self.dcm_list])
            if orientation=='Transverse':
                dicom_stack = [self.dcm_list[i] for i in np.argsort(z)]
            elif orientation=='Coronal':
                dicom_stack = [self.dcm_list[i] for i in np.argsort(y)]
            elif orientation=='Sagittal':
                dicom_stack = [self.dcm_list[i] for i in np.argsort(x)]
        else:
            print("WARNING: Incompatible or missing image position patient tag, ordering based on filenames, this may lead to incompatible data structures!")
            files = []
            for dcm in self.dcm_list:
                files.append(os.path.basename(dcm.filename))
            files.sort()

            dicom_stack=[]
            for i in range(len(files)):
                for dcm in self.dcm_list:
                    if os.path.basename(dcm.filename) == files[i]:
                        dicom_stack.append(dcm)

        img_stack = [dicom.pixel_array for dicom in dicom_stack]
        img_stack = [apply_modality_lut(dicom.pixel_array,dicom).astype('uint16') for dicom in dicom_stack]
        return img_stack, dicom_stack

    def orientation_checks(self):
        """
        Perform orientation checks on a set of images to determine if slice order inversion or an
        LR orientation swap is required.

        Description
        -----------
        This function analyzes the given set of images and their associated DICOM objects to determine if any
        adjustments are needed to restore the correct slice order and view orientation.
        """
        test_images = (self.images[0], self.images[-1])
        dx = self.pixel_spacing[0]

        normalised_images = [
            cv2.normalize(
                src=image,
                dst=None,
                alpha=0,
                beta=255,
                norm_type=cv2.NORM_MINMAX,
                dtype=cv2.CV_8U,
            )
            for image in test_images
        ]

        # search for circle in first slice of ACR phantom dataset with radius of ~11mm
        detected_circles = [
            cv2.HoughCircles(
                norm_image,
                cv2.HOUGH_GRADIENT,
                1,
                param1=50,
                param2=30,
                minDist=int(180 / dx),
                minRadius=int(15 / dx),
                maxRadius=int(20 / dx),
            )
            for norm_image in normalised_images
        ]

        if detected_circles[0] is not None:
            true_circle = detected_circles[0].flatten()
        else:
            true_circle = detected_circles[1].flatten() 
                

        if detected_circles[0] is None and detected_circles[1] is not None:
            print("Performing slice order inversion to restore correct slice order.")
            self.images.reverse()
            self.dcms.reverse()
        else:
            print("Slice order inversion not required.")

        if true_circle[0] > self.images[0].shape[0] // 2:
            print("Performing LR orientation swap to restore correct view.")
            flipped_images = [np.fliplr(image) for image in self.images]
            for index, dcm in enumerate(self.dcms):
                dcm.PixelData = flipped_images[index].tobytes()
        else:
            print("LR orientation swap not required.")

    def determine_rotation(self):
        """
        Determine the rotation angle of the phantom using edge detection and the Hough transform.

        Returns
        ------
        rot_angle : float
            The rotation angle in degrees.
        """

        thresh = cv2.threshold(self.images[0], 127, 255, cv2.THRESH_BINARY)[1]
        if (self.MediumACRPhantom==True): #the above thresh doesnt work for the med phantom (not sure why but maybe it shouldnt be a flat thresh anyway...)
            thresh = cv2.threshold(self.images[0], np.max(self.images[0])*0.25, 255, cv2.THRESH_BINARY)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilate = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
        diff = cv2.absdiff(dilate, thresh)

        h, theta, d = skimage.transform.hough_line(diff)
        _, angles, _ = skimage.transform.hough_line_peaks(h, theta, d)

        
        from packaging.version import Version
        if Version(str(scipy.version.version)) == Version('1.10.0'):
            angle = np.rad2deg(scipy.stats.mode(angles)[0][0]) #This needs as specific version of scipy or you get an error (drop the last [0])
        elif Version(str(scipy.version.version)) >= Version('1.11.0'): 
            angle = np.rad2deg(scipy.stats.mode(angles)[0])
        else:
            raise ModuleNotFoundError("This version of scipy is not supported, please use 1.10.0 or >= 1.11.0")

        rot_angle = angle + 90 if angle < 0 else angle - 90
        return rot_angle

    def rotate_images(self):
        """
        Rotate the images by a specified angle. The value range and dimensions of the image are preserved.

        Returns
        -------
        np.array:
            The rotated images.
        """

        return skimage.transform.rotate(
            self.images, self.rot_angle, resize=False, preserve_range=True
        )

    def find_phantom_center(self):
        """
        Find the center of the ACR phantom by filtering the uniformity slice and using the Hough circle detector.


        Returns
        -------
        centre  : tuple
            Tuple of ints representing the (x, y) center of the image.
        """
        img = self.images[6]
        dx, dy = self.pixel_spacing
        img_blur = cv2.GaussianBlur(img, (1, 1), 0)
        img_grad = cv2.Sobel(img_blur, 0, dx=1, dy=1)

        if (self.MediumACRPhantom==False):
            img_blur = cv2.GaussianBlur(img, (1, 1), 0)
            img_grad = cv2.Sobel(img_blur, 0, dx=1, dy=1)
            detected_circles = cv2.HoughCircles(
                img_grad,
                cv2.HOUGH_GRADIENT,
                1,
                param1=50,
                param2=30,
                minDist=int(180 / dy),
                minRadius=int(180 / (2 * dy)),
                maxRadius=int(200 / (2 * dx)),
            ).flatten()

            #This prob should be rounding like it is below but i kept it this way so the unit tests all work.
            centre = [int(i) for i in detected_circles[:2]]
            radius = int(detected_circles[2])

        else: 
            values = img[img > np.mean(img)*0.1] 
            image = img > np.median(values)*0.5
            from skimage import io, color, measure, draw, img_as_bool
            from scipy import optimize
            def cost(params):
                x0, y0, r = params
                coords = draw.disk((y0, x0), r, shape=image.shape)
                template = np.zeros_like(image)
                template[coords] = 1
                return -np.sum(template == image)
            test = image.shape
            x0, y0, r = optimize.fmin(cost, (int(image.shape[0]/2), int(image.shape[1]/2), 165 / (2 * dx)))
            detected_circles= [x0,y0,r]
            centre = [int(round(i)) for i in detected_circles[:2]] # This is better as round than just int otherwise its always rounding down.
            radius = int(round(detected_circles[2]))
            
            
        return centre, radius

    def get_mask_image_from_slice(self,SliceNum, mag_threshold=0.05, open_threshold=500):
        if self.ParamaterOverrideHolder.MaskingOverride[SliceNum].any() != None:
            return self.ParamaterOverrideHolder.MaskingOverride[SliceNum]
        else:
            return self.get_mask_image(self.images[SliceNum],mag_threshold=mag_threshold, open_threshold=open_threshold)

    def get_mask_image(self, image, mag_threshold=0.05, open_threshold=500):
        """Create a masked pixel array
        Mask an image by magnitude threshold before applying morphological opening to remove small unconnected
        features. The convex hull is calculated in order to accommodate for potential air bubbles.

        Args:
            image (_type_): _description_
            mag_threshold (float, optional): magnitude threshold. Defaults to 0.05.
            open_threshold (int, optional): open threshold. Defaults to 500.

        Returns:
            np.array:
                The masked image.
        """
        test_mask = self.circular_mask(
            self.centre, (80 // self.pixel_spacing[0]), image.shape
        )
        test_image = image * test_mask
        test_vals = test_image[np.nonzero(test_image)]
        if np.percentile(test_vals, 80) - np.percentile(test_vals, 10) > 0.9 * np.max(
            image
        ):
            print(
                "Large intensity variations detected in image. Using local thresholding!"
            )
            initial_mask = skimage.filters.threshold_sauvola(
                image, window_size=3, k=0.95
            )
        else:
            initial_mask = image > mag_threshold * np.max(image)

        opened_mask = skimage.morphology.area_opening(
            initial_mask, area_threshold=open_threshold
        )
        final_mask = skimage.morphology.convex_hull_image(opened_mask)

        return final_mask

    @staticmethod
    def circular_mask(centre, radius, dims):
        """
        Sort a stack of images based on slice position.

        Parameters
        ----------
        centre : tuple
            The centre coordinates of the circular mask.
        radius : int
            The radius of the circular mask.
        dims   : tuple
            The dimensions of the circular mask.

        Returns
        -------
        img_stack : np.array
            A sorted stack of images, where each image is represented as a 2D numpy array.
        """
        # Define a circular logical mask

        #BugFix, should this not start at 0?
        y = np.linspace(0, dims[0]-1, dims[0])
        x = np.linspace(0, dims[1]-1, dims[1])

        #This is the old code
        #x = np.linspace(1, dims[0], dims[0])
        #y = np.linspace(1, dims[1], dims[1])

        X, Y = np.meshgrid(x, y)
        mask = (X - centre[0]) ** 2 + (Y - centre[1]) ** 2 <= radius**2

        return mask

    def measure_orthogonal_lengths(self, mask):
        """
        Compute the horizontal and vertical lengths of a mask, based on the centroid.

        Parameters:
        ----------
        mask    : ndarray of bool
            Boolean array of the image.

        Returns:
        ----------
        length_dict : dict
            A dictionary containing the following information for both horizontal and vertical line profiles:
            'Horizontal Start'      | 'Vertical Start' : tuple of int
                Horizontal/vertical starting point of the object.
            'Horizontal End'        | 'Vertical End' : tuple of int
                Horizontal/vertical ending point of the object.
            'Horizontal Extent'     | 'Vertical Extent' : ndarray of int
                Indices of the non-zero elements of the horizontal/vertical line profile.
            'Horizontal Distance'   | 'Vertical Distance' : float
                The horizontal/vertical length of the object.
        """
        dims = mask.shape
        dx, dy = self.pixel_spacing

        horizontal_start = (self.centre[1], 0)
        horizontal_end = (self.centre[1], dims[0] - 1)
        horizontal_line_profile = skimage.measure.profile_line(
            mask, horizontal_start, horizontal_end
        )
        horizontal_extent = np.nonzero(horizontal_line_profile)[0]
        horizontal_distance = (horizontal_extent[-1] - horizontal_extent[0]) * dx

        vertical_start = (0, self.centre[0])
        vertical_end = (dims[1] - 1, self.centre[0])
        vertical_line_profile = skimage.measure.profile_line(
            mask, vertical_start, vertical_end
        )
        vertical_extent = np.nonzero(vertical_line_profile)[0]
        vertical_distance = (vertical_extent[-1] - vertical_extent[0]) * dy

        length_dict = {
            "Horizontal Start": horizontal_start,
            "Horizontal End": horizontal_end,
            "Horizontal Extent": horizontal_extent,
            "Horizontal Distance": horizontal_distance,
            "Vertical Start": vertical_start,
            "Vertical End": vertical_end,
            "Vertical Extent": vertical_extent,
            "Vertical Distance": vertical_distance,
        }

        return length_dict

    @staticmethod
    def rotate_point(origin, point, angle):
        """
        Compute the horizontal and vertical lengths of a mask, based on the centroid.

        Parameters:
        ----------
        origin : tuple
            The coordinates of the point around which the rotation is performed.
        point  : tuple
            The coordinates of the point to rotate.
        angle  : int
            Angle in degrees.

        Returns:
        ----------
        x_prime : float
            A float representing the x coordinate of the desired point after being rotated around an origin.
        y_prime : float
            A float representing the y coordinate of the desired point after being rotated around an origin.
        """
        theta = np.radians(angle)
        c, s = np.cos(theta), np.sin(theta)

        x_prime = origin[0] + c * (point[0] - origin[0]) - s * (point[1] - origin[1])
        y_prime = origin[1] + s * (point[0] - origin[0]) + c * (point[1] - origin[1])
        return x_prime, y_prime

    @staticmethod
    def find_n_highest_peaks(data, n, height=1):
        """
        Find the indices and amplitudes of the N highest peaks within a 1D array.

        Parameters:
        ----------
        data    : np.array
            The array containing the data to perform peak extraction on.
        n       : int
            The coordinates of the point to rotate.
        height  : int or float
            The amplitude threshold for peak identification.

        Returns:
        ----------
        peak_locs       : np.array
            A numpy array containing the indices of the N highest peaks identified.
        peak_heights    : np.array
            A numpy array containing the amplitudes of the N highest peaks identified.
        """
        peaks = scipy.signal.find_peaks(data, height)
        pk_heights = peaks[1]["peak_heights"]
        pk_ind = peaks[0]

        peak_heights = pk_heights[
            (-pk_heights).argsort()[:n]
        ]  # find n highest peak amplitudes
        peak_locs = pk_ind[(-pk_heights).argsort()[:n]]  # find n highest peak locations

        return np.sort(peak_locs), np.sort(peak_heights)

    @staticmethod
    def find_Peaks_Within_Thresh(data,thresh,height=1):
        #This is similar to the above function. The above function fails if there is >2 peaks found which can happen with some phantoms.
        #It will return all peaks within a specific threshold of the max peak
        peaks = scipy.signal.find_peaks(data, height)
        pk_heights = peaks[1]["peak_heights"]
        pk_ind = peaks[0]
        
        LowerWindow = np.max(pk_heights)*(1.0-thresh)
        pk_ind = pk_ind[np.where(pk_heights >= LowerWindow)]
        pk_heights = pk_heights[np.where(pk_heights >= LowerWindow)]

        peak_heights = pk_heights[
            (pk_ind).argsort()
        ]  # find n highest peak amplitudes
        peak_locs = pk_ind[(pk_ind).argsort()]
        return np.sort(peak_locs), np.sort(peak_heights)