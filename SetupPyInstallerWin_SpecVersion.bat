
set Python=C:/Users/Johnt/anaconda3/envs/ACRPhantom/python.exe

%Python% -m unittest discover || echo Unit Tests Failed && exit /b

pyi-makespec .\PyInstallerGUI\GUI.py -n "ACR QA Analysis" --icon=_internal\ct-scan.ico ^
--hidden-import=docopt ^
--hidden-import=cv2 ^
--hidden-import=pydicom.encoders.gdcm ^
--hidden-import=pydicom.encoders.pylibjpeg ^
--hidden-import=imutils ^
--hidden-import=skimage ^
--hidden-import=skimage.filters ^
--hidden-import=colorlog ^
--hidden-import=skimage.segmentation ^
--collect-data sv_ttk ^
--collect-submodules hazenlib ^
--paths . ^
--add-data "_internal\ct-scan.ico;." ^
--splash "_internal\SplashScreen.jpg" 

%Python% -m PyInstaller ".\ACR QA Analysis.spec" --distpath ".\PyInstallerGUI" --noconfirm


xcopy "ToleranceTable" "PyInstallerGUI\ACR QA Analysis\ToleranceTable\*" /E /Y
cd ".\PyInstallerGUI\"
tar -a -cf ACR_QA_Analysis_Package.zip  "ACR QA Analysis"
cd ..