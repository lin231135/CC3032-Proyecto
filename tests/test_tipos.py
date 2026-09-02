"""
Una prueba por fila de la matriz de tipos de docs/PLAN_IMPLEMENTACION.md §3,
caso valido e invalido.

El indexado (`a[i]`) es la unica fila que no se puede ejercitar de punta a
punta todavia: `a` es un Identifier y `visitIdentifierExpr` lo implementa P3
en la fase F3. Se prueba `_aplicar_indice` directo, como el resto del fold
de `leftHandSide` (`_aplicar_llamada`/`_aplicar_propiedad`) hasta F5.
"""

from antlr4 import CommonTokenStream, InputStream

from core.types import ArrayType, BOOLEAN, ERROR, FLOAT, INTEGER, STRING
from driver import analizar
from generated.CompiscriptLexer import CompiscriptLexer
from generated.CompiscriptParser import CompiscriptParser
from semantico.visitor import SemanticVisitor


def _categorias(resultado):
    return {e.category for e in resultado.errores}


def _index_suffix(fuente: str):
    """Extrae el IndexExprContext del suffixOp de un `expressionStatement` como `arr[0];`."""
    lexer = CompiscriptLexer(InputStream(fuente))
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)
    tree = parser.program()
    expr = tree.statement(0).expressionStatement().expression()
    lhs = (
        expr.assignmentExpr()
        .conditionalExpr()
        .logicalOrExpr()
        .logicalAndExpr(0)
        .equalityExpr(0)
        .relationalExpr(0)
        .additiveExpr(0)
        .multiplicativeExpr(0)
        .unaryExpr(0)
        .primaryExpr()
        .leftHandSide()
    )
    return lhs.suffixOp(0)


# ---------------------------------------------------------------------
# + : numerico, numerico -> max_tipo(a,b) ; string,string -> string ; otro -> error tipo
# ---------------------------------------------------------------------

def test_suma_numericos_valido():
    assert analizar("1 + 2;").ok
    assert analizar("1 + 2.5;").ok


def test_suma_strings_valido():
    assert analizar('"Hola " + "mundo";').ok


def test_suma_combinacion_invalida():
    r = analizar('1 + "a";')
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# - * / % : numerico, numerico -> max_tipo(a,b) ; otro -> error tipo
# ---------------------------------------------------------------------

def test_aritmetica_numerico_valido():
    assert analizar("5 - 2;").ok
    assert analizar("5 * 2.0;").ok
    assert analizar("5 / 2;").ok
    assert analizar("5 % 2;").ok


def test_aritmetica_invalida():
    r = analizar('"a" - 1;')
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# < <= > >= : numerico, numerico -> boolean ; otro -> error tipo
# ---------------------------------------------------------------------

def test_relacional_valido():
    assert analizar("3 < 4;").ok
    assert analizar("3.5 >= 2;").ok


def test_relacional_invalido():
    r = analizar('3 < "a";')
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# == != : T,T equivalentes (DEC-7) -> boolean ; tipos distintos -> error tipo
# ---------------------------------------------------------------------

def test_igualdad_valida():
    assert analizar("3 == 3;").ok
    assert analizar("3 != 3.0;").ok
    assert analizar('"a" == "a";').ok


def test_igualdad_invalida():
    r = analizar('3 == "a";')
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# && || : boolean, boolean -> boolean ; otro -> error tipo
# ---------------------------------------------------------------------

def test_logicos_validos():
    assert analizar("true && false;").ok
    assert analizar("true || false;").ok


def test_logicos_invalidos():
    r = analizar("1 && true;")
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# ! : boolean -> boolean ; otro -> error tipo
# ---------------------------------------------------------------------

def test_negacion_valida():
    assert analizar("!true;").ok


def test_negacion_invalida():
    r = analizar("!1;")
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# - unario : numerico -> mismo tipo ; otro -> error tipo
# ---------------------------------------------------------------------

def test_menos_unario_valido():
    assert analizar("-5;").ok
    assert analizar("-5.5;").ok


def test_menos_unario_invalido():
    r = analizar('-"a";')
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# ?: : cond boolean, ramas equivalentes -> tipo de las ramas
# ---------------------------------------------------------------------

def test_ternario_valido():
    assert analizar("true ? 1 : 2;").ok
    assert analizar("true ? 1 : 2.5;").ok


def test_ternario_condicion_no_booleana_invalida():
    r = analizar("1 ? 1 : 2;")
    assert not r.ok
    assert "tipo" in _categorias(r)


def test_ternario_ramas_distintas_invalido():
    r = analizar('true ? 1 : "a";')
    assert not r.ok
    assert "tipo" in _categorias(r)


# ---------------------------------------------------------------------
# indexado a[i] : a ArrayType, i integer -> element_type
# ---------------------------------------------------------------------

def test_indexado_valido():
    visitor = SemanticVisitor()
    sufijo = _index_suffix("arr[0];")
    assert visitor._aplicar_indice(ArrayType(INTEGER), sufijo) == INTEGER
    assert not visitor.reporter.has_errors()


def test_indexado_base_no_arreglo_invalido():
    visitor = SemanticVisitor()
    sufijo = _index_suffix("arr[0];")
    assert visitor._aplicar_indice(INTEGER, sufijo) == ERROR
    assert "lista" in {e.category for e in visitor.reporter.all()}


def test_indexado_indice_no_entero_invalido():
    visitor = SemanticVisitor()
    sufijo = _index_suffix('arr["x"];')
    assert visitor._aplicar_indice(ArrayType(INTEGER), sufijo) == ERROR
    assert "lista" in {e.category for e in visitor.reporter.all()}
