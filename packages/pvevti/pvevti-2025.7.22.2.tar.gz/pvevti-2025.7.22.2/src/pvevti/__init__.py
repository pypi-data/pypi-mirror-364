# Define the __all__ variable
__all__ = ["csvutil", "genutil", "jsonutil"]

import time

s = time.time()
print('[vti] Import csvutil module')
from . import csvutil
print('      Done ({}ms)'.format(1000*(time.time()-s)))
s = time.time()
print('[vti] Import genutil module')
from . import genutil
print("      Done ({}ms)".format(1000*(time.time()-s)))
s = time.time()
print('[vti] Import jsonutil module')
from . import jsonutil
print("      Done ({}ms)".format(1000*(time.time()-s)))

print('[vti] Modules imported successfully.')