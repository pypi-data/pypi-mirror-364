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
import re

from .io import colored, display
import os
    
"""PyFreeFEM parsing module"""

#: Enable or disable the parsing of double backslash ``\\``.   
ENABLE_LINE_BREAKS = True

MAGIC_CHARACTER = '$'
""" Prefix character for magic variables (by default ``$``)."""


class Preprocessor():
    """A class that parses FreeFEM ``.edp`` scripts with enhanced
    PyFreeFEM meta-language instructions (see :ref:`language`).
        
    The :class:`pyfreefem.preprocessor.Preprocessor` class is used by
    :class:`pyfreefem.FreeFemRunner` for parsing FreeFEM ``.edp`` scripts with enhanced
    preprocessing instructions and converting it into a proper, executable
    ``.edp`` code. The usage is similar to ``pyfreefem.FreeFemRunner``:
    
    .. code:: python
    
       from pyfreefem import Preprocessor
       # Parse a single file
       preproc=Preprocessor('solveState.edp')
    
       # Parse a list of files (to be assembled consecutively)
       preproc=Preprocessor(['params.edp','solveState.edp'])
    
       # Parse a single file with an updated configuration
        preproc=Preprocessor('solveState.edp',{'ITER':'0010'})
    
        # Parse raw code
       code = \"""DEFAULT (n,30)
       mesh Th=square($n,$n);
       preproc=Preprocessor(code)\"""
    
       # Then parse these files with `Preprocessor.parse':
       parsedCode=preproc.parse();
       parsedCode=preproc.parse({'n':'0001'});# Parse with a different configuration
    
    A configuration dictionary ``config`` containing the updated (or
    predefined) values of magic variables is assembled while parsing the
    ``.edp`` file.
        

    :param script:  single file name, list of
                    file names or raw ``.edp`` script

    :param config: (optional) a dictionary of magic variables with default values

    :param included: (optional) a list of file names that must not be
                included. Usually empty, used for implementation
                purposes.

    :param debug:  A tuning parameter for flexible verbose output, allowing to
                   check the behavior of the parsing.
    """
    ACTIONS = {'IF': '__execute_if',
               'ENDIF': '__execute_endif',
               'ELSE': '__execute_else',
               'IFEQ': '__execute_ifeq',
               'IFDEF': '__execute_ifdef',
               'FOR': '__execute_for',
               'ENDFOR': '__execute_endfor',
               'DEFAULT': '__execute_default',
               'SET':  '__execute_set',
               'DEBUG': '__execute_debug',
               'INCLUDE': '__execute_include',
               'SET_TEXTVAR': '__execute_set_textvar',
               'END_TEXTVAR': '__execute_end_textvar',
               'IMPORT':'__execute_import'}

    def __init__(self, script, config=dict(), included=set(), debug=0):
        self.code = []
        self.files = []
        self.debug = debug
        self.interpreted = ''
        self.state = []
        self.position = 0

        #: Dictionary of magic variables.   
        #: This dictionary is updated after calling :meth:`pyfreefem.preprocessor.Preprocessor.parse`.
        self.config = dict()
        self.stackFor = dict()
        self.imports = []
        if isinstance(script, str):
            self.files = [script]
        else:
            self.files = script
        self.initConfig = config
        for fileName in self.files:
            if len(fileName.splitlines())==1:
                display("Including "+fileName, 1, debug, 'green')
                try:
                    with open(fileName, "r") as f:
                        self.code = self.code+f.readlines()
                except:
                    display("Warning: it seems "+fileName+" is a file name "\
                            "however this file does not exist. Will treat as "\
                            "portion of code.",0,self.debug, "red")
                    self.code = self.code+[x+'\n' for x in fileName.splitlines()]
                    self.code[-1] = self.code[-1][:-1]  # Remove extra \n
            else:
                self.code = self.code+[x+'\n' for x in fileName.splitlines()]
                self.code[-1] = self.code[-1][:-1]  # Remove extra \n
        self.initialIncluded = set(included)

    def replace(self, string, config=None):
        """Replace a string containing magic variables with their values provided   
           by the ``config`` parameter.

           :param string: string to replace
           :param config: (default: None). The magic variables are replaced      
                          according to the values given by `config`
                          If not specified, config is set to be the attribute
                          :attr:`pyfreefem.preprocessor.Preprocessor.config`.
        """
        if config is None:
            config = self.config
        keys = list(config.keys())
        keys.sort(reverse=True)
        ret = string
        for key in keys:
            replacement = str(config[key])
            if os.name == 'nt':
                replacement = replacement.replace('\\','/')
            ret = ret.replace(MAGIC_CHARACTER+'{'+key+'}', replacement)
            ret = ret.replace(MAGIC_CHARACTER+key, replacement)
        return ret

    def parse(self, config=dict()):
        """Parse the ``.edp`` script provided to the :class:`pyfreefem.preprocessor.Preprocessor`   
        instance.
            
        :param config: a configuration for the magic variable that takes precedence over    
                       the default ``config`` value provided to the 
                       :class:`pyfreefem.preprocessor.Preprocessor` constructor. 

                       .. code:: python

                          preproc = Preprocessor('file.edp')
                          parsedCode=preproc.parse({'hmin':'0.002'})

        Once the :meth:`pyfreefem.preprocessor.Preprocessor.parse` has been called,  
        the parameter :attr:`pyfreefem.preprocessor.Preprocessor.config` is   
        updated.    
        """
        # Set the cursor at position 0 and initialize the configuration
        # with the values supplied at initialization
        self.position = 0
        self.interpreted = ''
        self.state = []
        self.imports = []
        self.stackFor = dict()
        self.config = dict(self.initConfig)
        self.config.update(config)
        self.included = set(self.initialIncluded)
        # Read each line of the file and interpret.
        # For each line, either we have an instruction, or some code that is
        #interpreted and store in self.interpreted
        while self.position < len(self.code):
            line = self.replace(self.code[self.position], config=self.stackFor)
            display(str(self.position)+" : "+line.strip(), 2, self.debug)
            instruction = line.split()
            if instruction != [] and instruction[0] in self.ACTIONS:
                exec(f"self._Preprocessor{self.ACTIONS[instruction[0]]}"
                     "(instruction)")
            else:
                self.__read_line()
                self.position = self.position+1
        if self.state != []:
            raise Exception("Parse error : the state stack is not empty.\n"
                            + self.state.__str__())
        # Remove magic comments
        self.interpreted = re.sub(r'(\n\s*\/\/\*\*.*)+\n',
                                  r'\n', self.interpreted)
        self.interpreted = re.sub(r'\/\/\*\*.*', '', self.interpreted)
        # Arrange line breaks with \\ characters
        if ENABLE_LINE_BREAKS:
            self.interpreted = re.sub(r'\\\\\n\s*', '', self.interpreted)
            self.interpreted = re.sub(r'\n\s*\\\\', '', self.interpreted)
        # Remove extra lines
        self.interpreted = re.sub(r'\n(\n)+\n', r'\n\n', self.interpreted)
        return self.interpreted

    def __read_line(self):
        """Read a line which is not a special instruction."""
        # Starts by checking if line must be added depending on whether
        # we are within a if or for loop, or text variable
        ignore = False
        try:
            if self.state[-1][1] == 'if' \
                    and self.state[-1][2] in {False, 'ignore'}:
                ignore = True
        except:
            pass
        try:
            if self.state[-1][1] == 'for' \
                    and self.state[-1][3] >= self.state[-1][4]:
                ignore = True
        except:
            pass
        try:
            if self.state[-1][1] == 'for' and self.state[-1][2] == 'ignore':
                ignore = True
        except:
            pass
        line = self.code[self.position]
        line = self.replace(line, config=self.stackFor)
        line = self.replace(line)
        try:
            if self.state[-1][1] == 'set_text_var':
                self.state[-1][3] += line
                ignore = True
        except:
            pass
        if not ignore:
            self.interpreted = self.interpreted+line
            if self.debug > 1:
                display(colored("Interpreted : ", "green") +
                      colored(line[:-1], "blue"),2,self.debug)

    def __execute_include(self, instruction):
        """Include file"""
        fileToInclude = self.replace(instruction[1][1:-1])
        if not fileToInclude in self.included:
            self.included.add(fileToInclude)
            t = Preprocessor(fileToInclude, self.config, self.included)
            t.debug = self.debug
            self.interpreted = self.interpreted+t.parse()
            self.config.update(t.config)
            # Avoid inclusion of already included files
            self.included = self.included.union(t.included)
        self.position = self.position+1

    def __execute_if(self, instruction):
        var = instruction[1]
        ignore = False
        try:
            if self.state[-1][1] == 'if' and not self.state[-1][2]:
                ignore = True
            if self.state[-1][2] == 'ignore':
                ignore = True
        except:
            pass
        if ignore:
            result = 'ignore'
        else:
            if var in self.config:
                result = True
                try:
                    if str(self.config[var]) == '0':
                        result = False
                except:
                    pass
            else:
                result = False
        self.state.append([self.position, 'if', result])
        self.position = self.position+1
        display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')

    def __execute_endif(self, instruction):
        if self.state[-1][1] != 'if':
            raise Exception("Parse error at line "+str(self.position))
        display("Closed : "+self.state[-1].__str__(), 1, self.debug, 'green')
        self.state.pop()
        self.position = self.position+1

    def __execute_else(self, instruction):
        ignore = False
        try:
            if self.state[-1][1] == 'if' and self.state[-1][2] == 'ignore':
                ignore = True
            if self.state[-1][1] == 'for' and self.state[-1][2] == 'ignore':
                ignore = True
        except:
            pass
        if not ignore:
            self.state[-1][2] = (not self.state[-1][2])
        self.position = self.position+1
        display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')

    def __execute_ifeq(self, instruction):
        instruction = " ".join(instruction)
        instruction = re.findall(
            r'\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+', instruction)
        for i in range(1, len(instruction), 2):
            instr = instruction[i]
            m = re.search(r'\(\s*(.+)\s*,\s*"(.+)"\s*\)', instr)
            if m:
                var = m.group(1)
                toCompare = m.group(2)
                result = var in self.config and str(
                    self.config[var]) == toCompare
                # Allow to test for variables
                result = result or var in self.stackFor and str(
                    self.stackFor[var]) == toCompare
            else:
                m = re.search(r'\(\s*(.+)\s*,\s*\[(.+)\]\s*\)', instr)
                var = m.group(1)
                toCompare = set([s[1:-1] for s in m.group(2).split(',')])
                result = var in self.config and str(
                    self.config[var]) in toCompare
            if result:
                break
        for i in range(2, len(instruction), 2):
            if not instruction[i] == 'OR':
                raise Exception(
                    "Parse error in IFEQ, for now only OR "
                    "is supported between statements.")
        try:
            if self.state[-1][1] == 'if' \
                    and self.state[-1][2] in {False, 'ignore'}:
                result = 'ignore'
            if self.state[-1][1] == 'for' \
                    and self.state[-1][2] == 'ignore':
                result = 'ignore'
        except:
            pass
        self.state.append([self.position, 'if', result])
        self.position = self.position+1
        display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')

    def __execute_ifdef(self, instruction):
        var = instruction[1]
        result = var in self.config
        try:
            if self.state[-1][1] == 'if' \
                    and self.state[-1][2] in {False, 'ignore'}:
                result = 'ignore'
            if self.state[-1][1] == 'for' \
                    and self.state[-1][2] == 'ignore':
                result = 'ignore'
        except:
            pass
        self.state.append([self.position, 'if', result])
        self.position = self.position+1
        display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')

    def __execute_for(self, instruction):
        ignoreFor = False
        try:
            if self.state[-1][1] == 'if' \
                    and self.state[-1][2] in {False, 'ignore'}:
                self.state.append([self.position, 'for', 'ignore'])
                ignoreFor = True
        except:
            pass
        if not ignoreFor:
            instr = instruction[1]
            m = re.search(r'\((.+),(.+),(.+),"(.+)"\)', instr)
            if not hasattr(m, 'group'):
                m = re.search(r'\((.+),(.+),(.+)\)', instr)
            try:
                start = int(m.group(2))
            except ValueError:
                start = int(self.config[m.group(2)])
            try:
                end = int(m.group(3))
            except ValueError:
                if m.group(3) in self.config:
                    end = int(self.config[m.group(3)])
                else:
                    end = 0
            if start >= end:
                self.state.append([self.position, 'for', 'ignore'])
            else:
                self.state.append(
                    [self.position, 'for', m.group(1), start, end])
                if m.lastindex == 4:
                    self.state[-1].append(m.group(4))
                else:
                    self.state[-1].append('')
            self.stackFor[m.group(1)] = start
            display("Assigned for variable : " +
                    m.group(1)+"="+str(start), 1, self.debug, 'green')
        self.position = self.position+1
        display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')

    def __execute_endfor(self, instruction):
        if self.state[-1][1] != 'for':
            raise Exception("Parse error at line "+self.position)
        if self.state[-1][2] == 'ignore':
            self.position = self.position+1
            self.state.pop()
        else:
            varFor = self.state[-1][2]
            if self.stackFor[varFor] >= self.state[-1][4]-1:
                self.stackFor.pop(varFor)
                self.state.pop()
                self.position = self.position+1
            else:
                self.interpreted = self.interpreted+self.state[-1][5]
                self.stackFor[varFor] = self.stackFor[varFor]+1
                display("Assigned for variable : "+varFor +
                        "="+str(self.stackFor[varFor]), 1, self.debug, 'green')
                self.position = self.state[-1][0]+1
        if self.debug > 0:
            try:
                display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')
            except:
                pass

    def __execute_default(self, instruction):
        try:
            if self.state[-1][1] == 'if' and self.state[-1][2] in {False,
                                                                   'ignore'}:
                self.position = self.position+1
                return
        except:
            pass
        instruction[1] = " ".join(instruction[1:])
        m = re.search(r'\((.+)\s*,\s*"(.+)"\)', instruction[1])
        try:
            key = m.group(1)
            value = m.group(2)
            if not key in self.config:
                value = self.replace(value)
                self.config[key] = value
        except:
            try:
                m = re.search(r'\((.+)\s*,\s*(.+)\)', instruction[1])
                key = m.group(1)
            except:
                raise Error("Error while parsing DEFAULT instruction")
            value = m.group(2)
            if not key in self.config:
                value = eval(self.replace(value))
                self.config[key] = value
        display("Defined "+key+"="+str(self.config[key]), 1, self.debug, 'green')
        self.position = self.position+1

    def __execute_set(self, instruction):
        try:
            if self.state[-1][1] == 'if' and self.state[-1][2] in {False,
                                                                   'ignore'}:
                self.position = self.position+1
                return
        except:
            pass
        instruction[1] = " ".join(instruction[1:])
        m = re.search(r'\(\s*(.+)\s*,\s*"(.+)"\s*\)', instruction[1])
        try:
            key = m.group(1)
            value = m.group(2)
            value = self.replace(value)
        except:
            try:
                m = re.search(r'\((.+)\s*,\s*(.+)\)', instruction[1])
                key = m.group(1)
            except:
                raise NameError("Error while parsing SET instruction")
            value = m.group(2)
            value = eval(self.replace(value))
        self.config[key] = value
        display("Defined "+key+"="+str(self.config[key]), 1, self.debug, 'green')
        self.position = self.position+1

    def __execute_set_textvar(self, instruction):
        try:
            if self.state[-1][1] == 'if' \
                    and self.state[-1][2] in {False, 'ignore'}:
                self.position = self.position+1
                return
        except:
            pass
        nameVar = instruction[1]
        self.state.append([self.position, 'set_text_var', nameVar, ''])
        self.position = self.position+1
        display("State : "+self.state[-1].__str__(), 1, self.debug, 'green')

    def __execute_end_textvar(self, instruction):
        try:
            if self.state[-1][1] == 'if' \
                    and self.state[-1][2] in {False, 'ignore'}:
                self.position = self.position+1
                return
        except:
            pass
        if self.state[-1][1] != 'set_text_var':
            raise Exception("Parse error at line "+str(self.position))
        display("Closed : "+self.state[-1].__str__(), 1, self.debug, 'green')
        state = self.state.pop()
        self.set({state[2]: state[3]})
        display("Set : "+state[2]+":\n"+state[3], 1, self.debug, 'green')
        self.position = self.position+1

    def __execute_debug(self, instruction):
        import ipdb;
        ipdb.set_trace();
        self.position = self.position + 1

    def __execute_import(self, instruction):
        macro_file = os.path.dirname(__file__)+"/edp/"+instruction[1][1:-1]
        self.imports.append(macro_file)
        if not os.path.exists(macro_file):
            raise NameError("Error while parsing IMPORT instruction: file \""+macro_file+"\" does not "
                        "exist")
        
        filename = instruction[1][1:-1]
        line = "include \""+self.config['RUNDIR']+"/"+filename+"\"\n"
        self.interpreted += line
        if self.debug > 1:
            display(colored("Interpreted : ", "green") +
                  colored(line[:-1], "blue"),2,self.debug)
        self.position += 1

        
    def set(self, assign):
        """Update the config dictionary 
            
        :param assign: New values for the dictionary :attr:`pyfreefem.preprocessor.Preprocessor.config`.
        :type assign: dict"""
        self.config.update(assign)
