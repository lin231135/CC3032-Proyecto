"""
Parametriza pruebas/runner.ejecutar_bateria() con pytest: un test por
archivo .cps de la bateria, mas los 2 chequeos dedicados de pruebas/demo/.
"""

import pytest

from core.errors import CATEGORIAS
from driver import analizar_archivo
from pruebas.runner import RAIZ, ejecutar_bateria

RESULTADOS = ejecutar_bateria()


@pytest.mark.parametrize(
    "resultado",
    RESULTADOS,
    ids=[str(r.archivo.relative_to(RAIZ)) for r in RESULTADOS],
)
def test_bateria(resultado):
    assert resultado.paso, resultado.razon


def test_bateria_no_esta_vacia():
    assert len(RESULTADOS) >= 45


def test_demo_programa_completo_sin_errores():
    resultado = analizar_archivo(RAIZ / "demo" / "programa_completo.cps")
    assert resultado.ok, [str(e) for e in resultado.errores]


def test_demo_programa_errores_una_por_categoria():
    resultado = analizar_archivo(RAIZ / "demo" / "programa_errores.cps")
    categorias = [e.category for e in resultado.errores]
    assert sorted(categorias) == sorted(CATEGORIAS), [str(e) for e in resultado.errores]
