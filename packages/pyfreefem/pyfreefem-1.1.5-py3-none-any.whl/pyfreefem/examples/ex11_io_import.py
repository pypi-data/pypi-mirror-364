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
from pyfreefem import FreeFemRunner, freefemrunner

import numpy as np
from pymedit import square
import scipy.sparse as sp
    
x = np.pi   
arr = np.asarray([1,2,3])
if freefemrunner.WITH_BFSTREAM:
    B = np.asarray([[1,2,3],[4,5,6]])
Th = square(10,10)
A = sp.diags([1,2,3,4])

code = """
IMPORT "io.edp"

mesh Th=importMesh("Th");
plot(Th,cmm="Th");

real x = importVar("x");
dispVar(x);

real[int] arr = importArray("arr"); 
dispArray(arr);

matrix A = importMatrix("A");
dispMatrix(A);
    
IF BFSTREAM
real[int,int] B = import2DArray("B"); 
disp2DArray(B); 
ENDIF
"""

runner = FreeFemRunner(code) 
    
runner.import_variables(x, arr, Th, A)
if freefemrunner.WITH_BFSTREAM:
    runner.import_variables(B)
runner.execute(verbosity=0, plot=True)
    
result = runner.rets[1]




