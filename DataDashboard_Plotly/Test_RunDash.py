import subprocess
import sys
from threading import Thread

def RunDash():
    subprocess.run(['DataDashboard_Plotly\ACR_Data_Dashboard.exe'], stderr=sys.stderr, stdout=sys.stdout)


thread = Thread(target = RunDash)
thread.start()

print("adadwaw")
input("Press Enter to continue...")