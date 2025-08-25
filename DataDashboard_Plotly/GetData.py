import pandas as pd
import numpy as np
import random
from datetime import time
import glob
import os
import sys
import pickle
import platform
import os
import datetime
from datetime import datetime, timezone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def creation_date(path_to_file):
    if platform.system() == 'Windows':
       return os.path.getctime(path_to_file)
    else:
       stat = os.stat(path_to_file)
       try:
          # return stat.st_birthtime
          return datetime.fromtimestamp(stat.st_birthtime, tz=timezone.utc)
       except AttributeError:           
          # return stat.st_mtime
          return datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

def GetDummyData():
    dummy_start_date = "2019-01-01"
    dummy_end_date = "2021-10-03"

    full_df = pd.DataFrame()
    Date= []
    TestCount = []
    Tests = []
    Scanner = []
    Time = []

    for date in pd.date_range(dummy_start_date, dummy_end_date):
        Date.append(date)
        TestCount.append(np.random.randint(low=1, high=3))
        Tests.append([None]*TestCount[-1])
        Scanner.append(["GE Scanner"]*TestCount[-1])

        Time.append([])
        for i in range(TestCount[-1]):
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            Time[-1].append(time(hour, minute, second))

    full_df["date"] = Date
    full_df["TestCount"] = TestCount
    full_df["Tests"] = Tests
    full_df["Scanner"] = Scanner
    full_df["date"] = pd.to_datetime(full_df["date"])
    full_df["Time"] = Time

    return full_df

def loadDatabase(path):
    DateDict = {}
    CreationTimeDict = {}
    files = glob.glob(os.path.join(path, "*.docx"))
    for file in files:
        with open(file, 'rb') as f:
            data = pickle.load(f)
            date = data["date"].date()
            creation_time = creation_date(file)
            if date not in DateDict:
                DateDict[date] = [data]
                CreationTimeDict[date] = [creation_time]
            else:
                DateDict[date].append(data)
                CreationTimeDict[date].append(creation_time)

    full_df = pd.DataFrame()
    Dates= []
    TestCount = []
    Tests = []
    ScannerManufacuter = []
    InstitutionName = []
    ScannerModel = []
    ScannerSerialNumber = []
    Time = []
    Sequence = []
    ProcessTimeDate = []

    YearsIncldued = []

    for date in DateDict.keys():
        TestCount.append(len(DateDict[date]))
        Dates.append(date)
        YearsIncldued.append(date.year)
        Tests.append(DateDict[date])
        ScannerManufacuter.append([])
        InstitutionName.append([])
        ScannerModel.append([])
        ScannerSerialNumber.append([])
        Time.append([])
        Sequence.append([])
        ProcessTimeDate.append([])

        for i in range(TestCount[-1]):
            ScannerManufacuter[-1].append(DateDict[date][i]["ScannerDetails"]["Manufacturer"])
            InstitutionName[-1].append(DateDict[date][i]["ScannerDetails"]["Institution Name"])
            ScannerModel[-1].append(DateDict[date][i]["ScannerDetails"]["Model Name"])
            ScannerSerialNumber[-1].append(DateDict[date][i]["ScannerDetails"]["Serial Number"])
            Sequence[-1].append(DateDict[date][i]["Sequence"])
            Time[-1].append(DateDict[date][i]["date"].time())
            ProcessTimeDate[-1].append(CreationTimeDict[date][i])

    #Fill in the gaps with empty stuff
    Startyear = min(set(YearsIncldued))
    Endyear = max(set(YearsIncldued))
    dummy_start_date = str(Startyear)+"-01-01"
    dummy_end_date = str(Endyear)+"-12-31"
    
    for date in pd.date_range(dummy_start_date, dummy_end_date):    
        if date.date() not in Dates:
            Dates.append(date.date())
            TestCount.append(0)
            Tests.append([])
            ScannerManufacuter.append([])
            InstitutionName.append([])
            ScannerModel.append([])
            ScannerSerialNumber.append([])
            Time.append([])
            Sequence.append([])
            ProcessTimeDate.append([])

    full_df["date"] = Dates
    full_df["date"] = pd.to_datetime(full_df["date"])
    full_df["TestCount"] = TestCount
    full_df["Tests"] = Tests
    full_df["ScannerManufacuter"] = ScannerManufacuter
    full_df["InstitutionName"] = InstitutionName
    full_df["ScannerModel"] = ScannerModel
    full_df["ScannerSerialNumber"] = ScannerSerialNumber
    full_df["Time"] = Time
    full_df["Sequence"] = Sequence
    full_df["ProcessTimeDate"] = ProcessTimeDate

    return full_df