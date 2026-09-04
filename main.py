"""
CLI del analizador: python main.py archivo.cps

Sin argumentos, lanza el IDE (ide/app.py).
"""

from __future__ import annotations

import sys

from driver import analizar_archivo


def main(argv: list[str]) -> int:
    if not argv:
        from ide.app import main as lanzar_ide

        lanzar_ide()
        return 0

    resultado = analizar_archivo(argv[0])

    if resultado.errores:
        for error in resultado.errores:
            print(error)
    else:
        print("OK: 0 errores")

    print()
    print(resultado.table.format_environments())

    return 0 if resultado.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
