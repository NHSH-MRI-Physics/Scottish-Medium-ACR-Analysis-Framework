
set Python=C:/Users/Johnt/anaconda3/envs/ACRPhantom/python.exe

REM pyi-makespec .\DataDashboard_Plotly\dash_app.py -n "ACR Data Dashboard" --onefile^
REM --hidden-import=plotly ^

%Python% -m PyInstaller ".\ACR_Data_Dashboard.spec" --distpath ".\DataDashboard_Plotly" --noconfirm  