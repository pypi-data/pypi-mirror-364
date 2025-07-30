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
from pyfreefem.io import readFFArray, writeFFArray
from pyfreefem import FreeFemRunner
import numpy as np

code = """
real[int] table = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
{
    ofstream f("$RUNDIR/ex7_x.gp");
    f << table;
}
cout << "FreeFEM : saved ex7_x.gp" << endl;
cout << table << endl;
"""
with FreeFemRunner(code) as runner: 
    runner.execute(verbosity=0)
    x = readFFArray(runner.run_dir+"/ex7_x.gp")

print(f"Python : read ex7_x.gp \nnumpy array x={x}")
x2 = np.flip(x,0)

code = """
int n;
{
    ifstream f("$RUNDIR/ex7_x2.gp");
    f >> n;
}
real[int] table(n);
{ 
    ifstream f("$RUNDIR/ex7_x2.gp");
    f >> table;
}
cout << "FreeFEM : read ex7_x2.gp " << endl << table << endl;
"""
with FreeFemRunner(code) as runner: 
    writeFFArray(x2, runner.run_dir+"/ex7_x2.gp")
    print(f"Python : saved ex7_x2.gp \nnumpy array x2={x2}")
    runner.execute(verbosity=0)
    rets = runner.rets
