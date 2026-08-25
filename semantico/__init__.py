# Mixins del analizador semantico (uno por persona), combinados en
# semantico/visitor.py:
#   - scope_mixin.py      -> Persona 1 / Persona 3 (ambito)
#   - type_mixin.py       -> Persona 2 (tipos, listas)
#   - function_mixin.py   -> Persona 3 (funciones, control de flujo)
#   - class_mixin.py      -> Persona 4 (clases y objetos)
#
# Ver docs/ARCHITECTURE.md para el detalle de que regla del grammar
# (visitXxx) le toca a cada quien.
