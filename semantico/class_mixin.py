"""
Clases y Objetos (Persona 4). Mixin vacio a proposito: no definir visitXxx
aqui hasta implementarlos.

Visita (ver docs/ARCHITECTURE.md):
  classDeclaration / classMember, NewExpr, ThisExpr, PropertyAccessExpr.

Consume: self.table (P1), self.get_type (P2), self.check_call_args (P3).
Pila ya inicializada por ScopeMixin: current_class.
"""

from __future__ import annotations


class ClassMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
