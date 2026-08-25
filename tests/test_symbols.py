"""
Pruebas de core/symbols.py (Persona 1).

Corran con: pytest tests/test_symbols.py -v

Estas pruebas fallan a proposito hasta que se implementen los TODO en
core/symbols.py. Sirven como definicion de "terminado" del modulo de
Tabla de Simbolos.
"""

import pytest

from core.errors import ErrorReporter
from core.symbols import ScopeHelpers, Symbol, SymbolTable
from core.types import INTEGER, STRING


def make_var(name: str, type_=INTEGER, kind: str = "var") -> Symbol:
    return Symbol(name=name, type=type_, kind=kind)


def test_define_and_resolve_en_el_mismo_scope():
    table = SymbolTable()
    x = make_var("x")
    assert table.current().define(x) is True
    assert table.current().resolve("x") is x


def test_redeclaracion_en_el_mismo_scope_falla():
    table = SymbolTable()
    table.current().define(make_var("x"))
    ok = table.current().define(make_var("x", type_=STRING))
    assert ok is False


def test_shadowing_en_scopes_anidados_esta_permitido():
    table = SymbolTable()
    table.current().define(make_var("x", type_=INTEGER))

    inner = table.enter_scope("block")
    ok = inner.define(make_var("x", type_=STRING))
    assert ok is True
    assert inner.resolve("x").type == STRING
    table.exit_scope()

    assert table.current().resolve("x").type == INTEGER


def test_resolver_variable_global_desde_scope_anidado():
    table = SymbolTable()
    table.current().define(make_var("global_var"))

    table.enter_scope("function")
    table.enter_scope("block")
    assert table.current().resolve("global_var") is not None
    table.exit_scope()
    table.exit_scope()


def test_bloque_anidado_no_fuga_variables_al_salir():
    table = SymbolTable()
    table.enter_scope("block")
    table.current().define(make_var("local"))
    table.exit_scope()

    assert table.current().resolve("local") is None


def test_resolve_no_encontrado_retorna_none():
    table = SymbolTable()
    assert table.current().resolve("no_existe") is None


def test_scope_helpers_require_declared_reporta_error_si_falta():
    table = SymbolTable()
    reporter = ErrorReporter()
    helpers = ScopeHelpers(table=table, reporter=reporter)

    class FakeToken:
        line = 1
        column = 1

    class FakeCtx:
        start = FakeToken()

    resultado = helpers.require_declared("no_existe", FakeCtx())
    assert resultado is None
    assert reporter.has_errors()
    assert reporter.all()[0].category == "ambito"


def test_scope_helpers_define_or_error_reporta_redeclaracion():
    table = SymbolTable()
    reporter = ErrorReporter()
    helpers = ScopeHelpers(table=table, reporter=reporter)

    class FakeToken:
        line = 1
        column = 1

    class FakeCtx:
        start = FakeToken()

    assert helpers.define_or_error(make_var("x"), FakeCtx()) is True
    assert helpers.define_or_error(make_var("x"), FakeCtx()) is False
    assert reporter.has_errors()
