#Options for the MedACRAnalysis file

from enum import Enum
from hazenlib.tasks.acr_spatial_resolution import ResOptions

class GeometryOptions(Enum):
    ACRMETHOD=1
    MAGNETMETHOD=2

class ParamaterOveride():
    CentreOverride = None
    RadiusOverride = None