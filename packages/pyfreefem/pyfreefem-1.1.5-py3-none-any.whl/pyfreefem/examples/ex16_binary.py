import numpy as np
from pyfreefem import FreeFemRunner, get_root, tic, toc, freefemrunner
from pyfreefem.io import display
    
if not freefemrunner.WITH_BFSTREAM: 
    print("This examples demonstrates binary exports/import"
          " of real[int,int] arrays. Please install the fork repository "
          "from https://github.com/ffeppon/FreeFem-sources/tree/develop")
    import sys
    sys.exit(0)

tic()   
np.random.seed(42)
big_matrix = np.random.rand(31758,397)
display("Generate matrix took "+toc()) 
    
code = r""" 
IMPORT "io.edp"  
        
tic; 
real[int,int] m = import2DArray("big_matrix"); 
disp("Import took "+toc); 
    
tic; 
export2DArray(m); 
disp("Export took "+toc); 
"""
runner = FreeFemRunner(code,run_dir="run",debug=2) 
tic()
exports = runner.import_variables(big_matrix)
display("Import took "+toc()) 
#
#    
tic()
exports = runner.execute(verbosity=0)
display("Execute took "+toc()) 
    
print("Big matrix = "+str(big_matrix))
print("FreeFEM = "+str(exports['m']))
