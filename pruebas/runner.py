"""
Ejecuta la bateria de archivos .cps bajo pruebas/<categoria>/{validos,invalidos}/.

Lo usan tests/test_bateria.py (via pytest) y el boton "Correr bateria" del
IDE (F7).

Convencion (docs/PLAN_IMPLEMENTACION.md §6):
  - Cabecera obligatoria: `// @caso: <descripcion>` y, en los invalidos, una
    o mas lineas `// @error: <categoria>`.
  - validos/   -> se exige 0 errores (sintacticos y semanticos).
  - invalidos/ -> se exige >= 1 error y que TODAS las categorias declaradas
    en @error: aparezcan entre las reportadas (para no dar un falso positivo
    de "fallo, pero por otra razon").

`pruebas/demo/*.cps` queda fuera de `ejecutar_bateria()` a proposito: no
sigue la convencion validos/invalidos, es material de presentacion (ver
tests/test_bateria.py para sus 2 chequeos dedicados).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from driver import analizar_archivo

RAIZ = Path(__file__).parent

_RE_CASO = re.compile(r"^\s*//\s*@caso:\s*(.+?)\s*$")
_RE_ERROR = re.compile(r"^\s*//\s*@error:\s*(\S+)")


@dataclass
class ResultadoPrueba:
    archivo: Path
    es_valido: bool  # True si esta bajo .../validos/
    caso: str
    categorias_esperadas: list[str] = field(default_factory=list)
    paso: bool = False
    razon: str = ""

    def __str__(self) -> str:
        estado = "PASA" if self.paso else "FALLA"
        return f"[{estado}] {self.archivo.relative_to(RAIZ)} - {self.caso}"


def _leer_cabecera(ruta: Path) -> tuple[str, list[str]]:
    caso = ""
    categorias: list[str] = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m_caso = _RE_CASO.match(linea)
        if m_caso:
            caso = m_caso.group(1)
            continue
        m_error = _RE_ERROR.match(linea)
        if m_error:
            categorias.append(m_error.group(1))
            continue
        if linea.strip() and not linea.strip().startswith("//"):
            break  # termino la cabecera de comentarios
    return caso, categorias


def _evaluar(ruta: Path) -> ResultadoPrueba:
    es_valido = ruta.parent.name == "validos"
    caso, categorias_esperadas = _leer_cabecera(ruta)
    resultado = analizar_archivo(ruta)

    if es_valido:
        if resultado.ok:
            return ResultadoPrueba(ruta, es_valido, caso, categorias_esperadas, True)
        return ResultadoPrueba(
            ruta,
            es_valido,
            caso,
            categorias_esperadas,
            False,
            f"se esperaban 0 errores, hubo {len(resultado.errores)}: "
            f"{[str(e) for e in resultado.errores]}",
        )

    # invalidos/
    if not resultado.errores:
        return ResultadoPrueba(
            ruta, es_valido, caso, categorias_esperadas, False, "se esperaba >=1 error, hubo 0"
        )

    categorias_obtenidas = {e.category for e in resultado.errores}
    faltantes = [c for c in categorias_esperadas if c not in categorias_obtenidas]
    if faltantes:
        return ResultadoPrueba(
            ruta,
            es_valido,
            caso,
            categorias_esperadas,
            False,
            f"faltaron las categorias {faltantes} (se obtuvieron {sorted(categorias_obtenidas)})",
        )
    return ResultadoPrueba(ruta, es_valido, caso, categorias_esperadas, True)


def listar_archivos() -> list[Path]:
    """Todos los .cps de la bateria (validos + invalidos), sin pruebas/demo/."""
    return sorted(RAIZ.glob("*/validos/*.cps")) + sorted(RAIZ.glob("*/invalidos/*.cps"))


def ejecutar_bateria() -> list[ResultadoPrueba]:
    return [_evaluar(ruta) for ruta in listar_archivos()]


if __name__ == "__main__":
    resultados = ejecutar_bateria()
    fallos = [r for r in resultados if not r.paso]
    print(f"{len(resultados) - len(fallos)}/{len(resultados)} pasaron")
    for r in fallos:
        print(f"{r}: {r.razon}")
