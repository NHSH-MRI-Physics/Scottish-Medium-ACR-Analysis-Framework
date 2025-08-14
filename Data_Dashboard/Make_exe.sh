rm -r -f MedACRModules
mkdir MedACRModules
cp -r ../MedACRModules/* MedACRModules/
cp -f ../MedACR_ToleranceTableCheckerV2.py MedACR_ToleranceTableCheckerV2.py
#mkdir hazenlib
#cp -r ../hazenlib/* hazenlib/

# Run npm commands
npm install
npm run dump
npm run serve
# npm run app:dist