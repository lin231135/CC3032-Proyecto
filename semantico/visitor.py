"""
Visitor combinado del analizador semantico.

Orden del MRO (F5, integracion): FunctionMixin y ClassMixin van ANTES que
TypeMixin. TypeMixin (F2) define `_aplicar_llamada` y `_aplicar_propiedad`
como stubs que devuelven ERROR (comentario "lo implementa P3/P4 en su
mixin"), y FunctionMixin/ClassMixin (F3/F4) definen las implementaciones
reales con el mismo nombre. Con TypeMixin antes en el MRO esos stubs ganan
en silencio y toda llamada a funcion (`f()`) o acceso a miembro (`obj.x`)
evaluaba siempre a ERROR sin reportar nada. Iban antes en este orden por
como se fueron sumando los mixins fase a fase; F5 lo corrige aqui. Los
stubs de TypeMixin quedan sin uso (dead code) pero no se borran: no se
puede tocar type_mixin.py en esta fase.

    class SemanticVisitor(
        ScopeMixin,      # P1 — tabla de simbolos (ya conectada)
        FunctionMixin,   # P3
        ClassMixin,      # P4
        TypeMixin,       # P2
        CompiscriptVisitor,
    ):
        ...
"""

from __future__ import annotations

from semantico.class_mixin import ClassMixin
from semantico.function_mixin import FunctionMixin
from semantico.scope_mixin import ScopeMixin
from semantico.type_mixin import TypeMixin

try:
    from generated.CompiscriptVisitor import CompiscriptVisitor
except ImportError:  # pragma: no cover - generated/ aparece tras `python build_grammar.py`
    class CompiscriptVisitor:  # type: ignore[no-redef]
        pass


class SemanticVisitor(
    ScopeMixin,
    FunctionMixin,
    ClassMixin,
    TypeMixin,
    CompiscriptVisitor,
):
    """Punto de entrada del analisis semantico. El IDE llama a `visit(tree)`."""
