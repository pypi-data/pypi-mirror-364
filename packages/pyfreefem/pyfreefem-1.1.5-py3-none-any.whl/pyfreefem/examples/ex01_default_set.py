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
from pyfreefem import Preprocessor

import os
examples_folder = os.path.split(__file__)[0]
preproc = Preprocessor(examples_folder+"/edp/ex1.edp")

parsed_default = preproc.parse()
config_default = preproc.config.copy()

print("config after default setting=",config_default)

print("Setting $Re=100 and $Pe=3:")
parsed_variant = preproc.parse({'Re':100,'Pe':3})
config_variant = preproc.config.copy()

print("config after setting=",config_variant)
