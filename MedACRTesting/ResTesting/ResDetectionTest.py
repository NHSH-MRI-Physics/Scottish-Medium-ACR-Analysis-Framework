import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage import filters

squares = []
for i in range (1,5):
    squares.append(np.load("MedACR\\ResTesting\\restest_"+str(i)+".npy"))

fig, ax = plt.subplots(nrows=4, ncols=4)
for j in range (0,4):
    for i in range (0,4):
        var = cv2.Laplacian(filters.gaussian(squares[i], sigma=j,preserve_range=True), cv2.CV_64F).var()
        ax[j,i].imshow(filters.gaussian(squares[i], sigma=j))
        ax[j,i].title.set_text(str( "{:.2e}".format(var) ))

plt.tight_layout()
plt.show()
