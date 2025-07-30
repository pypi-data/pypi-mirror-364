import ctypes
import platform
from .basic import *
from .cvt_color import *

if platform.system() == 'Windows':
	ctypes.windll.shcore.SetProcessDpiAwareness(2)