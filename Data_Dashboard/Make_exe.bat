rmdir /s /q MedACRModules 2>nul
mkdir MedACRModules
xcopy /E /I /Y ..\MedACRModules MedACRModules
copy  ..\MedACR_ToleranceTableCheckerV2.py MedACR_ToleranceTableCheckerV2.py

REM Run npm commands
call npm install 
call npm run dump
call npm run serve 
REM call npm run app:dist