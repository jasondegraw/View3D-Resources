# To run this, install Python and make sure it is in your path
# environment variable, and then run it from the command line
# as
#
#   python vs3tovtk.py input.vs3 output.vtk
#
# This script should work with Python 2.7+ and 3+
#
import sys 
import os
import vs3

fperr = sys.stderr

if not len(sys.argv) in [2,3]:  # Require 2 or 3 arguments
    sys.exit('usage: python vs3tovtk.py <VS3 file> [VTK file]')

# Use exception handling to handle bad file name input
try:
    infile = open(sys.argv[1],'r')
except IOError:
    sys.exit('Failed to open input file "%s"' % sys.argv[1])

if len(sys.argv) == 3:
    outname = sys.argv[2]
else:
    basename = os.path.splitext(sys.argv[1])[0]
    outname = basename + '.vtk'

try:
    outfile = open(outname,'w')
except IOError:
    sys.exit('Failed to open output file "%s"' % outname)

# Read in the VS3 file
vs3data = vs3.Data.load(infile,stringData=True)
infile.close()

# Write the VTK file
vs3data.writeVTK(outfile)
outfile.close()

# Write out the stats
fperr.write('Summary of input file "%s":\n' % sys.argv[0])
fperr.write('  %d vertices\n' % vs3data.nvertices())
fperr.write('  %d surfaces\n' % vs3data.nsurfaces())
#print('    %d regular' % stats['S'])
#print('    %d mask' % stats['M'])
#print('    %d null' % stats['N'])
#print('    %d obstructing' % stats['O'])

