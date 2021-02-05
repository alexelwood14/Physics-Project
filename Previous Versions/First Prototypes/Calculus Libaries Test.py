import sympy
from sympy import *
x, y, z = symbols('x y z')
init_printing (use_unicode=True)

numa = 15
numb = 12
numc = 2

print ('diff is:',diff(numa*(x)**numc+numb*(x),x))
print ('integral is:',integrate(15*(x)**2+12*(x),x))
