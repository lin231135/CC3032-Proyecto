# Mixins del analizador semantico (uno por persona), combinados en
# semantico/visitor.py:
#   - scope_mixin.py      -> Persona 1 (tabla de simbolos; estado compartido)
#   - type_mixin.py       -> Persona 2 (tipos, listas)
#   - function_mixin.py   -> Persona 3 (funciones, control de flujo, block)
#   - class_mixin.py      -> Persona 4 (clases y objetos)
#
# Ver docs/ARCHITECTURE.md para el detalle de que regla del grammar
# (visitXxx) le toca a cada quien.

from semantico.visitor import SemanticVisitor

__all__ = ["SemanticVisitor"]
