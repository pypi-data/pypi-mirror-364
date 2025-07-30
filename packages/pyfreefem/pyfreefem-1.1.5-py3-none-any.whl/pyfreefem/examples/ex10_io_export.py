# This file is part of PyFreeFEM.
#
# PyFreeFEM is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# PyFreeFEM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# A copy of the GNU General Public License is included below.
# For further information, see <http://www.gnu.org/licenses/>.
from pyfreefem import FreeFemRunner, extract
try:
    import pymedit  
    WITH_PYMEDIT = True
except:
    WITH_PYMEDIT = False

code = """
IMPORT "io.edp"

real var = pi;
real[int] arr = [1,2,3,4];

mesh Th = square(10,10);
fespace Fh1(Th,P1);

macro grad(u) [dx(u),dy(u)]//
varf laplace(u,v) = int2d(Th)(u*v+grad(u)'*grad(v));
varf rhs(u,v) = int1d(Th,1)(v);

matrix A = laplace(Fh1,Fh1);
real[int] f= rhs(0,Fh1);

real[int] u=A^-1*f;
    
IF BFSTREAM
real[int,int] B = [[1,2,3],[4,5,6]]; 
ENDIF


dispVar(var);
exportVar(var);
IF BFSTREAM
export2DArray(B); 
ENDIF

IF PYMEDIT
exportMesh(Th);
ENDIF   

exportArray(arr);
exportArray(f);
exportArray(u);
exportMatrix(A);
"""

config = dict(PYMEDIT=int(WITH_PYMEDIT))
exports = FreeFemRunner(code,run_dir="run").execute(config=config,verbosity=1)

if __name__=="__main__":
    print('var='+str(exports['var']))
    print('arr='+str(exports['arr']))
    print('A=',exports['A'])
    from pyfreefem import freefemrunner
    if freefemrunner.WITH_BFSTREAM:
        print('B=',exports['B'])
    print('f=',exports['f'])
    if WITH_PYMEDIT:
        import matplotlib.pyplot as plt
        plt.ion()
        exports['Th'].plot()

        from pymedit import P1Function
        Th = exports['Th']
        u = P1Function(Th, exports['u'])
        u.plot(title="u")
        input("Press any key")




