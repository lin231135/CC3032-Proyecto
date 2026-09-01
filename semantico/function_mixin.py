"""
Ambito + Funciones + Control de Flujo (Persona 3). Mixin vacio a proposito:
no definir visitXxx aqui hasta implementarlos.

Visita (ver docs/ARCHITECTURE.md):
  block, IdentifierExpr, functionDeclaration / parameters / parameter,
  if/while/doWhile/for/foreach/switch, break/continue/return, CallExpr,
  tryCatchStatement.

Expone: check_call_args(func_type, args_ctx).
Consume: self.table (P1), self.get_type (P2).
Pilas ya inicializadas por ScopeMixin: function_stack, loop_depth.
"""

from __future__ import annotations


class FunctionMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
