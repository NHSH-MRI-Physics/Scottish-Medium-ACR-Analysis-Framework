import numpy as np
import matplotlib.pyplot as plt
import os, glob
import pydicom
import pylab as pl
import sys
import matplotlib.path as mplPath
from tkinter import filedialog as fd
#from Index_Tracker import IndexTracker
sys.path.insert(0,"F:\Medical Physics\DMP\RPIP\Imaging\MRI\QA\Hazen-MediumACRPhantom")
from hazenlib.utils import get_dicom_files
from hazenlib.utils import get_manufacturer
from hazenlib.utils import get_image_orientation
from hazenlib.ACRObject import ACRObject

#Prompt for DICOM dir:
folder_sel = fd.askdirectory()
files = get_dicom_files(folder_sel,sort=True)
#filenamemask="\\*.dcm"
filenamemask="\\I*"
fullmask=folder_sel+filenamemask
fullmaskFormatted=fullmask.replace('/','\\')
print(f'Fullmask = {fullmaskFormatted}')


class IndexTracker(object):
    def __init__(self, ax, X):
        self.ax = ax
        ax.set_title('Scroll to Navigate through the DICOM Image Slices')

        self.X = X
        rows, cols, self.slices = X.shape
        self.ind = self.slices//2

        self.im = ax.imshow(self.X[:, :, self.ind])
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.ind])
        ax.set_ylabel('Slice Number: %s' % self.ind)
        self.im.axes.figure.canvas.draw()

fig, ax = plt.subplots(1,1)

#os.system("tree H:\MRI")

plots = []

'''for f in glob.glob(fullmaskFormatted):
#    print(f'file is {f}')
    pass
    filename = f.split("/")[-1]
    print(f'Plot filename is {filename}')
    ds = pydicom.dcmread(filename)
    pix = ds.pixel_array
    pix = pix*1+(-1024)
    plots.append(pix)
'''

ACRDICOMSFiles = {}
for file in files:
    data = pydicom.dcmread(file)
    print(f'ACR filename is {file}')
    if (data.SeriesDescription not in ACRDICOMSFiles.keys()):
        ACRDICOMSFiles[data.SeriesDescription]=[]
    ACRDICOMSFiles[data.SeriesDescription].append(file)
    ChosenData = ACRDICOMSFiles[data.SeriesDescription]

print(f'ChosenData= {ChosenData}')
dcm_list = [pydicom.dcmread(dicom) for dicom in ChosenData]
#print(f'dcm_list is {dcm_list}')
img_stack = [dicom.pixel_array for dicom in dcm_list]
#img_stack.reverse()
#img_stack.append(img_stack.pop(0))

vendor=get_manufacturer(dcm_list[2])
print(f'Vendor is {vendor}')
orientation=get_image_orientation(dcm_list[2])
print(f'Orientation is {orientation}')

#print(dcm_list[3])

y = np.dstack(img_stack)
tracker = IndexTracker(ax,y)

fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
plt.show()

#for i in range(11):
plt.imshow(img_stack[6], cmap=plt.cm.bone)  # set the color map to bone 
plt.show()