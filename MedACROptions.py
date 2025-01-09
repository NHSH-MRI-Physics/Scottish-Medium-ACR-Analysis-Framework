#Options for the MedACRAnalysis file

from enum import Enum
from hazenlib.tasks.acr_spatial_resolution import ResOptions
import numpy as np
class GeometryOptions(Enum):
    ACRMETHOD=1
    MAGNETMETHOD=2

class ParamaterOveride():
    CentreOverride = None
    RadiusOverride = None
    MaskingOverride = np.array( [None,None,None,None,None,None,None,None,None,None,None,] )