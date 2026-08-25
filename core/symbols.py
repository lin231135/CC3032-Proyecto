"""
Tabla de Simbolos (25 pts) - Persona 1.

Entornos anidados (global, funcion, clase, bloque). Este es el modulo que
consumen los otros 3 (Persona 2, 3 y 4), asi que la firma de estas clases
no deberia cambiar una vez que el equipo la de por buena - si necesitan
cambiarla, avisen antes de romperla.

Referencia: Libro del Dragon, manejo de ambitos y tabla de simbolos
(seccion de analisis semantico / entornos anidados).

Lo que hay que implementar (marcado con TODO):
  - Scope.define / Scope.resolve
  - SymbolTable.enter_scope / exit_scope / current
  - ScopeHelpers.require_declared

Casos que las pruebas en tests/test_symbols.py van a exigir:
  - Redeclaracion en el mismo scope -> error.
  - Mismo nombre en scopes anidados distintos -> permitido (shadowing).
  - Resolver una variable global desde dentro de una funcion.
  - Un bloque anidado no debe "fugar" sus variables hacia afuera al salir.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.errors import ErrorReporter
from core.types import Type

ScopeKind = str  # "global" | "function" | "class" | "block"


@dataclass
class Symbol:
    name: str
    type: Type
    kind: str  # "var" | "const" | "param" | "function" | "class"


class Scope:
    def __init__(self, kind: ScopeKind, parent: "Scope | None" = None):
        self.kind = kind
        self.parent = parent
        self.symbols: dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> bool:
        """
        Inserta `symbol` en ESTE scope (no busca en los padres).

        Retorna True si se insertó correctamente, False si ya existia un
        simbolo con ese nombre en este mismo scope (redeclaracion). Quien
        llama a este metodo es responsable de reportar el error via
        ErrorReporter si retorna False - Scope no conoce el ErrorReporter
        a proposito, para mantenerlo simple de probar.
        """
        # TODO(P1): implementar.
        raise NotImplementedError

    def resolve(self, name: str) -> Symbol | None:
        """
        Busca `name` en este scope y, si no esta, sube por la cadena de
        `parent` hasta encontrarlo o llegar al scope global sin exito.

        Esta cadena de padres es la que hace que los closures funcionen:
        una funcion anidada resuelve nombres subiendo por el scope donde
        fue DEFINIDA, no por el scope desde donde fue LLAMADA.
        """
        # TODO(P1): implementar.
        raise NotImplementedError

    def resolve_local(self, name: str) -> Symbol | None:
        """Como resolve(), pero sin subir a los padres. Util para chequear redeclaracion."""
        return self.symbols.get(name)


class SymbolTable:
    def __init__(self):
        self._global = Scope(kind="global", parent=None)
        self._stack: list[Scope] = [self._global]

    @property
    def global_scope(self) -> Scope:
        return self._global

    def current(self) -> Scope:
        return self._stack[-1]

    def enter_scope(self, kind: ScopeKind) -> Scope:
        """Crea un scope hijo del scope actual, lo apila y lo retorna."""
        # TODO(P1): implementar.
        raise NotImplementedError

    def exit_scope(self) -> None:
        """Desapila el scope actual, volviendo al padre."""
        # TODO(P1): implementar.
        raise NotImplementedError


@dataclass
class ScopeHelpers:
    """
    Convenciones compartidas para que Persona 2/3/4 no dupliquen el patron
    "si resolve() da None -> error de variable no declarada" en cada uno
    de sus visit methods.
    """

    table: SymbolTable
    reporter: ErrorReporter

    def require_declared(self, name: str, ctx) -> Symbol | None:
        """
        Busca `name` desde el scope actual. Si no existe, reporta un error
        de categoria "ambito" y retorna None.
        """
        # TODO(P1): implementar usando self.table.current().resolve(name).
        raise NotImplementedError

    def define_or_error(self, symbol: Symbol, ctx) -> bool:
        """
        Intenta declarar `symbol` en el scope actual. Si ya existe en ESE
        scope, reporta un error de categoria "ambito" (redeclaracion) y
        retorna False.
        """
        # TODO(P1): implementar usando self.table.current().define(symbol).
        raise NotImplementedError
