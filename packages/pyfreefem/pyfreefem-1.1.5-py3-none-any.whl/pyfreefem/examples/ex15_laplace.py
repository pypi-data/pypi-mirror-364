from pyfreefem import FreeFemRunner
from pymedit import P1Function

exports = FreeFemRunner("edp/ex15.edp").execute({'N':40})
u = P1Function(exports['Th'],exports['u[]'])

u.plot(title="u")
