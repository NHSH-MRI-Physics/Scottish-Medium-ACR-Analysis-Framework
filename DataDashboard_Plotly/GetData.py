import pandas as pd
import numpy as np
import random
def GetDummyData():
    dummy_start_date = "2019-01-01"
    dummy_end_date = "2021-10-03"

    full_df = pd.DataFrame()
    Date= []
    TestCount = []
    Tests = []
    Scanner = []

    for date in pd.date_range(dummy_start_date, dummy_end_date):
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        new_datetime = date.replace(hour=hour, minute=minute, second=second)
        
        Date.append(date)
        TestCount.append(np.random.randint(low=1, high=3))
        Tests.append([None]*TestCount[-1])
        Scanner.append(["GE Scanner"]*TestCount[-1])

    full_df["date"] = Date
    full_df["TestCount"] = TestCount
    full_df["Tests"] = Tests
    full_df["Scanner"] = Scanner
    full_df["date"] = pd.to_datetime(full_df["date"])

    return full_df