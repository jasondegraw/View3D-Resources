# To run this, install Python 2.7 and make sure it is in your
# path environment variable, and then run it from the command
# line as
#
#   python vs3refine delta input.vs3 output.vs3
#
#
import sys
import math
import numpy

# TODO:
# 1) Clean up the output
# 2) Integrate this with the other scripts
# 3) Move the more general geometry stuff out of here
# 4) Decide if the numpy dependency is really needed

def bilinearInterpolate(x,i,j,di,dj):
    s1 = x[i  ,j  ]
    s2 = x[i+1,j  ]
    s3 = x[i+1,j+1]
    s4 = x[i  ,j+1]
    a1 =  s1
    a2 = -s1 + s2
    a3 = -s1 + s4
    a5 =  s1 - s2 + s3 - s4   
    return a1 + a2*di + a3*dj + a5*di*dj

# A vertex class
class Vertex(object):
    def __init__(self,nr,x,y,z):
        self.nr = nr
        self.x = x
        self.y = y
        self.z = z
    def __str__(self):
        return 'V %d %g %g %g' % (self.nr, self.x, self.y, self.z)

# A surface class
class Surface(object):
    def __init__(self,nr,verts,base=0,combo=0,emit=0.5,name=None):
        self.nr = nr
        self.vertices = verts
        self.base = base
        self.combo = combo
        self.emit = emit
        if name:
            self.name = name
        else:
            self.name = 'Surface-%d' % nr
    def __str__(self):
        out = 'S %d' % self.nr
        for vertex in self.vertices:
            out += ' %d' % vertex.nr
        out += ' %d %d %s %s' % (self.base,self.combo,self.emit,self.name)
        return out
    def findSubdivision(self,delta,sides):
        # Attempt to get a subdivision of the even numbered sides
        # The "sides" input is a list of side ids - e.g. [0,1,2,3]
        N = 0
        for i in sides:
            ip1 = i+1
            if ip1 == 4:
                ip1=0
            dx = self.vertices[ip1].x -  self.vertices[i].x
            dy = self.vertices[ip1].y -  self.vertices[i].y
            dz = self.vertices[ip1].z -  self.vertices[i].z
            mag = math.sqrt(dx*dx+dy*dy+dz*dz)
            N = max(N,int(mag/delta))
        return N+1
    def findSubdivisionEven(self,delta):
        return self.findSubdivision(delta,[0,2])
    def findSubdivisionOdd(self,delta):
        return self.findSubdivision(delta,[1,3])

fperr = sys.stderr

if len(sys.argv) != 4: 
    sys.exit('usage: python vs3refine <delta> <VS3 input file> <VS3 output file>')

# Use exception handling to handle bad file name input
try:
    infile = open(sys.argv[2],'r')
except IOError:
    sys.exit('Failed to open input file "%s"' % sys.argv[2])

try:
    outfile = open(sys.argv[3],'w')
except IOError:
    sys.exit('Failed to open output file "%s"' % sys.argv[3])

delta = float(sys.argv[1])

# Initialize a dictionary (an associative array) to count vertices
# and surfaces
stats = {'V':0,'S':0,'M':0,'N':0,'O':0}

lines = {}
for key in stats.keys():
    lines[key]=[]

# Step through the file line by line - some files will not get through
# this step very well.  Make sure that all the control lines are first
# and limit the number of comments in the vertex and surface sections
# (comments are all getting copied over to the output and will end up
# at the top of the file).
for line in infile:
    firstChar = line.strip()[0].upper()
    if firstChar in stats:  # Is this something we're looking for?
        stats[firstChar] += 1
        lines[firstChar].append(line.strip()[1:].strip())
    elif firstChar in ['E','*']: # Bail out if this is the end flag
        break
    else:
        outfile.write(line)

# Convert the vertices into Python objects
vertices = []
for line in lines['V']:
    data = line.split()
    vertices.append(Vertex(int(data[0]), float(data[1]),
                    float(data[2]), float(data[3])))

# Step through the regular surfaces and make objects out of them
surfaces = []
for line in lines['S']:
    data = line.split()
    print(data)
    nr = int(data[0])
    verts = [vertices[int(x)-1] for x in data[1:5]]
    base = int(data[5])
    combo = int(data[6])
    emit = data[7]
    name = data[8]
    surfaces.append(Surface(nr, verts, base=base, combo=combo,
                            emit=emit, name=name))

xr = numpy.zeros((2,2))
yr = numpy.zeros((2,2))
zr = numpy.zeros((2,2))

newVertices = []
newSurfaces = []
offset = 0

# Try to figure out the correct subdivision (need to do this better)
for surface in surfaces:
    # Use a fairly brain-dead calculation to guess the resolution
    nx = surface.findSubdivisionEven(delta)
    ny = surface.findSubdivisionOdd(delta)
    print(surface.name,nx,ny)
    # Make the right size arrays
    # x = numpy.zeros((nx+1,ny+1))
    # y = numpy.zeros((nx+1,ny+1))
    # z = numpy.zeros((nx+1,ny+1))
    # Copy the vertices into the array form we need
    xr[0,0] = surface.vertices[0].x
    yr[0,0] = surface.vertices[0].y
    zr[0,0] = surface.vertices[0].z
    xr[1,0] = surface.vertices[1].x
    yr[1,0] = surface.vertices[1].y
    zr[1,0] = surface.vertices[1].z
    xr[1,1] = surface.vertices[2].x
    yr[1,1] = surface.vertices[2].y
    zr[1,1] = surface.vertices[2].z
    xr[0,1] = surface.vertices[3].x
    yr[0,1] = surface.vertices[3].y
    zr[0,1] = surface.vertices[3].z
    # Do a bilinear interpolation refinement
    for j in range(ny+1):
        for i in range(nx+1):
            di = i/float(nx)
            dj = j/float(ny)
            x = bilinearInterpolate(xr,0,0,di,dj)
            y = bilinearInterpolate(yr,0,0,di,dj)
            z = bilinearInterpolate(zr,0,0,di,dj)
            newVertices.append(Vertex(len(newVertices)+1,x,y,z))
    # Generate new surfaces
    for j in range(1,ny+1):
        for i in range(1,nx+1):
            p2 = (j*(nx+1))+i
            p3 = p2 - 1
            p0 = p3 - nx - 1
            p1 = p0 + 1
            # print(p0,p1,p2,p3,offset,len(newVertices))
            verts = [newVertices[i+offset] for i in [p0,p1,p2,p3]]
            newSurfaces.append(Surface(len(newSurfaces)+1,verts,
                                       name=surface.name
                                            + '_'+str(len(newSurfaces))))
    offset = len(newVertices)

# Write it all out
for vertex in newVertices:
    outfile.write(str(vertex)+'\n')
for surface in newSurfaces:
    outfile.write(str(surface)+'\n')
outfile.write('End of data\n')
outfile.close()

# Write out the stats
fperr.write('Summary of input file "%s":\n' % sys.argv[2])
fperr.write('  %d vertices\n' % stats['V'])
fperr.write('  %d surfaces\n' % (stats['S']+stats['M']+stats['N']+stats['O']))
fperr.write('    %d regular\n' % stats['S'])
fperr.write('    %d mask\n' % stats['M'])
fperr.write('    %d null\n' % stats['N'])
fperr.write('    %d obstructing\n' % stats['O'])

