# Tabla de Simbolos — Persona 1 (25 pts)

Documentacion de lo implementado para el modulo **Tabla de Simbolos** del
Proyecto 2 (Analisis Semantico de Compiscript). Sirve para presentar esta
parte y para que P2, P3 y P4 programen contra una interfaz estable.

El plan de equipo (reparticion, mixins, orden de integracion) sigue en
[`ARCHITECTURE.md`](ARCHITECTURE.md). Este archivo no lo reemplaza: describe
**como se construyo P1**, **como usarla** y **como se cubre el enunciado**.

Enunciado: [`Generador_de_Analizadores_Semanticos.pdf`](Generador_de_Analizadores_Semanticos.pdf).
Lenguaje: [`Especificaciones.md`](Especificaciones.md).

---

## 1. Que se entrega

El PDF asigna **25 pts** a:

> Manejo correcto de entornos anidados (global, funcion, clase, bloque)
> a lo largo de las fases del compilador.

P1 implementa esa estructura y los helpers que el resto del visitor usa
para declarar y resolver nombres. No recorre el arbol: eso lo hacen los
`visitXxx` de P2/P3/P4. La tabla es el servicio compartido.

| Archivo | Rol |
|---|---|
| `core/symbols.py` | `Symbol`, `Scope`, `SymbolTable`, `ScopeHelpers` |
| `core/errors.py` | `ErrorReporter` (categorias del enunciado) |
| `semantico/scope_mixin.py` | Estado compartido en el visitor (`self.table`, `self.helpers`, …) |
| `semantico/visitor.py` | Combina los 4 mixins; P1 ya dejo `ScopeMixin` conectado |
| `tests/test_symbols.py` | Pruebas del modulo |

Correr las pruebas de esta parte:

```bash
pytest tests/test_symbols.py -v
```

---

## 2. Como se diseno

Referencia: Libro del Dragon, entornos anidados (cadena de scopes con
puntero al padre).

```
SymbolTable
  _stack          [global] -> [function] -> [block]     # busqueda actual
  _environments   [global, function, class, block, …]   # historial para el IDE

Scope (kind, parent, symbols{})
  define(symbol)     inserta solo en ESTE scope; False si ya existe
  resolve(name)      busca aqui y, si no, sube por parent (closures)
  resolve_local(name) solo este scope (redeclaracion / shadowing)

Symbol (name, type, kind, initialized, line, column)
```

Decisiones de diseno:

1. **Pila + cadena de padres.** `enter_scope` apila un hijo del scope
   actual. `resolve` no usa la pila de llamada: sube por `parent`, que es
   el entorno donde el nombre **se definio**. Eso es lo que pide el PDF
   para closures (*capturando variables del entorno de definicion*).
2. **`Scope` no reporta errores.** Retorna `bool` / `None`. Quien llama
   decide como reportar. Facilita probar la tabla sin ANTLR.
3. **`ScopeHelpers`** concentra el patron repetido
   “no declarado / redeclarado” con categoria `"ambito"`, para que P2/P3/P4
   no dupliquen mensajes.
4. **Historial de entornos.** Al hacer `exit_scope` el ambito deja de ser
   visible para `resolve` (no hay fuga), pero queda en `environments()`
   porque el enunciado pide el **estado por cada entorno** como salida,
   no solo los scopes que siguen abiertos al final del programa.

### Kinds congelados

`Symbol.kind`: `"var"` | `"const"` | `"param"` | `"function"` | `"class"`

`Scope.kind`: `"global"` | `"function"` | `"class"` | `"block"`

Usen exactamente esos strings. El scope `"global"` lo crea `SymbolTable`;
el resto se abre con `enter_scope(kind)`.

---

## 3. Contrato para el equipo (no romper sin avisar)

```python
from core.symbols import Symbol, SymbolTable, ScopeHelpers
from core.types import INTEGER

# Declarar
symbol = Symbol(name="x", type=INTEGER, kind="var", line=3, column=8)
ok = table.current().define(symbol)          # False = redeclaracion
ok = helpers.define_or_error(symbol, ctx)    # igual + ErrorReporter

# Resolver (local, luego padres, hasta global)
sym = table.current().resolve("x")           # None si no existe
sym = helpers.require_declared("x", ctx)     # None + error "ambito"

# Entornos
table.enter_scope("function")  # o "class" / "block"
table.exit_scope()             # no se puede salir del global

# Salida para el IDE (Persona 4)
table.snapshot()             # scopes vivos ahora
table.environments()         # todos los creados (incluye cerrados)
table.format_environments()  # texto para el panel / presentacion
```

En el visitor combinado (`SemanticVisitor`) ya existen:

| Atributo / metodo | Dueno | Para que |
|---|---|---|
| `self.table` | P1 | Tabla de simbolos |
| `self.reporter` | P1 | Errores semanticos |
| `self.helpers` | P1 | `require_declared` / `define_or_error` |
| `self.enter_scope` / `self.exit_scope` | P1 | Abrir/cerrar entorno |
| `self.function_stack` | P3 | Funcion actual + tipo de retorno |
| `self.loop_depth` | P3 | `break` / `continue` |
| `self.current_class` | P4 | `this` y miembros heredados |

Cada persona llena **solo su mixin**. No definan `visitXxx` vacios con
`pass`: taparian el recorrido por defecto de ANTLR.

```text
P2  semantico/type_mixin.py
P3  semantico/function_mixin.py   (incluye visitBlock)
P4  semantico/class_mixin.py      + ide/ + arbol/
```

`semantico/visitor.py` ya declara la herencia de los cuatro mixins. No
hace falta tocarlo salvo que cambie esa lista.

### Recetas cortas

**P2 — declarar una variable** (la redeclaracion sale gratis):

```python
symbol = Symbol(name=nombre, type=tipo, kind="var", line=..., column=...)
self.define_or_error(symbol, ctx)
```

**P3 — funcion (el nombre va en el scope exterior para permitir recursion):**

```python
self.define_or_error(Symbol(name=fn_name, type=fn_type, kind="function"), ctx)
self.enter_scope("function")
# declarar params con kind="param"
self.function_stack.append((fn_name, return_type))
self.visit(ctx.block())
self.function_stack.pop()
self.exit_scope()
```

**P3 — bloque:**

```python
self.enter_scope("block")
self.visitChildren(ctx)
self.exit_scope()
```

**P4 — clase:**

```python
self.enter_scope("class")
self.current_class = class_type
# visitar miembros
self.current_class = None
self.exit_scope()
```

**P4 — panel del IDE:** despues de `visitor.visit(tree)`, mostrar
`visitor.table.format_environments()` o iterar `visitor.table.environments()`.
Los errores van en `visitor.reporter.all()` (linea, columna, categoria,
mensaje).

---

## 4. Cumplimiento del enunciado (PDF)

### 4.1 Rubrica (pagina de evaluacion)

| Componente | Pts | Estado en esta entrega |
|---|---|---|
| IDE | 15 | P4. La tabla ya expone `environments()` / `format_environments()` para el panel. |
| Analizador sintactico y semantico | 60 | P2/P3/P4 recorren el arbol. P1 no implementa reglas de tipos ni control de flujo. |
| **Tabla de simbolos** | **25** | **Implementada.** Entornos `global` / `function` / `class` / `block`, sin fuga al salir, shadowing permitido, closures por cadena de `parent`. |

### 4.2 Manejo de ambito (especificaciones del PDF)

Estas reglas las **sostiene la tabla**. Quedan efectivas en el compilador
cuando P2/P3/P4 llamen a `define_or_error` / `require_declared` /
`enter_scope` en sus `visitXxx`.

| Regla del PDF | Como se cubre |
|---|---|
| Resolucion de nombres segun ambito local o global | `Scope.resolve`: local, luego `parent`, hasta global |
| Error por uso de variables no declaradas | `require_declared` → categoria `"ambito"` |
| Prohibicion de redeclaracion en el mismo ambito | `define` / `define_or_error` → False + error `"ambito"` |
| Control de acceso en bloques anidados | Al `exit_scope`, el bloque deja de resolverse; el padre no ve esas variables |
| Nuevo entorno por cada funcion, clase y bloque | `enter_scope("function" \| "class" \| "block")` |
| Closures: capturar el entorno de **definicion** | Cadena `parent` (no el scope de llamada) |
| Redeclaracion de funciones / params duplicados | Mismo `define` sobre `kind="function"` o `"param"` |
| Salida: estado de la tabla por cada entorno | `environments()` y `format_environments()` |
| Errores con tipo y ubicacion | `ErrorReporter`: linea, columna, categoria, mensaje |

Categorias de error alineadas con la salida del PDF
(*tipo, ambito, funciones, control de flujo, clases, listas*):
`"tipo"`, `"ambito"`, `"funcion"`, `"control_flujo"`, `"clase"`, `"lista"`,
`"general"` (`core/errors.py`). P1 emite `"ambito"`.

### 4.3 Lo que P1 no implementa (a proposito)

El PDF pide ademas tipos, funciones, control de flujo, clases y listas.
Eso **no es la tabla**; es el visitor. Mapeo para no duplicar trabajo:

| Regla del PDF | Quien |
|---|---|
| Aritmetica, logicos, comparaciones, asignaciones, `const` con init | P2 |
| Tipos de listas e indices | P2 |
| Argumentos y tipo de retorno de llamadas | P3 |
| Recursion y funciones anidadas (usar la tabla) | P3 |
| Condiciones booleanas; `break`/`continue`/`return` | P3 |
| Codigo muerto | P3 |
| `.`, `this`, constructor | P4 |
| IDE, arbol visual, bateria `.cps` | P4 |

### 4.4 Limitacion documentada: `float`

El PDF pide operandos `integer` **o** `float` en aritmetica. La gramatica
oficial (`grammar/Compiscript.g4`) y `Especificaciones.md` **no** definen
tipo ni literal `float` (`baseType` es `boolean | integer | string | Identifier`;
el lexer solo tiene `IntegerLiteral` y `StringLiteral`).

P1 no extendio la gramatica. Hasta que el equipo acuerde lo contrario,
lo numerico es `integer`. Si se agrega `float` despues hay que tocar, en
conjunto: lexer, `baseType`, `PrimitiveKind.FLOAT` e `is_numeric` (P2).

### 4.5 `+` con strings

`Especificaciones.md` usa concatenacion (`"Hola " + nombre`). El PDF solo
menciona `+` aritmetico. Propuesta para P2: aceptar **`string + string`**,
no `string + T` arbitrario. Se implementa en `type_mixin.py`, no en la
tabla.

---

## 5. Que demuestran las pruebas

`pytest tests/test_symbols.py -v` cubre, frente al PDF:

- Declarar y resolver en el mismo scope
- Redeclaracion en el mismo ambito rechazada
- Shadowing en scopes anidados permitido
- Variable global visible desde funcion/bloque
- Un bloque **no fuga** variables al salir (`exit_scope`)
- Nombre inexistente → `None` / error `"ambito"`
- `resolve_local` no sube a los padres
- No se puede `exit_scope` del global
- `snapshot` = entornos vivos; `environments` = tambien los cerrados
  (global, funcion, clase, bloque)
- `ScopeMixin` y `SemanticVisitor` se construyen con el estado compartido

---

## 6. Ejemplo de salida (presentacion)

Tras analizar un programa que declara un global, una funcion y un bloque:

```text
[0] global: var x: integer, function foo: (integer) -> integer
[1] function: param n: integer
[2] block: var tmp: integer
```

Eso es `table.format_environments()`. El IDE (P4) puede pintarlo en el
panel de tabla de simbolos; ya no hace falta mock para la forma de los
datos.

Errores (ejemplo de `require_declared` / `define_or_error`):

```text
[ambito] linea 4:10 - 'y' no esta declarado en este ambito
[ambito] linea 7:8 - 'x' ya esta declarado en este ambito
```
