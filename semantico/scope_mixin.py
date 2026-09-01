"""
Estado compartido de la tabla de simbolos (Persona 1).

Los mixins de P2/P3/P4 heredan estos atributos a traves de SemanticVisitor.
No definan visitXxx aqui: Persona 3 es duena de `visitBlock` (crear scope
+ codigo muerto); Persona 2 declara simbolos con `define_or_error` al
visitar declaraciones.

Si un mixin posterior define `__init__`, DEBE llamar
`super().__init__(*args, **kwargs)` para no romper el MRO.
"""

from __future__ import annotations

from core.errors import ErrorReporter
from core.symbols import Scope, ScopeHelpers, ScopeKind, Symbol, SymbolTable
from core.types import ClassType, Type


class ScopeMixin:
    """Infraestructura de ambitos. Disponible en el visitor combinado como `self`."""

    table: SymbolTable
    reporter: ErrorReporter
    helpers: ScopeHelpers
    function_stack: list[tuple[str, Type]]
    loop_depth: int
    current_class: ClassType | None

    def __init__(self, *args, reporter: ErrorReporter | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.reporter = reporter or ErrorReporter()
        self.table = SymbolTable()
        self.helpers = ScopeHelpers(table=self.table, reporter=self.reporter)
        # P3: (nombre_funcion, tipo_de_retorno_declarado)
        self.function_stack = []
        self.loop_depth = 0
        # P4: clase que se esta visitando (para `this` y miembros heredados)
        self.current_class = None

    def enter_scope(self, kind: ScopeKind) -> Scope:
        return self.table.enter_scope(kind)

    def exit_scope(self) -> None:
        self.table.exit_scope()

    def require_declared(self, name: str, ctx) -> Symbol | None:
        return self.helpers.require_declared(name, ctx)

    def define_or_error(self, symbol: Symbol, ctx) -> bool:
        return self.helpers.define_or_error(symbol, ctx)
