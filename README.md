# CC3032-Proyecto — Analizador Semantico de Compiscript

### Construccion de Compiladores — UVG 2026

* Javier Linares (231135)
* Gadiel Ocaña
* Cindy Gualim
* Jennifer Toxcon (21276)

---

Analizador sintactico y semantico de **Compiscript** (subconjunto de
TypeScript). El analizador sintactico se genera con **ANTLR** a partir de
`grammar/Compiscript.g4`; el analizador semantico recorre el arbol con un
**Visitor** de ANTLR aplicando reglas de tipos, ambito, funciones, control
de flujo, clases y listas, apoyado en una tabla de simbolos con entornos
anidados (global, funcion, clase, bloque).

Ver **`docs/ARCHITECTURE.md`** para la arquitectura completa y la
repartición de trabajo por persona. La documentacion de la tabla de
simbolos esta en **`docs/Tabla de Simbolos.md`**.

---

## Requisitos

* Python 3.11+
* Java (JDK) en el `PATH` — lo usa `antlr4-tools` para generar el parser
* Graphviz instalado en el sistema (para visualizar el arbol sintactico)

## Instalacion

```bash
pip install -r requirements.txt
python build_grammar.py   # genera generated/ a partir de grammar/Compiscript.g4
```

## Correr las pruebas

```bash
pytest tests/ -v
```

## Estructura del repo

```
CC3032-Proyecto/
├── build_grammar.py       # genera el lexer/parser/visitor de ANTLR
├── grammar/
│   └── Compiscript.g4
├── generated/              # salida de ANTLR (gitignored, se regenera)
├── core/                   # Persona 1 + Persona 2: contrato compartido
│   ├── symbols.py          # Tabla de Simbolos — Persona 1
│   ├── types.py            # Sistema de Tipos — Persona 2
│   └── errors.py           # Reporte de errores semanticos
├── semantico/               # Visitor combinado (mixins por persona)
├── arbol/                   # Visualizacion del arbol sintactico — Persona 4
├── ide/                      # IDE (CustomTkinter) — Persona 4
├── pruebas/                  # .cps validos/invalidos por regla semantica
├── tests/                    # pytest
└── docs/
    ├── README.md              # Tabla de simbolos (P1): diseno, uso y enunciado
    ├── ARCHITECTURE.md
    ├── Especificaciones.md
    └── Generador_de_Analizadores_Semanticos.pdf
```

## Flujo de trabajo del equipo

* Cada persona trabaja en su propio modulo/mixin y hace sus propios
  commits (el enunciado no permite commits compartidos).
* El contrato de `core/` (symbols, types, errors) se congela primero —
  todo lo demas se programa contra esa interfaz.
* Detalle de quien implementa que regla del grammar, en
  `docs/ARCHITECTURE.md`.
