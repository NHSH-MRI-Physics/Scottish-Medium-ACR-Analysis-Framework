pyinstaller .\PyInstallerGUI\GUI.py --distpath ".\PyInstallerGUI" -n "ACR QA Analysis" --icon=_internal\ct-scan.ico ^
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
--add-data "_internal\ct-scan.ico;." 

xcopy "ToleranceTable" "PyInstallerGUI\ACR QA Analysis\ToleranceTable\*" /E /Y
cd ".\PyInstallerGUI\"
tar -a -cf ACR_QA_Analysis_Package.zip  "ACR QA Analysis"
cd ..