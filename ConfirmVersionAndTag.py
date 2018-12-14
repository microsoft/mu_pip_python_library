'''
Quick script to check that the wheel/package created is aligned on a git tag.
Official releases should not be made from non-tagged code.
'''

import glob
import os
import sys

p = os.path.join(os.getcwd(), "dist")
whlfile = glob.glob(os.path.join(p, "*.whl"))
if(len(whlfile) != 1):
    for filename in whlfile:
        print(filename)
    raise Exception("Too many wheel files")
v = whlfile[0].split("-")[1]
if v.count(".") > 2:
    raise Exception("Version %s not in format major.minor.patch" % v)
print("version: " + str(v))
sys.exit(0)
