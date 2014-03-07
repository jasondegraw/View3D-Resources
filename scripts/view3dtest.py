#
# View3D testing script
#
import os.path

def promote(cls,data):
    objs = []
    for el in data:
        objs.append(cls(**el))
    return objs

class Case:
    def __init__(self,**kwargs):
        self.name = kwargs.get('name','unknown')
        self.path = kwargs.get('path','.')
        #self.path = os.path.join(*os.path.split(path))
    def __str__(self):
        return 'Case: ' + self.name

class ResultsError(Exception):
    pass

class View3DResults:
    def __init__(self,name,filename):
        self.name = name
        if not os.path.exists(filename):
            raise ResultsError('View3D results file "%s" not found'
                               %filename)
        fp = open(filename,'r')
        try:
            line1 = next(fp)
            line2 = next(fp)
        except StopIteration:
            raise ResultsError("View3D results file is incomplete")
        try:
            guido,self.version,self.out,encl,emit,N = line1.split()
        except ValueError as e:
            raise ResultsError('Failed to parse results line 1: ' + str(e))
        self.encl = False
        if encl == '1':
            self.encl = True
        self.emit = False
        if emit == '1':
            self.emit = True
        try:
            self.N = int(N)
        except ValueError as e:
            raise ResultsError('Noninteger number of surfaces: ' + N)
        areas = line2.split()
        if len(areas) != self.N:
            raise ResultsError('Wrong number of areas in results line 2: %d'
                               % len(areas))
        self.areas = list(map(float,areas))
        self.data = []
        try:
            for i in range(self.N):
                data = next(fp).split()
                if len(data) != self.N:
                    raise ResultsError('Insufficient data in line %d' %i)
                try:
                    self.data.append(list(map(float,data)))
                except ValueError:
                    raise ResultsError('Data line %d contains non-float data'
                                       %i)
        except StopIteration:
            raise ResultsError('Insufficient data in results file')
        try:
            lineNp1 = next(fp)
            emit = lineNp1.split()
            if len(emit) != self.N:
                raise ResultsError('Insufficient emittance data in esults file')
            self.emit = list(map(float,emit))
        except StopIteration:
            raise ResultsError('No emittance data in results file')
        except ValueError:
            raise ResultsError('Emittance line contains non-float data')
    def diff(self,other,output,eps=0.0):
        different = False
        if self.N != other.N:
            output.write('Data sets "%s" and "%s" have different surface counts\n'
                         %(self.name,other.name))
            output.write('Data sets "%s" and "%s" differ\n'
                         %(self.name,other.name))
            return True
        if self.encl != other.encl:
            different = True
            if self.encl:
                output.write('Data set "%s" is an enclosure and data set "%s" is not\n'
                             %(self.name,other.name))
            else:
                output.write('Data set "%s" is not an enclosure and data set "%s" is\n'
                             %(self.name,other.name))
        if self.emit != other.emit:
            different = True
            if self.emit:
                output.write('Data set "%s" uses emittances and data set "%s" does not\n'
                             %(self.name,other.name))
            else:
                output.write('Data set "%s" does not use emittances and data set "%s" does\n'
                             %(self.name,other.name))
        maxError = 0.0
        imax = 0
        jmax = 0
        v1 = -1.0
        v2 = -1.0
        for i in range(self.N):
            for j in range(self.N):
                error = abs(self.data[i][j] - other.data[i][j])
                if error > maxError:
                    imax = i
                    jmax = j
                    maxError = error
                    v1 = self.data[i][j]
                    v2 = other.data[i][j]
        if maxError > eps:
            different = True
            output.write('Maximum error in view factors (%d and %d): %g\n' % (i,j,maxError))
            output.write('                              (%f and %f): %g\n' % (v1,v2,maxError))
        if different:
            output.write('Data sets "%s" and "%s" differ\n'
                         %(self.name,other.name))
        return different

import sys

filename = '../examples/pinney-bean-test-4.vs3'
filename = '../examples/out.vf'

r1 = View3DResults('4.0.0',filename)

filename = '../examples/out32.vf'
r2 = View3DResults('3.2',filename)

r1.diff(r2,sys.stdout,1e-4)

versionInfo = [{'name':'3.2',
                'path':'C:\\EnergyPlusV8-0-0\\PreProcess\\ViewFactorCalculation\\View3D.exe'},
               {'name':'4.0.0 32 bit',
                'path':'..\\..\\View3D\\View3D32.exe'},
               {'name':'4.0.0 64 bit',
                'path':'..\\..\\View3D\\View3D64.exe'}]

caseInfo = [{'name':'Unit Cube',
             'path':'..\\examples\\cube.vs3'},
            {'name':'Pinney & Bean Test 4',
             'path':'..\\examples\\pinney-bean-test-4.vs3'},
            {'name':'Gunter Pueltz Test 1',
             'path':'..\\tests\\gunter1.vs3'},
            {'name':'Gunter Pueltz Test 1A',
             'path':'..\\tests\\gunter1a.vs3'},
            {'name':'Gunter Pueltz Test 1B',
             'path':'..\\tests\\gunter1b.vs3'},
            {'name':'Gunter Pueltz Test 2',
             'path':'..\\tests\\gunter2.vs3'},
            {'name':'Window/Door Case',
             'path':'..\\tests\\wdwdoor.vs3'},
            {'name':'Cone 20x416',
             'path':'..\\tests\\cone20x416.vs3'},
            {'name':'Cone 20x416 A',
             'path':'..\\tests\\cone20x416a.vs3'}]

# Promote the dictionaries into objects
versions = promote(Case,versionInfo)
cases = promote(Case,caseInfo)
N = len(versions)

for c,case in enumerate(cases):
    for i in range(N):
        syscall = '%s %s c%dv%d.vf' % (versions[i].path,
                                       case.path,c,i)
        # print(syscall+'\n')
        os.system(syscall)
    for i in range(N):
        ri = View3DResults(versions[i].name,'c%dv%d.vf'%(c,i))
        for j in range(i+1,N):
            sys.stdout.write('Case "%s": compare "%s" and "%s"\n'
                             % (case.name,versions[i].name,versions[j].name))
            rj = View3DResults(versions[j].name,'c%dv%d.vf'%(c,j))
            different = ri.diff(rj,sys.stdout,1e-4)
            sys.stdout.write('\n')
            
                
                

