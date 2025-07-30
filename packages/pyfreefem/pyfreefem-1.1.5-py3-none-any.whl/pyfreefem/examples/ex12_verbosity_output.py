# Copyright 2018-2020 CNRS, Ecole Polytechnique and Safran.
#
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
import sys
if len(sys.argv)==3 and sys.argv[1]=='--debug':
    debug = int(sys.argv[2])
else:
    debug = 0
from pyfreefem import FreeFemRunner
from pyfreefem.io import colored

code = """
mesh Th=square(30,30);
fespace Fh(Th,P1);
Fh u,v;

DEFAULT (SOLVE_LAPLACE,0)
cout << "The value of SOLVE_LAPLACE is $SOLVE_LAPLACE." << endl;
IF SOLVE_LAPLACE
solve laplace(u,v)=
    int2d(Th)(dx(u)*dx(v)+dy(u)*dy(v))
        -int2d(Th)(v)
        +on(1,2,3,4,u=0);
plot(u,cmm="$message");
ENDIF
"""

runner = FreeFemRunner(code,debug=debug)    
    
if __name__=='__main__':
    print(colored("Running with verbosity=1:",attr="bold"))
    runner.execute({'message':'Hello world',\
                    'SOLVE_LAPLACE':1},verbosity=1,\
                   plot=True)

    print(colored("\nRunning with verbosity=0:",attr="bold"))
    runner.execute({'message':'Hello world',\
                    'SOLVE_LAPLACE':1},verbosity=0,\
                   plot=False)

    print(colored("\nRunning with default verbosity (-1):",attr="bold"))
    runner.execute({'message':'Hello world',\
                    'SOLVE_LAPLACE':1},\
                   plot=False)
