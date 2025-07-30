from pyfreefem import FreeFemRunner

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

# Small hack for running FreeFem++-nw instead of FreeFem++ command 
def cmd(self, *args, **kwargs):
    cmd = self.old_cmd(*args,**kwargs).split(" ")
    cmd[0] = "FreeFem++-nw"
    cmd = " ".join(cmd)
    return cmd

FreeFemRunner.old_cmd = FreeFemRunner.cmd
FreeFemRunner.cmd = cmd

FreeFemRunner(code,debug=1).execute({'message':'Hello world',\
                                       'SOLVE_LAPLACE':1},verbosity=0,\
                                      plot=False)
