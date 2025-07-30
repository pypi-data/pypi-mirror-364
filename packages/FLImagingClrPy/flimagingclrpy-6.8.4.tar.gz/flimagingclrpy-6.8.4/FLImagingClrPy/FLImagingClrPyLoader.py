# Begin of FLImaging(R) initialization

import clr
import glob
import os
import platform

def load_dll():
    arch = platform.architecture()[0]  # '32bit' or '64bit'

    if arch == '64bit':
        dll_pattern = "FLImaging*X64CLR.dll"
        dll_dir = r'C:/Program Files/FLImaging/FLImaging/BinaryX64/'
    else:
        dll_pattern = "FLImaging*X86CLR.dll"
        dll_dir = r'C:/Program Files/FLImaging/FLImaging/Binary/'

    dllFiles = glob.glob(os.path.join(dll_dir, dll_pattern))

    for path in dllFiles:
        clr.AddReference(path)

# End of FLImaging(R) initialization
