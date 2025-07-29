# Define the __all__ variable
__all__ = ["csvutil", "genutil", "jsonutil", "pdfutil"]

import time

s = time.time()
print('[vti] Import csvutil module')
from . import csvutil
print('       Done ({:.0f}ms)'.format(1000*(time.time()-s)))
s = time.time()
print('[vti] Import genutil module')
from . import genutil
print("       Done ({:.0f}ms)".format(1000*(time.time()-s)))
s = time.time()
print('[vti] Import jsonutil module')
from . import jsonutil
print("       Done ({:.0f}ms)".format(1000*(time.time()-s)))
s = time.time()
print('[vti] Import pdfutil module')
from . import pdfutil
print("       Done ({:.0f}ms)".format(1000*(time.time()-s)))