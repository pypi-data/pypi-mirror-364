# FLImagingClrPy version
__version__ = "6.8.5"

import clr
from .FLImagingClrPyLoader import load_dll

# FLImaging dll Load
load_dll()

from FLImagingCLR import *
from FLImagingCLR.Base import *
from FLImagingCLR.Foundation import *
from FLImagingCLR.GUI import *
from FLImagingCLR.ImageProcessing import *
from FLImagingCLR.AdvancedFunctions import *
from FLImagingCLR.ThreeDim import *
from FLImagingCLR.AI import *
from FLImagingCLR.Devices import *

clr.AddReference("System")
clr.AddReference("mscorlib")

from System import *
from System.Text import *
from System.Collections.Generic import *