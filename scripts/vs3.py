#
# VS3 File Objects
#
class Data(object):
    def __init__(self,stringData=False,**kwargs):
        self.controls = kwargs.get('controls',[])
        self.vertices = kwargs.get('vertices',[])
        self.surfaces = kwargs.get('surfaces',[])
        self.stringData = stringData
    @staticmethod
    def load(fp,stringData=False):
        lines = {'V':[],'S':[],'M':[],'N':[],'O':[],'C':[],'T':[],'F':[]}
        for line in fp:
            char = line.strip()[0]
            firstChar = char.upper()
            if firstChar in lines:  # Is this something we're looking for?
                lines[firstChar].append(line.strip())
            elif firstChar == '!':
                continue
            elif firstChar in ['E','*']: # End the loop if this is the end flag
                break
            else:   
                raise Exception('Unexpected data element "%s"' % firstChar)
        # Bail out if there are elements we don't handle yet
        if lines['M'] or lines['N'] or lines['O']:
            raise Exception('Unhandled data element (M, N, or O)')
        if stringData: # Keep everything as strings
            controls = lines['T'] + lines['C'] + lines['F']
            vertices = lines['V']
            surfaces = lines['S']
        return Data(controls=controls,vertices=vertices,
                    surfaces=surfaces, stringData=stringData)
    def nvertices(self):
        return len(self.vertices)
    def nsurfaces(self):
        return len(self.surfaces)
    def writeVS3(self,fp):
        if self.stringData:
            for line in self.controls:
                fp.write(line+'\n')
            for line in self.vertices:
                fp.write(line+'\n')
            for line in self.surfaces:
                fp.write(line+'\n')
            fp.write('End of data')
    def writeVTK(self,fp):
        # Write out the header of the file
        fp.write('# vtk DataFile Version 2.0\n')
        fp.write('Automatically created from VS3 input\n')
        fp.write('ASCII\nDATASET UNSTRUCTURED_GRID\n')
        # Write out the point data
        fp.write('POINTS %d double\n' % self.nvertices())
        if self.stringData:
            for line in self.vertices:
                pt = tuple(line.split()[2:])
                fp.write('%s %s %s\n'%pt)
        # Write out cell data (assume quads for now)
        fp.write('CELLS %d %d\n' % (self.nsurfaces(), 5*self.nsurfaces()))
        if self.stringData:
            for line in self.surfaces:
                cell = tuple(map(lambda x: int(x)-1, line.split()[2:6]))
                fp.write('4 %d %d %d %d\n'%cell)
        fp.write('CELL_TYPES %d\n'%self.nsurfaces())
        for line in self.surfaces:
            fp.write('9\n')
    def copy(self):
            return Data(controls=self.controls[:],
                        vertices=self.vertices[:],
                        surfaces=self.surfaces[:],
                        stringData=self.stringData)


