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
from pyfreefem import FreeFemRunner
try:
    from pymedit import Mesh, P1Function
    WITH_PYMEDIT = True
    import matplotlib.pyplot as plt
    plt.ion()
except:
    WITH_PYMEDIT = False


import os
examples_folder = os.path.split(__file__)[0]

with FreeFemRunner(examples_folder+"/edp/ex9.edp") as runner:
    # FreeFemRunner will save files in a temporary directory
    # accessible in runner.script_folder (python) or $RUNDIR (in FreeFEM)
    # runner and The temporary directory is deleted outside the with context
    runner.execute({'n':40})
    if WITH_PYMEDIT:
        M = Mesh(runner.run_dir+"/Th.mesh")
        phi = P1Function(M,runner.run_dir+"/phi.sol")
    with open(runner.run_dir+"/result.gp","r") as f:
        result=float(f.readlines()[0].strip())


if __name__=="__main__":
    print("Result=",result)
    if WITH_PYMEDIT:
        M.plot(title="Mesh Th")
        phi.plot(title="P1Function f")
        input("Press any key to close the plots.")

    import matplotlib.pyplot as plt
    plt.close('all')
