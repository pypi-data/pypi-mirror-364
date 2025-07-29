# Define the __all__ variable
__all__ = ["csvutil", "genutil"]

import time

s = time.time()
print('[vti] Import csvutil module')
from . import csvutil
print('      Done ({}s)'.format(time.time()))
s = time.time()
print('[vti] Import genutil module')
from . import genutil
print("      Done ({}s)".format(time.time()))

print('[vti] Modules imported successfully.')