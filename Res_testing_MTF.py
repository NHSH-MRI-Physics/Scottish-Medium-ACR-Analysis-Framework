from hazenlib.ACRObject import ACRObject
import glob
from hazenlib.utils import get_dicom_files
import pydicom
from matplotlib import pyplot as plt
from skimage.measure import profile_line
import numpy as np

dcm_list = []

def rotate_points(points, center, angle_degrees):
    """
    Rotates a list of points around a center point by a given angle.
    
    :param points: List or array of two points, e.g., [(x1, y1), (x2, y2)]
    :param center: Tuple or array of the center point (cx, cy)
    :param angle_degrees: Angle of rotation in degrees
    :return: NumPy array of the rotated points
    """
    # Convert angle to radians
    theta = np.radians(angle_degrees)
    
    # Create the 2D rotation matrix
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[c, -s], 
                  [s,  c]])
    
    center = np.array(center)
    rotated_points = []
    
    for p in points:
        p = np.array(p)
        # 1. Shift to origin, 2. Rotate, 3. Shift back
        rotated = R.dot(p - center) + center
        rotated_points.append(rotated)
        
    return np.array(rotated_points)

def ComputeRes(fileLoc):
    files = get_dicom_files(fileLoc)
    for file in files:
        dcm_list.append(pydicom.dcmread(file))

    ACRObj = ACRObject(dcm_list,kwargs={'MediumACRPhantom': True})
    Image = ACRObj.images[6]
    Mask = ACRObj.mask_image

    LineLen = len(Image[0])

    start_point = (ACRObj.centre[1], 0)   # (y1, x1)
    end_point = (ACRObj.centre[1],LineLen)  # (y2, x2)

    RotatedPoints = rotate_points([start_point, end_point], ACRObj.centre, 45)

    plt.imshow(Mask, cmap='gray')
    plt.plot(ACRObj.centre[0], ACRObj.centre[1], 'r+')
    plt.plot([start_point[1], end_point[1]], [start_point[0], end_point[0]], 'x', lw=2,color='green')
    plt.plot([start_point[1], end_point[1]], [start_point[0], end_point[0]], 'x', lw=2,color='green')
    plt.colorbar()
    plt.savefig("Image.png")
    plt.close()


    '''
    profile = profile_line(Image, start_point, end_point, linewidth=3)
    profile = np.clip(profile, a_min=None, a_max=1600)

    plt.plot(profile)
    plt.savefig("Profile.png")
    plt.close()

    lsf = np.diff(profile)
    plt.plot(lsf)
    plt.savefig("LSF.png")
    plt.close()

    window = np.hamming(len(lsf))
    lsf_windowed = lsf * window
    plt.plot(lsf_windowed)
    plt.savefig("LSF_Windowed.png")

    # 4. Compute the Fast Fourier Transform (FFT) and take the magnitude
    fft_vals = np.fft.fft(lsf_windowed, n=512) # Zero-padding for smooth curve
    mtf = np.abs(fft_vals)

    # 5. Normalize so the DC component (zero frequency) is 1.0
    mtf = mtf / mtf[0]

    # Keep only the positive frequencies (first half)
    frequencies = np.fft.fftfreq(512)[:256]
    mtf_positive = mtf[:256]
    mtf_Perfect = np.ones(256)

    # Plotting the MTF
    plt.figure(figsize=(6, 4))
    plt.plot(frequencies, mtf_positive, color='blue', lw=2)
    plt.title("Modulation Transfer Function (MTF)")
    plt.xlabel("Spatial Frequency (cycles/pixel)")
    plt.ylabel("MTF (Response)")
    plt.grid(True)
    plt.ylim(0, 1.05)
    plt.savefig("MTF.png")

    integral_area = np.trapz(mtf_positive, frequencies)

    PerfectIntegral =  np.trapz(mtf_Perfect, frequencies)

    print(integral_area/PerfectIntegral)
    '''




fileLoc = "MedACRTestingSetAndResults\\Blair Gartnavel"
ComputeRes(fileLoc)