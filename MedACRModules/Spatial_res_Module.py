
from MedACRModules.MedACRModuleAbstract import MedACRModule
from hazenlib.tasks.acr_spatial_resolution import ACRSpatialResolution
import MedACR_ToleranceTableCheckerV2 as MedACR_ToleranceTableChecker
from MedACROptions import *
import matplotlib.pyplot as plt
import scipy.ndimage
import os
class SpatialResModule(MedACRModule):

    def __init__(self,name,settings):
        self.name = name
        self.settings = settings
        self.results = None
        super(MedACRModule,self).__init__()
        

    def Run(self):
        Data = self.settings["Data"]
        OutputPath = self.settings["OutputPath"]
        ParamaterOverides = self.settings["ParamaterOverides"]
        SpatialResMethod = self.settings["SpatialResMethod"]

        print("Running Spatial Resolution")
        #Run the dot matrix version
        if SpatialResMethod != ResOptions.Manual:
            acr_spatial_resolution_task = ACRSpatialResolution(input_data=Data,report_dir=OutputPath,report=True,MediumACRPhantom=True,Paramater_overide = ParamaterOverides)
            acr_spatial_resolution_task.ResOption=SpatialResMethod
            self.results = acr_spatial_resolution_task.run()


    def GetReportText(self):
        SpatialResMethod = self.settings["SpatialResMethod"]
        ManualResData = self.settings["ManualResData"]
        OutputPath = self.settings["OutputPath"]
        Seq = self.settings["Seq"]
        Text = ""
        if SpatialResMethod == ResOptions.DotMatrixMethod:
            Text+=( '\t1.1mm Holes Score: %-12s%-12s\n' % (str(self.results["measurement"]["1.1mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["1.1mm holes"],"Spatial Resolution 1.1mm") ))
            Text+=( '\t1.0mm Holes Score: %-12s%-12s\n' % (str(self.results["measurement"]["1.0mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["1.0mm holes"],"Spatial Resolution 1.0mm") ))
            Text+=( '\t0.9mm Holes Score: %-12s%-12s\n' % (str(self.results["measurement"]["0.9mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["0.9mm holes"],"Spatial Resolution 0.9mm") ))
            Text+=( '\t0.8mm Holes Score: %-12s%-12s' % (str(self.results["measurement"]["0.8mm holes"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["0.8mm holes"],"Spatial Resolution 0.8mm") ))
            
        elif SpatialResMethod == ResOptions.MTFMethod:
            #Run the MTF
            Text+=( '\tRaw MTF50 :        %-12s%-12s\n' % (str(self.results["measurement"]["raw mtf50"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["raw mtf50"],"Spatial Resolution MTF50 Raw") ))
            Text+=( '\tFitted MTF50:      %-12s%-12s' % (str(self.results["measurement"]["fitted mtf50"]),MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["fitted mtf50"],"Spatial Resolution MTF50 Fitted") ))

        elif SpatialResMethod == ResOptions.ContrastResponseMethod:
            Text+=( '\tHorizontal Contrast Response\n')
            Text+=( '\t\t1.1mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["1.1mm holes Horizontal"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["1.1mm holes Horizontal"],"Contrast Response Resolution","1.1mm holes Horizontal")))
            Text+=( '\t\t1.0mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["1.0mm holes Horizontal"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["1.0mm holes Horizontal"],"Contrast Response Resolution","1.0mm holes Horizontal")))
            Text+=( '\t\t0.9mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["0.9mm holes Horizontal"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["0.9mm holes Horizontal"],"Contrast Response Resolution","0.9mm holes Horizontal")))
            Text+=( '\t\t0.8mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["0.8mm holes Horizontal"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["0.8mm holes Horizontal"],"Contrast Response Resolution","0.8mm holes Horizontal")))

            Text+=( '\tVertical Contrast Response\n')
            Text+=( '\t\t1.1mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["1.1mm holes Vertical"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["1.1mm holes Vertical"],"Contrast Response Resolution","1.1mm holes Vertical")))
            Text+=( '\t\t1.0mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["1.0mm holes Vertical"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["1.0mm holes Vertical"],"Contrast Response Resolution","1.0mm holes Vertical")))
            Text+=( '\t\t0.9mm Contrast Response: %-12s%-12s\n' % (str(self.results["measurement"]["0.9mm holes Vertical"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["0.9mm holes Vertical"],"Contrast Response Resolution","0.9mm holes Vertical")))
            Text+=( '\t\t0.8mm Contrast Response: %-12s%-12s' % (str(self.results["measurement"]["0.8mm holes Vertical"])+"%",MedACR_ToleranceTableChecker.GetPassResult(self.results["measurement"]["0.8mm holes Vertical"],"Contrast Response Resolution","0.8mm holes Vertical")))
        elif SpatialResMethod == ResOptions.Manual:
            pass
        else:
            raise Exception("Unexpected option in spatial res module")
        

        #Add in Manual Res Test
        if ManualResData != None:
            for key in ManualResData:
                Result = "Not Tested"
                import matplotlib
                matplotlib.use( 'tkagg' )
                fig, (ax1, ax2, ax3) = plt.subplots(3,1)
                fig.suptitle(key + ' Manual Resolution Output',y=0.99)
                fig.set_size_inches(20, 20)
                ax1.imshow(ManualResData[key].Image)


                ContrastResponse = []
                for Direction in range(2):                    
                    xpointsPeaks = ManualResData[key].ChosenPointsXPeaks[Direction]
                    ypointsPeaks = ManualResData[key].ChosenPointsYPeaks[Direction]
                    xpointsTroughs = ManualResData[key].ChosenPointsXTroughs[Direction]
                    ypointsTroughs = ManualResData[key].ChosenPointsYTroughs[Direction]

                    #if Direction==0:
                    #    xpointsPeaks, ypointsPeaks = zip(*sorted(zip(xpointsPeaks, ypointsPeaks)))
                    #    xpointsTroughs, ypointsTroughs = zip(*sorted(zip(xpointsTroughs, ypointsTroughs)))
                    #else:
                    #    ypointsPeaks, xpointsPeaks = zip(*sorted(zip(ypointsPeaks, xpointsPeaks)))
                    #    ypointsTroughs, xpointsTroughs = zip(*sorted(zip(ypointsTroughs, xpointsTroughs)))

                    pointsX = [xpointsPeaks[0],xpointsTroughs[0],xpointsPeaks[1],xpointsTroughs[1],xpointsPeaks[2],xpointsTroughs[2],xpointsPeaks[3]]
                    pointsY = [ypointsPeaks[0],ypointsTroughs[0],ypointsPeaks[1],ypointsTroughs[1],ypointsPeaks[2],ypointsTroughs[2],ypointsPeaks[3]]
                    if Direction==0:
                        ax1.plot(pointsX, pointsY,marker="",ls='-',color="blue",markersize=10)
                    else:
                        ax1.plot(pointsX, pointsY,marker="",ls='-',color="red",markersize=10)



                    #Do Peaks
                    zPeaks = scipy.ndimage.map_coordinates(ManualResData[key].Image, np.vstack((ypointsPeaks,xpointsPeaks)),order=1, mode = "nearest",output=np.float32)

                    xLine = np.array([])
                    yLine = np.array([])                    
                    for i in range(3):
                        endpoint = False
                        if i == 2:
                            endpoint=True
                        num = 50
                        xLine=np.append(xLine, np.linspace(xpointsPeaks[i],xpointsTroughs[i],endpoint=False,num=num))
                        xLine=np.append(xLine, np.linspace(xpointsTroughs[i],xpointsPeaks[i+1],endpoint=endpoint,num=num))

                        yLine=np.append(yLine, np.linspace(ypointsPeaks[i],ypointsTroughs[i],endpoint=False,num=num))
                        yLine=np.append(yLine, np.linspace(ypointsTroughs[i],ypointsPeaks[i+1],endpoint=endpoint,num=num))
                    zLine = scipy.ndimage.map_coordinates(ManualResData[key].Image, np.vstack((yLine,xLine)),output=np.float32,order=1, mode = "nearest")
           
                    MeanPeak = np.mean(zPeaks)
                    if Direction==0:
                        ax1.plot(xpointsPeaks, ypointsPeaks,marker="X",ls='',color="blue",markersize=10)
                    else:
                        ax1.plot(xpointsPeaks, ypointsPeaks,marker="X",ls='',color="red",markersize=10)

                    if Direction==0: 
                        ax2.plot(xpointsPeaks,zPeaks, marker="X",ls='',color="blue",markersize=10,label ="Horizontal Peaks")  
                        ax2.axhline(y=MeanPeak, color='blue', linestyle='-',label ="Mean Peak")
                        #sorted_x, sorted_y = zip(*sorted(zip(xLine, zLine)))
                        ax2.plot(xLine,zLine ,marker="",ls='-.',color="blue",label="Sample Line")
                    else:
                        ax3.plot(ypointsPeaks,zPeaks, marker="X",ls='',color="red",markersize=10,label ="Vertical Peaks")   
                        ax3.axhline(y=MeanPeak, color='red', linestyle='-',label ="Mean Peak")  
                        #sorted_x, sorted_y = zip(*sorted(zip(yLine, zLine)))    
                        ax3.plot(yLine, zLine,marker="",ls='-.',color="red",label="Sample Line") 

                    #Do Troughs
                    zTroughs = scipy.ndimage.map_coordinates(ManualResData[key].Image, np.vstack((ypointsTroughs,xpointsTroughs)),order=1, mode = "nearest",output=np.float32)
                    MeanTrough = np.mean(zTroughs)
                    if Direction==0:
                        ax1.plot(xpointsTroughs, ypointsTroughs,marker="o",ls='',color="blue",markersize=10)
                    else:
                        ax1.plot(xpointsTroughs, ypointsTroughs,marker="o",ls='',color="red",markersize=10)
            
                    if Direction==0: 
                        ax2.plot(xpointsTroughs,zTroughs, marker="o",ls='',color="blue",markersize=10,label ="Horizontal Troughs")     
                        ax2.axhline(y=MeanTrough, color='blue', linestyle='--',label ="Mean Trough")
                        ax2.legend()
                    else:       
                        ax3.plot(ypointsTroughs,zTroughs, marker="o",ls='',color="red",markersize=10,label ="Vertical Troughs")   
                        ax3.axhline(y=MeanTrough, color='red', linestyle='--',label ="Mean Trough")
                        ax3.legend()
                    
                    Amplitude = abs(MeanPeak - MeanTrough)
                    ContrastResponse.append(round( (Amplitude/MeanPeak)*100.0,2))
                
                fig.tight_layout()
                if not os.path.exists(OutputPath+"/ACRSpatialResolution"):
                    os.makedirs(OutputPath+"/ACRSpatialResolution")
                plt.savefig(OutputPath+"/ACRSpatialResolution/"+Seq+"_"+key+"_ManualRes.png")
                plt.close()
                #plt.show()

                Text+=( '\tManual '+key+' Resolution Hor: %-15s%-12s\n' % (str(ContrastResponse[0]) +"%",MedACR_ToleranceTableChecker.GetPassResult(ContrastResponse[0],"Manual Resolution",key +" Horizontal")))
                Text+=( '\tManual '+key+' Resolution Vert: %-15s%-12s' % (str(ContrastResponse[1]) +"%",MedACR_ToleranceTableChecker.GetPassResult(ContrastResponse[1],"Manual Resolution",key +" Vertical")))

        return Text

    def GetModuleName(self):
        return self.name
