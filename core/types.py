"""
Sistema de tipos de Compiscript.

Dueno: Persona 2 (Sistema de Tipos + Listas). Este archivo es un borrador
inicial para que Persona 1 pueda usar `Type` en `core/symbols.py` desde ya.
Persona 2 debe revisarlo, completarlo y es quien tiene la ultima palabra
sobre las reglas de coercion/compatibilidad.

PENDIENTE A DECIDIR EN EQUIPO (ver docs/ARCHITECTURE.md):
  - Compiscript.g4 no tiene tipo/literal `float`. El enunciado pide validar
    aritmetica con integer O float. Si agregan `float` a la gramatica,
    agreguen aqui `PrimitiveKind.FLOAT` y actualicen `is_numeric`.
  - Especificaciones.md usa `+` para concatenar strings
    (`"Hola " + nombre`). Decidir si `is_assignable`/el chequeo de la
    operacion `+` permite `string + string` (o `string + cualquier tipo`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class PrimitiveKind(Enum):
    INTEGER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    VOID = auto()  # tipo de retorno de una funcion sin ": type"


class Type:
    """Clase base. No instanciar directamente."""


@dataclass(frozen=True)
class PrimitiveType(Type):
    kind: PrimitiveKind

    def __repr__(self) -> str:
        return self.kind.name.lower()


@dataclass(frozen=True)
class ArrayType(Type):
    element_type: Type

    def __repr__(self) -> str:
        return f"{self.element_type!r}[]"


@dataclass(frozen=True)
class FunctionType(Type):
    param_types: tuple[Type, ...]
    return_type: Type

    def __repr__(self) -> str:
        params = ", ".join(repr(p) for p in self.param_types)
        return f"({params}) -> {self.return_type!r}"


@dataclass
class ClassType(Type):
    name: str
    parent: "ClassType | None" = None
    fields: dict[str, Type] = field(default_factory=dict)
    methods: dict[str, FunctionType] = field(default_factory=dict)

    def lookup_member(self, name: str) -> Type | None:
        """Busca un campo o metodo en esta clase y, si no esta, en la cadena de herencia."""
        cls: ClassType | None = self
        while cls is not None:
            if name in cls.fields:
                return cls.fields[name]
            if name in cls.methods:
                return cls.methods[name]
            cls = cls.parent
        return None

    def __repr__(self) -> str:
        return self.name


# Instancias unicas para los tipos primitivos (comparar con `is` o `==`, son frozen).
INTEGER = PrimitiveType(PrimitiveKind.INTEGER)
STRING = PrimitiveType(PrimitiveKind.STRING)
BOOLEAN = PrimitiveType(PrimitiveKind.BOOLEAN)
NULL = PrimitiveType(PrimitiveKind.NULL)
VOID = PrimitiveType(PrimitiveKind.VOID)


def is_numeric(t: Type) -> bool:
    # TODO(P2): agregar FLOAT aqui si se agrega al lenguaje.
    return t == INTEGER


def is_assignable(target: Type, value: Type) -> bool:
    """True si un valor de tipo `value` se puede asignar a una variable de tipo `target`."""
    if target == value:
        return True
    if value == NULL:
        # TODO(P2): decidir si null es asignable a cualquier tipo o solo a
        # tipos de clase / arreglo (no deberia serlo a integer/string/boolean).
        return True
    if isinstance(target, ArrayType) and isinstance(value, ArrayType):
        return is_assignable(target.element_type, value.element_type)
    if isinstance(target, ClassType) and isinstance(value, ClassType):
        cls: ClassType | None = value
        while cls is not None:
            if cls is target or cls.name == target.name:
                return True
            cls = cls.parent
        return False
    return False
