from hazenlib.ACRObject import ACRObject
import glob
from hazenlib.utils import get_dicom_files
import pydicom
from matplotlib import pyplot as plt
from skimage.measure import profile_line
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy.ndimage import gaussian_filter
import pickle

def rotate_points(points, center, angle_degrees):
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

def ComputeRes(files,blur=0):
    #files = get_dicom_files(fileLoc)
    dcm_list = []
    for file in files:
        dcm_list.append(pydicom.dcmread(file))

    ACRObj = ACRObject(dcm_list,kwargs={'MediumACRPhantom': True})
    Image = ACRObj.images[6]

    if blur != 0:
        Image = gaussian_filter(Image, sigma=blur)

    Mask = ACRObj.mask_image
    LineLen = len(Image[0])
    cx, cy = ACRObj.centre[0], ACRObj.centre[1]
    
    plt.imshow(Image, cmap='gray')
    #plt.imshow(Mask, cmap='gray')
    plt.plot(ACRObj.centre[0], ACRObj.centre[1], 'r+')
    CentreSignal = np.mean(Image[int(cy)-20:int(cy)+20, int(cx)-20:int(cx)+20])*0.9

    profiles = []
    MaskedProfiles = []
    angles = []

    for Angle in range(0,180,1):
        start_point = (cx - LineLen / 2, cy)  # (x1, y1)
        end_point =   (cx + LineLen / 2, cy)  # (x2, y2)
        RotatedPoints = rotate_points([start_point, end_point], ACRObj.centre, Angle)

        #Get back to y,x so we can extract the profiles...
        start_point_rot = (RotatedPoints[0][1], RotatedPoints[0][0])
        end_point_rot   = (RotatedPoints[1][1], RotatedPoints[1][0])
        #plt.plot([start_point_rot[1], end_point_rot[1]], [start_point_rot[0], end_point_rot[0]], 'x', lw=2,color='red',linestyle='dashed')

        profile = profile_line(Image, start_point_rot, end_point_rot, linewidth=1,mode='constant', cval=0)
        profileMask = profile_line(Mask, start_point_rot, end_point_rot, linewidth=1,mode='constant', cval=0)
        profile = np.clip(profile, a_min=None, a_max=CentreSignal)
        profiles.append(profile)
        MaskedProfiles.append(profileMask)
        angles.append(Angle)
    plt.colorbar()
    if blur == 0:
        plt.savefig("ResTesting\\Image.png")
    else:
        plt.savefig("ResTesting\\Image Blur " +str(blur)+".png")
    plt.close()

    HorRes=[]
    VertRes= []
    AllRes = []

    Results = []
    for i in range(len(profiles)):
        MaskProfile = MaskedProfiles[i]
        Edges = np.diff(MaskProfile)

        '''
        plt.plot(Edges)
        plt.savefig("Edges.png")
        plt.close()

        plt.plot(MaskProfile)
        plt.savefig("MaskProfile.png")
        plt.close()
        '''

        LowerEdge = np.where(Edges == 1)[0][0]
        UpperEdge = np.where(Edges == -1)[0][0]

        LineProfile = profiles[i]
        CandidateProfiles = [LineProfile[LowerEdge-10:LowerEdge+10], LineProfile[UpperEdge-10:UpperEdge+10]]

        ExtractedProfiles = []
        for profile in CandidateProfiles:
            if len(np.where(profile >= CentreSignal)[0])>3:  
                ExtractedProfiles.append(profile)
        
        MTF = []
        Res = []
        freq=[]
        for profile in ExtractedProfiles:
                lsf = np.diff(profile)
                window = np.hamming(len(lsf))
                lsf_windowed = lsf * window
                fft_vals = np.fft.fft(lsf_windowed, n=512)
                mtf = np.abs(fft_vals)
                mtf = mtf / mtf[0]
                frequencies = np.fft.fftfreq(512)[:256]
                mtf_positive = mtf[:256]
                mtf_Perfect = np.ones(256)
                integral_area = np.trapz(mtf_positive, frequencies)
                PerfectIntegral =  np.trapz(mtf_Perfect, frequencies)
                res = integral_area/PerfectIntegral
                MTF.append(mtf_positive)
                Res.append(res)
                freq.append(frequencies)

        '''
        for profile in ExtractedProfiles:
            plt.plot(profile)
        plt.title("Profiles at "+str(angles[i])+"°")
        plt.savefig("Profile.png")
        plt.close()

        plt.figure(figsize=(6, 4))
        for I in range(len(MTF)):
            plt.plot(freq[I], MTF[I], lw=2)
        plt.title("Modulation Transfer Function (MTF)")
        plt.xlabel("Spatial Frequency (cycles/pixel)")
        plt.ylabel("MTF (Response)")
        plt.grid(True)
        plt.ylim(0, 1.05)
        plt.savefig("MTF.png")
        plt.close()
        '''
        #print("Resolution at "+str(angles[i])+"°: "+str(np.mean(Res)))

        Results.append([angles[i]]+Res)

        if angles[i] < 45 or angles[i] > 135 and angles[i] < 225 or angles[i] > 315:
            HorRes+=Res
        else:
            VertRes += Res
        AllRes += Res

    return Results, np.mean(HorRes), np.mean(VertRes), np.mean(AllRes)

#fileLoc = "MedACRTestingSetAndResults\\Blair Gartnavel"
#Results, HorRes, VertRes, AllRes = ComputeRes(fileLoc)

#print("Horizontal Resolution: ", HorRes)
#print("Vertical Resolution: ", VertRes)
#print("Overall Resolution: ", AllRes)

def TestBatch(blur=0):
    target_path = Path("C:\\Users\\John\\Desktop\\MedACRRuns")
    folders = [f for f in target_path.iterdir() if f.is_dir()]
    f = open("ResTesting/Result.txt","w")

    dates = []
    VertResults = []
    HorResults = []
    HorVertResults = []

    DumpResults = {}
    DumpResults['1.1mm holes Horizontal']=[]
    DumpResults['1.0mm holes Horizontal']=[]
    DumpResults['0.9mm holes Horizontal']=[]
    DumpResults['0.8mm holes Horizontal']=[]

    DumpResults['1.1mm holes Vertical']=[]
    DumpResults['1.0mm holes Vertical']=[]
    DumpResults['0.9mm holes Vertical']=[]
    DumpResults['0.8mm holes Vertical']=[]
    DumpDates = []

    for folder in folders:
        Fullpath = Path.joinpath(folder,"DICOMS")
        files = get_dicom_files(Fullpath)
        DICOMDict = {}
        for file in files:
            seq = pydicom.dcmread(file).SeriesDescription 
            if seq not in DICOMDict.keys():
                DICOMDict[seq] = []
            DICOMDict[seq].append(file)

        for key in DICOMDict.keys():
            Results, HorRes, VertRes, AllRes = ComputeRes(DICOMDict[key],blur)


            AllResults = []
            for Result in Results:
                AllResults+=Result[1:]

            Text ="Folder: " + folder.name+ " Seq:" + key + " Hor: " + str(round(HorRes,3)) + " Vert:" + str(round(VertRes,3)) + " AllRes:" + str(round(AllRes,3)) + " ("+ str(round(np.max(AllResults),3)) +","+str(round(np.min(AllResults),3))+")"
            f.write(Text+"\n")
            f.flush()

            dates.append(datetime.strptime(folder.name.split("_")[-1], "%Y-%m-%d %H-%M-%S"))
            VertResults.append(VertRes)
            HorResults.append(HorRes)
            HorVertResults.append(AllRes)

            DumpFiles = glob.glob(str(Path.joinpath(folder,"*.docx")))
            for DumpFile in DumpFiles:
                with open(DumpFile, 'rb') as FILE:
                    data = pickle.load(FILE)
                    DUMP = (data["Test"]["SpatialRes"].results["measurement"])
                    DumpResults['1.1mm holes Horizontal'].append(DUMP['1.1mm holes Horizontal'])
                    DumpResults['1.0mm holes Horizontal'].append(DUMP['1.0mm holes Horizontal'])
                    DumpResults['0.9mm holes Horizontal'].append(DUMP['0.9mm holes Horizontal'])
                    DumpResults['0.8mm holes Horizontal'].append(DUMP['0.8mm holes Horizontal'])

                    DumpResults['1.1mm holes Vertical'].append(DUMP['1.1mm holes Vertical'])
                    DumpResults['0.9mm holes Vertical'].append(DUMP['1.0mm holes Vertical'])
                    DumpResults['0.8mm holes Vertical'].append(DUMP['0.9mm holes Vertical'])
                    DumpResults['0.8mm holes Vertical'].append(DUMP['0.8mm holes Vertical'])
                    DumpDates.append(data["date_scanned"])
            
    fig, axes = plt.subplots(3, 5, figsize=(60, 20))

    def Plot(i,j,x,y,title):
        axes[i, j].plot(x, y, color='tab:blue',linestyle="",marker="x")
        Mean = np.mean(y)
        STD = [np.mean(y)-np.std(y),np.mean(y)+np.std(y)]
        axes[i, j].axhline(Mean,label="Average=" + str(round(Mean,3)))
        axes[i, j].axhline(STD[0],label="Upper STD=" + str(round(STD[0],3)),linestyle="--")
        axes[i, j].axhline(STD[1],label="Lower STD=" + str(round(STD[1],3)),linestyle="--")
        axes[i, j].legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
        axes[i, j].set_title(title)

    Plot(0,0,dates,VertResults,'Vertical Res')
    Plot(1,0,dates,HorResults,'Horizontal Res')
    Plot(2,0,dates,HorVertResults,'Hor and Vert Res')

    Plot(0,1,DumpDates,DumpResults["1.1mm holes Vertical"],'1.1mm Vertical Res')
    Plot(1,1,DumpDates,DumpResults["1.1mm holes Horizontal"],'1.1mm Horizontal Res')

    Plot(0,1,DumpDates,DumpResults["1.0mm holes Vertical"],'1.0mm Vertical Res')
    Plot(1,1,DumpDates,DumpResults["1.0mm holes Horizontal"],'1.0mm Horizontal Res')

    Plot(0,1,DumpDates,DumpResults["0.9mm holes Vertical"],'0.9mm Vertical Res')
    Plot(1,1,DumpDates,DumpResults["0.9mm holes Horizontal"],'0.9mm Horizontal Res')

    Plot(0,1,DumpDates,DumpResults["0.8mm holes Vertical"],'0.8mm Vertical Res')
    Plot(1,1,DumpDates,DumpResults["0.8mm holes Horizontal"],'0.8mm Horizontal Res')

    '''
    axes[0, 0].plot(dates, VertResults, color='tab:blue',linestyle="",marker="x")
    Mean = np.mean(VertResults)
    STD = [np.mean(VertResults)-np.std(VertResults),np.mean(VertResults)+np.std(VertResults)]
    axes[0, 0].axhline(Mean,label="Average=" + str(round(Mean,3)))
    axes[0, 0].axhline(STD[0],label="Upper STD=" + str(round(STD[0],3)),linestyle="--")
    axes[0, 0].axhline(STD[1],label="Lower STD=" + str(round(STD[1],3)),linestyle="--")
    axes[0, 0].legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    axes[0, 0].set_title('Vertical Res')

    axes[1, 0].plot(dates, HorResults, color='tab:orange',linestyle="",marker="x")
    Mean = np.mean(HorResults)
    STD = [np.mean(HorResults)-np.std(HorResults),np.mean(HorResults)+np.std(HorResults)]
    axes[1, 0].axhline(Mean,label="Average=" + str(round(Mean,3)))
    axes[1, 0].axhline(STD[0],label="Upper STD=" + str(round(STD[0],3)),linestyle="--")
    axes[1, 0].axhline(STD[1],label="Lower STD=" + str(round(STD[1],3)),linestyle="--")
    axes[1, 0].legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    axes[1, 0].set_title('Horizontal Res')

    axes[2, 0].plot(dates, HorVertResults, color='tab:green',linestyle="",marker="x")
    Mean = np.mean(HorVertResults)
    STD = [np.mean(HorVertResults)-np.std(HorVertResults),np.mean(HorVertResults)+np.std(HorVertResults)]
    axes[2, 0].axhline(Mean,label="Average=" + str(round(Mean,3)))
    axes[2, 0].axhline(STD[0],label="Upper STD=" + str(round(STD[0],3)),linestyle="--")
    axes[2, 0].axhline(STD[1],label="Lower STD=" + str(round(STD[1],3)),linestyle="--")
    axes[2, 0].legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    axes[2, 0].set_title('Hor and Vert Res')
    '''


    plt.tight_layout()
    if blur !=0:
        plt.savefig("ResTesting/Results-Blur "+str(blur)+".png")
    else:
        plt.savefig("ResTesting/Results.png")
    plt.close()
    return np.mean(HorVertResults)

def TestBlur():
    blur = 0
    Blur = np.arange(0, 2.1, 0.2)
    AvgRes = []
    for blur in Blur:
        AvgRes.append(TestBatch(blur))
    
    plt.plot(Blur,AvgRes)
    plt.xlabel("Guassian Sigma")
    plt.ylabel("Res")
    plt.savefig("ResTesting/Blur.png")

#TestBlur()

TestBatch()