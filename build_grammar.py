"""
Regenera el lexer/parser/visitor de ANTLR a partir de grammar/Compiscript.g4.

Requisitos: Java en el PATH, y `pip install antlr4-tools` (ver requirements.txt).

Uso:
    python build_grammar.py
"""

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
GRAMMAR = ROOT / "grammar" / "Compiscript.g4"
OUT_DIR = ROOT / "generated"


def main() -> None:
    if shutil.which("antlr4") is None:
        sys.exit(
            "No se encontro el comando 'antlr4'. Instalen las dependencias con:\n"
            "    pip install -r requirements.txt\n"
            "y verifiquen que Java este disponible (`java -version`)."
        )

    OUT_DIR.mkdir(exist_ok=True)

    cmd = [
        "antlr4",
        "-Dlanguage=Python3",
        "-visitor",
        "-o", str(OUT_DIR),
        str(GRAMMAR),
    ]
    subprocess.run(cmd, check=True)
    print(f"Lexer/Parser/Visitor generados en: {OUT_DIR}")


if __name__ == "__main__":
    main()
