"""
Visitor combinado del analizador semantico.

Cada persona implementa su mixin. Esta clase solo se toca para agregar
la herencia del mixin propio (requisito: no compartir commits en conjunto).

    class SemanticVisitor(
        ScopeMixin,      # P1 — tabla de simbolos (ya conectada)
        TypeMixin,       # P2
        FunctionMixin,   # P3
        ClassMixin,      # P4
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
    TypeMixin,
    FunctionMixin,
    ClassMixin,
    CompiscriptVisitor,
):
    """Punto de entrada del analisis semantico. El IDE llama a `visit(tree)`."""
