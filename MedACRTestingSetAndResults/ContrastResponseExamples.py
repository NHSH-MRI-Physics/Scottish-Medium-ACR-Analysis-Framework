import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np
import pydicom
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np
from scipy import ndimage

Sigmas = [0, 2, 3.3, 4.2]

x_peaks_Clean = None
x_Troughs_Clean = None
y_peaks_Clean = None
y_Troughs_Clean = None
x_combined_Clean = None
Values_Combined_Clean = None


fig, axs = plt.subplots(len(Sigmas),2, figsize=(10, 12))
def ConvertMagNET(x_peaks, x_Troughs,Peaks,Troughs):
    x_combined = np.concatenate([x_peaks, x_Troughs])
    Values_Combined = np.concatenate([Peaks, Troughs])
    x_combined = np.insert(x_combined, 0, 0)
    x_combined = np.insert(x_combined, 0, -3)
    Values_Combined = np.insert(Values_Combined, 0, 1)
    Values_Combined = np.insert(Values_Combined, 0, 1)

    x_combined = np.append(x_combined, 22)
    Values_Combined = np.append(Values_Combined, 1)

    x_combined = np.append(x_combined, 25)
    Values_Combined = np.append(Values_Combined, 1)
    
    order = np.argsort(x_combined)
    x_combined = x_combined[order]
    Values_Combined = Values_Combined[order]

    x_peaks = x_peaks[1:-1]
    #x_Troughs = x_Troughs[1:-1]
    Peaks = Peaks[1:-1]
    #Troughs = Troughs[1:-1]

    return x_combined, Values_Combined,x_peaks,x_Troughs,Peaks,Troughs

for i in range(len(Sigmas)):
    sigma = Sigmas[i]
    # Plot sin(x) * sin(y)
    x = np.linspace(-2*np.pi, 9 * np.pi, 100)
    y = np.linspace(-2*np.pi, 9 * np.pi, 100) 
    X, Y = np.meshgrid(x, y)
    Z = ((np.sin(X) * np.sin(Y+np.pi)))+0.4
    Z[Z < 0] = 0
    Z_Clean = Z

    Z = ndimage.gaussian_filter(Z, sigma=sigma,mode="reflect")
    Z /= np.max(Z_Clean) 


    points = np.column_stack((X.ravel(), Y.ravel()))
    values = Z.ravel()

    yPos = 7*np.pi/2

    PointsPeaks = [(np.pi/2, yPos),(5*np.pi/2, yPos),(9*np.pi/2, yPos),(13*np.pi/2, yPos)]
    Peaks = griddata(points, values, PointsPeaks, method='cubic') 

    PointsTroughs= [(3*np.pi/2, yPos),(7*np.pi/2, yPos),(11*np.pi/2, yPos)]
    Troughs = griddata(points, values, PointsTroughs, method='cubic')

    StarterPoint = [(0, yPos)]
    StarterZ = griddata(points, values, StarterPoint, method='cubic')[0]

    avgpeak = np.mean(Peaks)
    avgtrough = np.mean(Troughs)

    Res = (avgpeak - avgtrough)/avgpeak

    x_peaks = np.array([pt[0] for pt in PointsPeaks])
    x_Troughs= np.array([pt[0] for pt in PointsTroughs])

    y_peaks = np.array([pt[1] for pt in PointsPeaks])
    y_Troughs= np.array([pt[1] for pt in PointsTroughs])


    if i == 0:
        x_peaks_Clean = x_peaks
        x_Troughs_Clean = x_Troughs
        y_peaks_Clean = Peaks
        y_Troughs_Clean = Troughs



    im0 = axs[i,0].imshow(Z, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower', cmap='Greys_r', aspect='auto', interpolation='none', vmin=np.min(Z), vmax=np.max(Z))
    axs[i,0].plot(x_peaks,y_peaks,linestyle='', marker='x', color='red', label='Peaks')
    axs[i,0].plot(x_Troughs,y_Troughs,linestyle='', marker='x', color='blue', label='Troughs')
    axs[i,0].set_title('Data Grid')
    axs[i,0].set_xlabel('x')
    axs[i,0].set_ylabel('y')
    axs[i,0].set_xlim(0, 7*np.pi)
    axs[i,0].set_ylim(0, 7*np.pi)
    axs[i,0].set_aspect('equal')
    x_combined = np.concatenate([x_peaks, x_Troughs])
    Values_Combined = np.concatenate([Peaks, Troughs])
    x_combined = np.insert(x_combined, 0, 0)
    Values_Combined = np.insert(Values_Combined, 0, StarterZ)
    order = np.argsort(x_combined)
    x_combined = x_combined[order]
    Values_Combined = Values_Combined[order]

    if i == 0:
        x_combined_Clean = x_combined
        Values_Combined_Clean = Values_Combined

    ResolveStatus = "Fully Resolvable"
    if i == 2:
        ResolveStatus = "Barely Resolvable"
    if i > 2:
        ResolveStatus = "Unresolvable"

    axs[i,1].plot(x_peaks, Peaks, 'r', label='Peaks',marker='x',linestyle='')
    axs[i,1].plot(x_Troughs, Troughs, 'b', label='Troughs',marker='x',linestyle='')
    axs[i,1].plot(x_combined,Values_Combined,linestyle='-', color='g')
    axs[i,1].axhline(avgpeak, color='red', linestyle='--')
    axs[i,1].axhline(avgtrough, color='blue', linestyle='--')
    axs[i,1].axhline(0.5, color='yellow', linestyle='--')
    axs[i,1].set_title('Resolution = ' + str(round(Res, 2)*100.0) +"%\nMagNET Resolvaility: " + ResolveStatus)
    axs[i,1].set_xlabel('x')
    axs[i,1].set_ylabel('y')
    axs[i,1].set_ylim(-0.05, 1.05)

    '''
    # MagNet Method
    x_combined, Values_Combined,x_peaks,x_Troughs,Peaks,Troughs = ConvertMagNET(x_peaks, x_Troughs,Peaks,Troughs)

    avgpeak = np.mean(Peaks)
    avgtrough = np.mean(Troughs)

    Res = (avgpeak - avgtrough)

    axs[i,2].plot(x_peaks, Peaks, 'r', label='Peaks',marker='x',linestyle='')
    axs[i,2].plot(x_Troughs, Troughs, 'b', label='Troughs',marker='x',linestyle='')
    axs[i,2].plot(x_combined,Values_Combined,linestyle='-', color='g')
    #axs[i,2].axhline(1, color='red', linestyle='--')
    axs[i,2].axhline(0.5, color='yellow', linestyle='--')
    axs[i,2].axhline(avgpeak, color='blue', linestyle='--')
    axs[i,2].axhline(avgtrough, color='green', linestyle='--')
    axs[i,2].set_title('Resolution = ' + str(round(Res, 2)*100.0) +"%")
    axs[i,2].set_xlabel('x')
    axs[i,2].set_ylabel('y')
    axs[i,2].set_ylim(-0.05, 1.05)
    '''



plt.tight_layout()
plt.savefig("ResExample.png", dpi=300)