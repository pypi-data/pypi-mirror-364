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
from pyfreefem.io import readFFMatrixBinary, writeFFMatrixBinary
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
matrix B = [[1,2,3],[4,5,6]]; 
    
exportMatrix(A); 
exportMatrix(B); 
    
savemtx("A.mtx",A,true); 
savemtx("B.mtx",B,true); 
"""
    
exports = FreeFemRunner(code,debug=3).execute(with_mpi=1,verbosity=0)

import numpy as np
import struct
from scipy.sparse import coo_matrix

A = readFFMatrixBinary("A.mtx")
B = readFFMatrixBinary("B.mtx")
writeFFMatrixBinary(A,"A.mtx")
writeFFMatrixBinary(B,"B.mtx")

code = """
IMPORT "io.edp" 

matrix A, B; 
readmtx("A.mtx",A,true); 
readmtx("B.mtx",B,true); 
    
exportMatrix(A); 
exportMatrix(B); 
"""

exports = FreeFemRunner(code,debug=3).execute(with_mpi=1,verbosity=0)
print("A-exports['A']=",A-exports['A'])
print("exports['B']=",exports['B'].todense())
    

# Exemple d'utilisation
# matrix = read_mtx_binary("matrix.mtx")
# print(matrix)
