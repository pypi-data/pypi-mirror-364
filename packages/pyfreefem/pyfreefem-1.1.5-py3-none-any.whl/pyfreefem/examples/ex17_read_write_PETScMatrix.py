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
from pyfreefem.io import readPetscMat, writePetscMatrix
from pyfreefem import FreeFemRunner
import numpy as np
import scipy as sp
import scipy.sparse as spa

code = """
IMPORT "io.edp" 

mesh Th=square(3,3);
fespace Fh(Th,P1);
varf laplace(u,v)=int2d(Th)(2*u*v+dx(u)*dx(v)+dy(u)*dy(v));
matrix A = laplace(Fh,Fh,tgv=-2);
    
exportMatrix(A); 
    
Mat APetsc(A); 
ObjectView(APetsc, format = "binary", name = "matpetsc_A");
"""
    
exports = FreeFemRunner(code,debug=3).execute(with_mpi=1,verbosity=0)

APetsc = readPetscMat("matpetsc_A")
A = exports['A']
print(APetsc)
print(APetsc-A)
    
writePetscMatrix(A, "matpetsc_B")
code = """
IMPORT "io.edp" 

Mat APetsc; 
MatLoad(APetsc, format = "binary", name = "matpetsc_B");

ObjectView(APetsc,format="info"); 
ObjectView(APetsc, format = "binary", name = "matpetsc_C");
"""
FreeFemRunner(code,debug=3).execute(with_mpi=True,verbosity=0); 
CPetsc = readPetscMat("matpetsc_C")
print(APetsc-CPetsc)
