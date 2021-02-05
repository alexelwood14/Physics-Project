import sympy
from sympy import *
x, y, z = symbols('x y z')
init_printing (use_unicode=True)

drag = 5
mass = 2
time = 5

print ('integral is:',integrate((drag * x ** 2) / mass, (x, time - 1, time)))
