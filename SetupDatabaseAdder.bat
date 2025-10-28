
set Python=C:/Users/Johnt/anaconda3/envs/ACRPhantom/python.exe

pyi-makespec DatabaseWriter/DatabaseAdder.py -n DatabaseAdder --paths . --collect-submodules=MedACRModules \
 --hidden-import=MedACRModules.SNR_Module \
 --hidden-import=MedACRModules.Geo_Acc_Module \
 --hidden-import=MedACRModules.Empty_Module \
 --hidden-import=MedACRModules.Ghosting_Module \
 --hidden-import=MedACRModules.SlicePos_Module \
 --hidden-import=MedACRModules.SliceThickness_Module \
 --hidden-import=MedACRModules.Spatial_res_Module \
 --hidden-import=MedACRModules.Uniformity_Module 

%Python% -m PyInstaller "DatabaseAdder.spec" --distpath "DatabaseWriter" --noconfirm
md "DatabaseWriter\DatabaseAdder\DatabaseWriter"
copy /Y "DatabaseWriter\qaproject-441416-f5fec0c61099.json" "DatabaseWriter\DatabaseAdder\DatabaseWriter\qaproject-441416-f5fec0c61099.json"
cd ".\DatabaseWriter\"
tar -a -cf DatabaseAdder.zip  "DatabaseAdder"
cd ..