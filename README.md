# CC3032-Proyecto — Analizador Semantico de Compiscript

### Construccion de Compiladores — UVG 2026

* Javier Linares (231135)
* Gadiel Ocaña (231270)
* Cindy Gualim (21226)
* Jennifer Toxcon (21276)

---

Analizador sintactico y semantico de **Compiscript** (subconjunto de
TypeScript). El analizador sintactico se genera con **ANTLR** a partir de
`grammar/Compiscript.g4`; el analizador semantico recorre el arbol con un
**Visitor** de ANTLR (dos pasadas: prepass + recorrido completo) aplicando
reglas de tipos, ambito, funciones, control de flujo, clases y listas,
apoyado en una tabla de simbolos con entornos anidados (global, funcion,
clase, bloque). Incluye un IDE (CustomTkinter) con editor, panel de
errores, tabla de simbolos, arbol sintactico visual y una bateria de
pruebas `.cps` ejecutable desde el IDE o con `pytest`.

Ver `docs/ARCHITECTURE.md` para la arquitectura y la repartición de trabajo
por persona, `docs/Tabla de Simbolos.md` para el diseño de la tabla de
simbolos, y `docs/COBERTURA.md` para la matriz completa regla del
enunciado → codigo → prueba.

---

## Requisitos

* Python 3.11+
* Java (JDK) en el `PATH` — lo usa `antlr4-tools` para generar el parser
* Graphviz instalado en el sistema, con el binario `dot` en el `PATH` (para
  visualizar el arbol sintactico en el IDE; sin el, el panel cae a un
  fallback de texto)

## Instalación

```bash
pip install -r requirements.txt
```

## Generar el parser

El lexer/parser/visitor de ANTLR no se versiona (`generated/` esta en
`.gitignore`); hay que generarlo despues de clonar o cada vez que cambie
`grammar/Compiscript.g4`:

```bash
python build_grammar.py
```

Esto deja `CompiscriptLexer.py`, `CompiscriptParser.py`,
`CompiscriptVisitor.py` y `CompiscriptListener.py` directamente en
`generated/`, usando la misma version de ANTLR que
`antlr4-python3-runtime` (fijada en `requirements.txt`) para evitar el
desfase generador/runtime.

## Correr el IDE

```bash
python main.py
```

Sin argumentos abre el IDE: editor con numeros de linea, botones Abrir /
Guardar / Guardar como / Compilar (F5) / Correr bateria, y pestañas de
Errores (doble clic salta a la linea), Tabla de simbolos, Arbol sintactico
(con zoom) y Bateria.

## Analizar un archivo por linea de comandos

```bash
python main.py archivo.cps
```

Imprime los errores (o `OK: 0 errores`) y la tabla de simbolos por
entorno. El codigo de salida es `0` si el archivo compilo sin errores.

## Correr las pruebas

```bash
python -m pytest tests/ -q
```

Incluye la bateria de archivos `.cps` (`tests/test_bateria.py`, parametriza
`pruebas/runner.ejecutar_bateria()`), las pruebas unitarias de cada mixin y
el guardarril de colision de `visit*` entre mixins (`tests/test_mixins.py`).
Para correr solo la bateria:

```bash
python -m pytest tests/test_bateria.py -q
```

o, desde codigo (lo mismo que usa el boton del IDE):

```python
from pruebas.runner import ejecutar_bateria

for resultado in ejecutar_bateria():
    print(resultado, resultado.razon)
```

Convencion de la bateria (`pruebas/<categoria>/{validos,invalidos}/*.cps`,
cabecera `// @caso:` / `// @error:`) en `pruebas/README.md`.

## Estructura del repo

```
CC3032-Proyecto/
├── main.py                  # CLI: python main.py archivo.cps (sin args -> IDE)
├── driver.py                # analizar(fuente) -> Resultado; punto de entrada unico
├── build_grammar.py         # genera generated/ a partir de grammar/Compiscript.g4
├── requirements.txt
├── grammar/
│   └── Compiscript.g4
├── generated/                # salida de ANTLR (gitignored, se regenera)
├── core/                     # contrato compartido
│   ├── symbols.py            # Tabla de simbolos (Persona 1) — congelado
│   ├── types.py               # Sistema de tipos (Persona 2)
│   └── errors.py              # SemanticError / ErrorReporter
├── semantico/                 # Visitor combinado, un mixin por persona
│   ├── scope_mixin.py          # P1 — estado compartido (tabla, reporter, ...)
│   ├── type_mixin.py            # P2 — tipos, listas, fold de leftHandSide
│   ├── function_mixin.py         # P3 — ambito, funciones, control de flujo
│   ├── class_mixin.py             # P4 — clases, this, new, herencia
│   ├── prepass.py                  # Pasada 1: funciones/clases por adelantado
│   ├── visitor.py                   # combina los 4 mixins (SemanticVisitor)
│   └── config.py                    # banderas de decisiones congeladas (DEC-5)
├── arbol/
│   └── ast_graphviz.py         # ParseTree -> PNG en memoria (Persona 4)
├── ide/
│   └── app.py                  # IDE CustomTkinter (Persona 4)
├── pruebas/                    # bateria .cps: <categoria>/{validos,invalidos}/*.cps
│   ├── runner.py                # ejecutar_bateria() -> list[ResultadoPrueba]
│   ├── README.md                 # convencion de la bateria
│   └── demo/                      # programa_completo.cps / programa_errores.cps
├── tests/                      # pytest
└── docs/
    ├── ARCHITECTURE.md          # arquitectura y repartición por persona
    ├── COBERTURA.md              # matriz regla del PDF -> codigo -> prueba
    ├── Tabla de Simbolos.md       # diseño de la tabla de simbolos (Persona 1)
    ├── Especificaciones.md         # lenguaje Compiscript
    └── Generador_de_Analizadores_Semanticos.pdf   # enunciado del proyecto
```
