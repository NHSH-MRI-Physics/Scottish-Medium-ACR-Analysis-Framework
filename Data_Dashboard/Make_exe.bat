rmdir /s /q MedACRModules 2>nul
mkdir MedACRModules
xcopy /E /I /Y ..\MedACRModules MedACRModules


REM Run npm commands
call npm install 
call npm run dump
call npm run serve 
call npm run app:dist