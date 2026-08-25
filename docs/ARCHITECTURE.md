# Arquitectura y reparticion de trabajo — CC3032-Proyecto

Analizador semantico de Compiscript. Grammar de ANTLR ya dada
(`grammar/Compiscript.g4`), especificacion en `docs/Especificaciones.md` y
`docs/Generador_de_Analizadores_Semanticos.pdf`.

## Decisiones a tomar el dia 1 (bloquean a todos)

1. **`float`**: `Compiscript.g4` no tiene tipo/literal `float`, pero el
   enunciado pide validar aritmetica con `integer` **o** `float`. Decidir
   si se extiende la gramatica (agregar `FloatLiteral` al lexer y
   `'float'` a `baseType`) o si se documenta como limitacion.
2. **`+` con strings**: `Especificaciones.md` usa `"Hola " + nombre`, pero
   las reglas de tipos del PDF solo mencionan `+` como aritmetico. Decidir
   si `string + string` (o `string + cualquier tipo`) es valido.
3. **Congelar el contrato de `core/`** (`core/symbols.py`, `core/types.py`,
   `core/errors.py`) antes de escribir logica semantica seria. Si cambia
   una firma despues, se coordina con el equipo, no se rompe en silencio.

## Patron para 4 personas en un solo Visitor

ANTLR genera **una sola clase** `CompiscriptVisitor` con un `visitXxx` por
regla de la gramatica. Para que 4 personas trabajen sin pisarse el mismo
archivo, cada quien define sus `visitXxx` en su propio **mixin**, y se
combinan al final en `semantico/visitor.py`:

```python
class SemanticVisitor(ScopeMixin, TypeMixin, FunctionMixin, ClassMixin, CompiscriptVisitor):
    ...
```

Estado compartido en pilas (no solo el scope):
- `function_stack` (funcion actual + tipo de retorno declarado) y
  `loop_depth` (contador) — Persona 3, para `return`/`break`/`continue`.
- `current_class` — Persona 4, para `this` y resolucion de miembros
  heredados.

## Reparticion

| # | Modulo | Puntos | Bloqueado por |
|---|---|---|---|
| P1 | Tabla de Simbolos | 25 pts | nadie — va primero |
| P2 | Sistema de Tipos + Listas/Estructuras | parte de 60 pts | contrato de `core/` (dia 1) |
| P3 | Ambito + Funciones y Procedimientos + Control de Flujo + Codigo muerto | parte de 60 pts | contrato de `core/` (dia 1) |
| P4 | Clases y Objetos + IDE | 15 pts + parte de 60 | Frente IDE: nadie. Frente Clases: P1/P2/P3 estables |

### P1 — Tabla de Simbolos (`core/symbols.py`)

Expone: `SymbolTable`, `Scope`, `Symbol`, `ScopeHelpers.require_declared` /
`define_or_error`. No consume nada de nadie.

Flujo:
1. Implementar `Scope.define` / `Scope.resolve` (cadena de `parent` — esto
   es lo que hace que los closures funcionen: una funcion anidada resuelve
   nombres subiendo por el scope donde fue **definida**, no por el scope
   donde fue **llamada**).
2. Implementar `SymbolTable.enter_scope` / `exit_scope` con pila.
3. Implementar `ScopeHelpers.require_declared` / `define_or_error`.
4. Pruebas propias en `tests/test_symbols.py` (ya escritas como
   definicion de "terminado", corran `pytest tests/test_symbols.py -v`).
5. Congelar y avisar al equipo.

### P2 — Sistema de Tipos + Listas (`core/types.py`, mixin `type_mixin.py`)

Visita: `variableDeclaration`, `constantDeclaration`, `typeAnnotation` /
`type` / `baseType`, `assignment` (statement), toda la cadena
`logicalOrExpr` → `unaryExpr`, `literalExpr`, `arrayLiteral`, `IndexExpr`.

Expone: `get_type(ctx) -> Type`, `resolve_type_annotation(ctx) -> Type`.
Consume: `Scope` / `require_declared` / `define_or_error` (P1).

Flujo:
1. Con P1, cerrar las decisiones de `float` y `+` con strings.
2. `visitLiteralExpr` / `visitArrayLiteral` (tipos base).
3. Cadena aritmetico-logica de abajo hacia arriba: `additiveExpr` /
   `multiplicativeExpr` → `relationalExpr` / `equalityExpr` →
   `logicalAndExpr` / `logicalOrExpr`.
4. `variableDeclaration` / `constantDeclaration`: resolver tipo anotado,
   tipar inicializador, comparar, y llamar `define_or_error` (P1) ahi
   mismo — la redeclaracion sale gratis. `const` sin inicializador es
   error aqui.
5. `IndexExpr`: el objeto indexado debe ser `ArrayType`; avisar si un
   indice literal esta fuera de rango conocido en tiempo de analisis.
6. Helper compartido `_check_assignment(target_type, value_ctx)` usado
   tanto en `visitAssignment` (statement) como en `visitAssignExpr` /
   `visitPropertyAssignExpr` (expression) — no duplicar la regla.
7. Tipar tambien funciones/clases (`FunctionType`, `ClassType`) para que
   "no multiplicar funciones" salga gratis del chequeo de operandos
   numericos, sin codigo extra.

### P3 — Ambito + Funciones + Control de Flujo (`function_mixin.py`)

Visita: `block` (crea scope + escaneo de codigo muerto), `IdentifierExpr`,
`functionDeclaration` / `parameters` / `parameter`, `ifStatement` /
`whileStatement` / `doWhileStatement` / `forStatement` /
`foreachStatement` / `switchStatement` (condicion boolean),
`breakStatement` / `continueStatement`, `returnStatement`, `CallExpr`,
`tryCatchStatement`.

Expone: `check_call_args(func_type, args_ctx)` (P4 lo reusa para validar
la llamada al constructor). Consume: `Scope` (P1), `get_type` (P2).

Flujo:
1. Pilas propias: `function_stack` (funcion actual + retorno declarado),
   `loop_depth` (contador).
2. `functionDeclaration`: `define_or_error` en el scope **exterior**
   (permite recursion — el nombre debe existir antes de visitar su propio
   body), `enter_scope("function")`, declarar params, push a
   `function_stack`, visitar `block`, pop, `exit_scope`.
3. `IdentifierExpr`: `require_declared`, retorna el `Type` del simbolo.
4. Condiciones: `get_type(cond_ctx)` debe ser `BOOLEAN`.
5. `break`/`continue`: error si `loop_depth == 0`. `return`: error si
   `function_stack` vacio; comparar tipo contra el retorno declarado.
6. `CallExpr`: resolver `FunctionType` del callee, comparar aridad y
   tipos posicionales.
7. `block`: despues de la visita normal, marcar como error cualquier
   statement despues de un `return`/`break`/`continue` en la misma lista.

### P4 — Clases y Objetos + IDE (`class_mixin.py`, `arbol/`, `ide/`)

**Frente IDE** (empieza dia 1, no depende de nadie):
1. `build_grammar.py` ya genera el parser en `generated/`.
2. Shell de la app (editor, cargar/guardar `.cps`, boton "Compilar").
3. `arbol/ast_graphviz.py`: recorrer el `ParseTree` crudo de ANTLR y
   dibujarlo con Graphviz — no depende del analisis semantico.
4. Panel de errores (linea/columna/categoria) y panel de tabla de
   simbolos (con datos mock hasta que el visitor combinado exista).
5. Boton "Ejecutar bateria de pruebas": corre `pruebas/*/validos` y
   `pruebas/*/invalidos` de todos y muestra pass/fail.

**Frente Clases** (arranca cuando P1/P2/P3 esten estables):

Visita: `classDeclaration` / `classMember`, `NewExpr`, `ThisExpr`,
`PropertyAccessExpr`.

Flujo:
1. `classDeclaration`: `enter_scope("class")`, resolver clase padre si
   hereda (`: Identifier`), visitar `classMember*` (`constructor` es una
   `functionDeclaration` con nombre especial).
2. Pila propia `current_class` (para `ThisExpr`).
3. `PropertyAccessExpr`: tipar el objeto con `get_type` (P2), exigir
   `ClassType`, buscar el miembro subiendo por `parent` si no esta.
4. `NewExpr`: resolver clase, buscar `constructor`, llamar
   `check_call_args` (P3).

## Orden de integracion / git

- Bloqueante real: contrato de `core/` (dia 1-2).
- P4-Frente IDE corre en paralelo desde el inicio, no bloquea ni bloquea
  a nadie.
- P4-Frente Clases es lo ultimo en integrarse.
- Cada quien trabaja en su propio archivo mixin — commits individuales,
  sin pisarse (requisito del enunciado: no compartir commits en
  conjunto). `semantico/visitor.py` se toca solo para agregar la propia
  herencia del mixin.
- Integracion final: combinar los 4 mixins → conectar `SemanticVisitor`
  al boton "Compilar" del IDE → cada quien corre sus pruebas contra el
  visitor combinado, no solo contra su mixin aislado.
