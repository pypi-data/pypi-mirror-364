import traceback

try:
    from . import DDebug as debug
    from .DDebug import *
except:
    print("Unable to import DDebug")
try:
    from . import Dev4Tango as dev4tango
    from .Dev4Tango import *
except:
    print("Unable to import Dev4Tango")
    traceback.print_exc()

