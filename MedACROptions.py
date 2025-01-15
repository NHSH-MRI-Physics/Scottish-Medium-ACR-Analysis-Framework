#Options for the MedACRAnalysis file

from enum import Enum
from hazenlib.tasks.acr_spatial_resolution import ResOptions
import numpy as np
class GeometryOptions(Enum):
    ACRMETHOD=1
    MAGNETMETHOD=2

class ParamaterOveride():
    def __init__(self):
        self.CentreOverride = None
        self.RadiusOverride = None
        self.MaskingOverride = np.array( [np.array(None),np.array(None),np.array(None),np.array(None),np.array(None),np.array(None),np.array(None),np.array(None),np.array(None),np.array(None),np.array(None)] )