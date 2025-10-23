pyi-makespec DatabaseWriter/DatabaseAdder.py -n DatabaseAdder --paths . --collect-submodules=MedACRModules \
 --hidden-import=MedACRModules.SNR_Module \
 --hidden-import=MedACRModules.Geo_Acc_Module \
 --hidden-import=MedACRModules.Empty_Module \
 --hidden-import=MedACRModules.Ghosting_Module \
 --hidden-import=MedACRModules.SlicePos_Module \
 --hidden-import=MedACRModules.SliceThickness_Module \
 --hidden-import=MedACRModules.Spatial_res_Module \
 --hidden-import=MedACRModules.Uniformity_Module 

pyinstaller DatabaseAdder.spec --distpath DatabaseWriter --noconfirm
mkdir /Users/john/Documents/Hazen-ScottishACR-Fork/DatabaseWriter/DatabaseAdder/DatabaseWriter
cp DatabaseWriter/qaproject-441416-f5fec0c61099.json /Users/john/Documents/Hazen-ScottishACR-Fork/DatabaseWriter/DatabaseAdder/DatabaseWriter/qaproject-441416-f5fec0c61099.json