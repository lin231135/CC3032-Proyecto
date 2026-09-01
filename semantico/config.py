"""
Banderas de configuracion para decisiones congeladas del plan
(docs/PLAN_IMPLEMENTACION.md §2) que conviene poder invertir en un segundo,
por ejemplo durante la defensa.
"""

# DEC-5: el enunciado dice que la condicion del switch debe ser boolean, pero
# docs/Especificaciones.md usa switch(x) { case 1: ... } con x: integer. Se
# implementa lo de Especificaciones: la expresion del switch puede ser de
# cualquier tipo y cada case debe ser del mismo tipo que ella. En False para
# que quede exactamente como en Especificaciones.md; cambiar a True exige
# ademas que la expresion del switch sea boolean.
SWITCH_EXIGE_BOOLEAN = False
