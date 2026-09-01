"""
Sistema de Tipos + Listas (Persona 2). Mixin vacio a proposito: no definir
visitXxx aqui hasta implementarlos, porque un `pass` taparia el recorrido
por defecto de CompiscriptVisitor.

Visita (ver docs/ARCHITECTURE.md):
  variableDeclaration, constantDeclaration, typeAnnotation / type / baseType,
  assignment, logicalOrExpr → unaryExpr, literalExpr, arrayLiteral, IndexExpr.

Expone: get_type(ctx) -> Type, resolve_type_annotation(ctx) -> Type.
Consume: self.table / self.helpers (Persona 1).
"""

from __future__ import annotations


class TypeMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
