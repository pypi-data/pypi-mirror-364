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
    

"""Module FreeFemRunner"""

from os import path
from .preprocessor import Preprocessor
import os.path
import shutil
from .io import display, exec2, ExecException, readFFMatrix, readFFArray, writeFF2DArray,   \
                   writeFFArray, writeFFMatrix, make_dictionary, readFF2DArray, writeFFMatrixBinary, \
                   readFFMatrixBinary, tic, toc
import tempfile
import numpy as np
import scipy.sparse as sp
import pymedit
import inspect
    

WITH_BFSTREAM = 1

class FreeFemRunner:
    """A class to run a FreeFem ``.edp`` scripts    
    supporting PyFreeFEM meta-language.   

    **Usage**

    * Load a single file .edp file
        
      .. code:: python    

         runner=FreeFemRunner('solveState.edp')
    

    * Load a list of files (to be assembled consecutively)


      .. code:: python    

         runner=FreeFemRunner(['params.edp','solveState.edp'])  


    * Load a single file with an updated configuration


      .. code:: python    

         runner=FreeFemRunner('solveState.edp',{'ITER':'0010'}) 


    * Load raw code


      .. code:: python    

         code = "mesh Th=square(10,10);"
         runner=FreeFemRunner(code) 


    * Load a pyfreefem.Preprocessor object


      .. code:: python    

         preproc = Preprocessor('solveState.edp')
         runner = FreeFemRunner(preproc)


    Then execute the code with :meth:`pyfreefem.FreeFemRunner.execute`:

    .. code:: python    

       runner.execute();
       runner.execute({'Re':30}); # Update magic variable value


    :parameter script:    Either:   

                          * raw FreeFEM code   (e.g. ``script="mesh Th=square(3,3)"``) 

                          * name of ``.edp`` script file (e.g. ``script="script.edp"``) 

                          * list of names of ``.edp`` script files to be appended   
                            in the generated executable ``.edp`` script     
                            (e.g. ``script=['script1.edp','script2.edp','script3.edp']``)

                          * instance of :mod:`pyfreefem.preprocessor.Preprocessor`

    :parameter config:  a default assignment of magic variables
                        which can be modified later on during the execute() 
                        operation.  
                            
                        Example: ```{'N':10, 'RES':'high'}```.  
                            
                        .. note::   
                            
                           The values of the magic variables are converted to   
                           strings in the interpreted executable ``.edp`` script.   

    :type config:      dict

    :parameter run_dir:    running directory where the executable script is written    
                          when calling :meth:`pyfreefem.FreeFemRunner.execute`.   
                          If ``run_dir`` is ``None``, then a temporary directory     
                          is created for this purpose and deleted after execution.     
                          The temporary name directory can be retrieved by using the   
                          ``run_dir`` attribute of the :class:`pyfreefem.FreeFemRunner`    
                          instance or from the ``$RUNDIR`` magic variable.

    :parameter run_file:   Name of the generated executable ``.edp`` script. If   
                          ``run_file`` is ``None``, then ``run_file`` is set to: 
                             
                          * ``run_file=script`` if ``script`` is the name of a file 

                          * ``run_file=script[0]`` if ``script`` is a list and   
                            ``script[0]`` is the name of a file 
                             
                          * ``run.edp`` if none of the previous case applies.

    :parameter debug:       More and more debugging information with a flexible level of verbosity    
                        are displayed as this parameter is set to a larger and larger value.
                        Details of the parsing operation are displayed if 
                        ``debug>=10`` (default ``debug=0``).
    :type debug:        int

    :parameter plot: (default: ``False``). enables  
                      ``FreeFem++`` graphics (``-wg`` option) which are disabled 
                      by default.

    :parameter macro_files: List of enhanced .edp macro files
                            supporting meta-instructions
                            which are also parsed and placed in the 
                            run folder of the final executable. For instance:   
                                
                            .. code:: python    
                                
                               FreeFemRunner('script.edp',macro_files=['macros.edp','params.edp'])

    """
    
    def __init__(self, script, config=dict(), run_dir=None,
                 run_file=None, debug=0,  plot=False,
                 macro_files=None):
        """
        """
        self.freefemFiles = dict()
        self.debug = int(debug)
        self.run_file = run_file
        self.run_time = -1
        self.exports = []
        self.plot = plot

        #: Captured output of FreeFem++ process.   
        #: After calling :meth:`pyfreefem.FreeFemRunner.execute`,
        #: `rets` is a tuple    
        #: containing:  
        #:  
        #: * rets[0]: the return code   
        #: * rets[1]: stdout    
        #: * rets[2]: stderr    
        #: * rets[3]: the whole standard output (mix of stdout and stderr)
        self.rets = tuple() 

        # create temporary directory if needed
        self.__context__ = False

        if run_dir is None:
            self.tempdir = tempfile.TemporaryDirectory(prefix="pyfreefem_")
            self.run_dir = self.tempdir.name
        else:   
            self.run_dir = str(run_dir)

        if not os.path.exists(self.run_dir):
            os.makedirs(self.run_dir)
            display("Create "+self.run_dir, level=10, debug=self.debug,
                    color="magenta")
        self.ffexport_dir = self.run_dir+'/ffexport'
        self.ffimport_dir = self.run_dir+'/ffimport'

        if os.name == 'nt':
            # If windows, do not use backslashes for directory
            self.run_dir = self.run_dir.replace('\\','/')
            self.ffexport_dir = self.ffexport_dir.replace('\\','/')
            self.ffimport_dir = self.ffimport_dir.replace('\\','/')

        if isinstance(script, Preprocessor):
            self.preprocessor = script
        else:
            self.preprocessor = Preprocessor(script, config, debug=self.debug-10)
                
        #: Dictionary of magic variables.   
        #: This dictionary is updated after calling :meth:`pyfreefem.FreeFemRunner.execute`.
        self.config = config


        if self.run_file is None:
            if isinstance(script,list) and os.path.isfile(script[0]):
                self.run_file = os.path.basename(script[0])
            elif os.path.isfile(script):
                self.run_file = os.path.basename(script)
            else:
                self.run_file = "run.edp"

        if macro_files is None:     
            macro_files = []
        self.macro_files = macro_files
        self.macro_files.append(os.path.dirname(__file__)+"/edp/io.edp")
        
    def import_variables(self, *args, **kwargs):
        """Import variables making them accessible from FreeFEM script  
            
        :parameter args: variables directly entered. They will be accessible in FreeFEM     
                         through the same name.     
                            
                         .. code:: python   
                                
                            runner.import_variables(x,M);   
                                
                         .. code:: freefem  
                            
                            IMPORT "io.edp"     
                            real x=importVar("x");    
                            matrix M=importMatrix("M");     

        :parameter kwargs: provide the variables in the form of a dictionary.   
                           In that case, the variable bear the names corresponding to the   
                           keys of the dictionary. 
                            
                         .. code:: python   
                                
                            runner.import_variables(x=x1,mat=M);   
                                
                         .. code:: freefem  
                            
                            IMPORT "io.edp"     
                            real x=importVar("x");    // The content of x1
                            matrix M=importMatrix("mat"); // The content of M
        """
        frame = inspect.currentframe().f_back  # Get the caller's frame
        names = {id(v): k for k, v in frame.f_locals.items()}  # Map object ids to variable names
        extra_vars = {names.get(id(arg), f'unknown_{i}'): arg for i, arg in enumerate(args)}
        kwargs.update(extra_vars)
        # Clean the ffimport dir 
        #if os.path.exists(self.ffimport_dir):
        #    shutil.rmtree(self.ffimport_dir, ignore_errors=True)
        os.makedirs(self.ffimport_dir, exist_ok=True)
        display("Prepare directory "+self.ffimport_dir, level=10, debug=self.debug, 
                color="magenta")
        tic()
        # Import python variables to FreeFEM
        for varname, var in kwargs.items():
            if isinstance(var,float) or isinstance(var,int):   
                with open(self.ffimport_dir+"/var_"+varname,"w") as f:  
                    f.write(str(var)+"\n")
            elif isinstance(var,np.ndarray) and len(var.shape)==1:        
                writeFFArray(var, self.ffimport_dir+"/array_"+varname, binary=True)
            elif isinstance(var,np.ndarray):    
                writeFF2DArray(var, self.ffimport_dir+"/2darray_"+varname)
            elif sp.issparse(var):    
                writeFFMatrixBinary(var, self.ffimport_dir+"/matrix_"+varname)
            elif isinstance(var,pymedit.mesh.Mesh):
                var.save(self.ffimport_dir+"/mesh_"+varname+".mesh")
            elif isinstance(var,pymedit.mesh3D.Mesh3D):
                var.save(self.ffimport_dir+"/mesh3D_"+varname+".meshb")
            else:   
                raise Exception("Error, type "+str(type(var)) + " is unknown for pyfreefem import." 
                                " Supported types are float, np.ndarray, pymedit.mesh.Mesh and "    
                                "pymedit.mesh3D.Mesh3D.")
        display("Imported files in "+toc(),level=3,debug=self.debug, color="orange_4a")

    def parse(self, config):    
        """Returns the parsed executable ``.edp`` script without executing it.

           :parameter config:  a default assignment of magic variables
                               which can be modified later on during the execute() 
                               operation.  
                                   
                               Example: ```{'N':10, 'RES':'high'}```.  
                                   
                               .. note::   
                                   
                                  The values of the magic variables are converted to   
                                  strings in the interpreted executable ``.edp`` script.   
            :return: a parsed ``.edp`` script.  For instance:   
                
                     .. code:: python   
                        
                        script="mesh Th=square($N,$N);" 
                        FreeFemRunner(script).parse({'N':10})
                            
                     .. code:: freefem 
                        
                        mesh Th=square(10,10);
                
          
        """
        return self.preprocessor.parse(config)

    def _write_edp_file(self, config=dict()):
        """
        Write the parsed .edp file in the running directory.

        Arguments
        ---------

            config      : a dictionary of magic variable which updates the 
                          default FreeFemRunner.config assignment.
        """
        target_file = path.join(self.run_dir, self.run_file)

        code = self.parse(config)
        
        f = open(target_file, "w")
        f.write(code)
        f.close()
        display("Write "+target_file, level=10, debug=self.debug,
                color="magenta")

        if self.preprocessor.imports:
            self.macro_files += self.preprocessor.imports

        if self.macro_files:
            for mf in self.macro_files:
                file_name = os.path.split(mf)[1]
                with open(self.run_dir+"/"+file_name, "w") as f:
                    f.write(Preprocessor(mf, self.config, debug=self.debug-10).parse(config))
        return target_file

    def __enter__(self):
        if not os.path.exists(self.run_dir):
            os.makedirs(self.run_dir)
            display("Create "+self.run_dir, level=10, debug=self.debug,
                    color="magenta")
        return self

    def __exit__(self, type, value, traceback):
        pass
            

    def execute(self, config=dict(), debug = None, verbosity = -1,  
                ncpu = 1, with_mpi = False, plot = None, level = 1, 
                extra_args="", import_variables=None):
        """
        Parse the script with the input config, save the code in an ``.edp`` file
        and execute FreeFEM on it.

        .. code:: python

            runner = FreeFemRunner('solveState.edp')
            runner.execute();
            runner.execute({"ITER" : "0024"});

        :parameter config: Dictionary of magic variable values. This    
                           parameter takes precedence over the default configuration    
                           specified in the :class:`pyfreefem.FreeFemRunner` constructor.
                            
                           .. warning::

                              A "SET" instruction in the .edp file
                              always has the precedence over the values specified
                              by `config`. See :ref:`set`.

        :type config: dict

        :parameter debug:  debugging parameter which takes precedence over the default value    
                           specified in the  :class:`pyfreefem.FreeFemRunner` constructor.  
        :type debug:   int

        :parameter verbosity: (default ``-1``). If ``verbosity`` is set to a value    
                              ``0`` or greater, the standard output of the ``FreeFem++``    
                              command will be displayed during execution with the   
                              level of verbosity corresponding to the option ``-v verbosity``.  
                              No display is shown if ``verbosity<0``.   

        :type verbosity: int

        :parameter ncpu: number of compute nodes to be used (option ``-np`` of ``ff-mpirun``). 
        :type ncpu: int

        :parameter with_mpi: execute the interpreted ``.edp`` script with ``ff-mpirun``.

                              .. code:: python    

                                 # Run on 4 cpus with ff-mpirun -np 4
                                 runner.execute(ncpu=4); 
                                 # Run on 1 cpu with ff-mpirun -np 1
                                 runner.execute(ncpu=1,with_mpi=1);

                              Note that in that case, a magic variable ``WITH_MPI`` is automatically
                              assigned and set to 1, which is useful to make adaptations in the 
                              source code, e.g. 
                                    
                              .. code:: freefem

                                 IF WITH_MPI
                                 /* Instructions to do if the code is parallel */
                                 ELSE
                                 /* Instructions to do if the code is not parallel */
                                 int mpirank = 0; 
                                 int mpisize = 1;
                                 ENDIF

        :type with_mpi: boolean
            
        :parameter plot: Enables or disables  ``FreeFem++`` graphics (``-wg`` option) which are disabled 
                         by default.    This parameter takes precedence over    
                         the ``plot`` parameter of the  
                         :class:`pyfreefem.FreeFemRunner` constructor.

        :type plot: boolean

        :parameter level: set a custom level for PyFreeFEM debugging informations.  
                          Namely, the executed ``FreeFem++`` command and further    
                          PyFreeFEM operations will be shown if ``debug>=level``.
                    
        :parameter extra_args: (default: empty). Extra arguments to pass to FreeFEM command (for instance, ``-log_view``)

        :return exports:    a dictionary containing FreeFEM exported variables. 
                            See :ref:`export`.
        :rtype: dict: 
        """
        if import_variables:    
            self.import_variables(**import_variables)
        selfdebug = self.debug 
        debug = self.debug if debug is None else debug  
        self.debug = debug
        plot = self.plot if plot is None else plot

        config.update({'RUNDIR':self.run_dir})
        config.update({'FFEXPORTDIR':self.ffexport_dir})
        config.update({'FFIMPORTDIR':self.ffimport_dir})

        config.update({'DEBUG':debug})
        if ncpu > 1 or with_mpi:
            config.update({'WITH_MPI': 1})
        else:
            config.update({'WITH_MPI': 0})
        config.update({'BFSTREAM':WITH_BFSTREAM})
        self.config.update(config)
        target_file = self._write_edp_file(config)
        silent = verbosity < 0
        if silent:
            verbosity = min(verbosity,-1)

        self.exports = dict()
        if not os.path.exists(self.run_dir):
            os.makedirs(self.run_dir)

        # Clean the ffexport_dir 
        if os.path.exists(self.ffexport_dir):
            shutil.rmtree(self.ffexport_dir, ignore_errors=True)
        os.makedirs(self.ffexport_dir)
        display("Reset directory "+self.ffexport_dir, level=10, debug=self.debug, 
                color="magenta")


        try:
            returncode, stdout, stderr, mix = \
                exec2(self.cmd(target_file, ncpu=ncpu, verbosity= verbosity, with_mpi=with_mpi,
                               plot=plot,extra_args=extra_args),
                       debug=debug, level=level, silent=silent)
        except ExecException as e:
            if verbosity > -10:
                display(e.args[0], level = 0, debug = 0)
                display('\n'.join(e.mix.splitlines()[-40:]), level=0, debug=0)
            e.args = []
            raise e

        exportfiles = os.listdir(self.ffexport_dir)
        tic()
        for file in exportfiles:
            if file.startswith('mesh_') and not file.endswith('.gmsh'):
                from pymedit import Mesh
                self.exports[file[5:-5]] = Mesh(self.ffexport_dir+"/"+file) 
            if file.startswith('mesh3D_') and not file.endswith('.gmsh'):
                from pymedit import Mesh3D
                self.exports[file[7:-5]] = Mesh3D(self.ffexport_dir+"/"+file) 
            if file.startswith('var_'): 
                with open(self.ffexport_dir+'/'+file) as f:
                    self.exports[file[4:]] = float(f.read())
            if file.startswith('array_'):
                self.exports[file[6:]] = readFFArray(self.ffexport_dir+'/'+file, binary=True)
            if file.startswith('arrayInt_'):
                self.exports[file[9:]] = readFFArray(self.ffexport_dir+'/'+file, binary=True).astype(int)
            if file.startswith('matrix_'):
                self.exports[file[7:]] = readFFMatrixBinary(self.ffexport_dir+'/'+file)
            if file.startswith('2darray_'):
                self.exports[file[8:]] = readFF2DArray(self.ffexport_dir+'/'+file)
        display("Exported files in "+toc(),level=3,debug=self.debug,color="orange_4a")

        self.debug = selfdebug 

        self.rets =(returncode, stdout, stderr, mix)
        return self.exports


    def cmd(self, target_file, ncpu=1, with_mpi=False, verbosity = None, plot=False, extra_args=""):
        """Returns the shell command that is to be run when calling the method :meth:`pyfreefem.FreeFemRunner.execute`.  
            
        :parameter target_file: name of the final executable file.  

        :parameter with_mpi: (default: ``False``). If set to ``True``, then     
                             :meth:`pyfreefem.FreeFemRunner.execute` will call ``ff-mpirun``.

        :type with_mpi: boolean

        :parameter ncpu: number of compute nodes to be used (option ``-np`` of ``ff-mpirun``). 

        :parameter verbosity: option '-v` of FreeFEM. This option is not specified if   
                              ``verbosity`` is ``None``.

        :parameter plot: (default: ``False``). If set to ``True``, then     
                         :meth:`pyfreefem.FreeFemRunner.execute` will use the   
                         ``-wg`` option (with graphics). Otherwise,     
                         FreeFem will be called with ``-nw`` option.

        :parameter extra_args: (default: empty). Extra arguments to pass to FreeFEM command (for instance, ``-log_view``)

        :type plot: boolean
            
        :returns: Shell command for executing FreeFEM with ``target_file`` input 
                  script.
        """
        if ncpu > 1 or with_mpi:    
            cmd = f"ff-mpirun -np {ncpu}"
        else:
            cmd = "FreeFem++"
        cmd += " " + target_file
        if not verbosity is None:
            cmd = cmd+" -v "+str(int(verbosity))
        if plot:    
            cmd = cmd+" -wg"
        elif not with_mpi:
            cmd += " -nw"
        if extra_args:  
            cmd += " "+extra_args
        return cmd

# Initialisation of bfstream
code = r"""
load "bfstream"
func int save2DArray(string fileName, real[int,int] &value){
	ofstream file(fileName,binary);
    file.write(value); 
}
"""
runner = FreeFemRunner(code)
try:
    runner.execute(verbosity=-11)
except ExecException:
    WITH_BFSTREAM = 0

