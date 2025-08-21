import pandas as pd
import numpy as np
def GetDummyData():
    dummy_start_date = "2019-01-01"
    dummy_end_date = "2021-10-03"
    full_df = pd.DataFrame({
        "date": pd.date_range(dummy_start_date, dummy_end_date),
        "TestCount": np.random.randint(low=0, high=30, size=(pd.to_datetime(dummy_end_date) - pd.to_datetime(dummy_start_date)).days + 1,),
        "Tests": [None]*((pd.to_datetime(dummy_end_date) - pd.to_datetime(dummy_start_date)).days + 1)
    })
    return full_df