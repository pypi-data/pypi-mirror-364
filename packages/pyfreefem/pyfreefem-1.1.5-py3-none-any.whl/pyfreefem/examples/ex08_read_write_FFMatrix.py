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
from pyfreefem.io import readFFMatrix, writeFFMatrix
from pyfreefem import FreeFemRunner
import numpy as np
import scipy as sp

code = """
mesh Th=square(1,1);
fespace Fh(Th,P1);
varf laplace(u,v)=int2d(Th)(2*u*v+dx(u)*dx(v)+dy(u)*dy(v));
matrix A = laplace(Fh,Fh,tgv=-2);
{
    ofstream f("$RUNDIR/ex8_A.gp");
    f << A;
}
cout << "FreeFEM : saved matrix ex8_A.gp" << endl;
cout << A << endl;
"""
with FreeFemRunner(code,debug=10) as runner: 
    runner.execute(verbosity=0)    
    A = readFFMatrix(runner.run_dir+"/ex8_A.gp")
print("Python : read matrix ex8_A.gp")
print(A)

# Sparse identity matrix
I = sp.sparse.eye(5,5)
code = """
matrix I;
{
    ifstream f("$RUNDIR/ex8_I.gp");
    f >> I;
}
cout << "FreeFEM : read matrix ex8_I.gp" << endl;
cout << I << endl;
"""
with FreeFemRunner(code) as runner: 
    writeFFMatrix(I, runner.run_dir+"/ex8_I.gp")
    print(I,"\n")
    print(f"\nPython : saved matrix {runner.run_dir}/ex8_I.gp")
    runner.execute()
    rets = runner.rets
