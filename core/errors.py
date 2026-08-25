"""
Reporte de errores semanticos, compartido por los 4 modulos.

Todos los visitors (tabla de simbolos, tipos, ambito/funciones/control de
flujo, clases) reportan aqui en vez de lanzar excepciones o hacer print():
asi el IDE puede mostrar la lista completa de errores de una sola pasada,
igual que el analizador lexico/sintactico de la fase anterior.
"""

from dataclasses import dataclass, field


CATEGORIAS = (
    "tipo",
    "ambito",
    "funcion",
    "control_flujo",
    "clase",
    "lista",
    "general",
)


@dataclass
class SemanticError:
    line: int
    column: int
    category: str
    message: str

    def __str__(self) -> str:
        return f"[{self.category}] linea {self.line}:{self.column} - {self.message}"


@dataclass
class ErrorReporter:
    errors: list[SemanticError] = field(default_factory=list)

    def error(self, ctx, category: str, message: str) -> None:
        """ctx es cualquier ParserRuleContext de ANTLR (tiene .start.line / .start.column)."""
        assert category in CATEGORIAS, f"categoria desconocida: {category}"
        token = ctx.start
        self.errors.append(SemanticError(token.line, token.column, category, message))

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def all(self) -> list[SemanticError]:
        return list(self.errors)
