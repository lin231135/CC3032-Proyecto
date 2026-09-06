# Bateria de pruebas `.cps`

Convencion completa en `docs/PLAN_IMPLEMENTACION.md` §6. Resumen:

```
pruebas/<categoria>/{validos,invalidos}/<nombre>.cps
```

Categorias: `tipos`, `ambito`, `funciones`, `control_flujo`, `clases`,
`listas`, `tabla_simbolos`, `generales` y `demo` (esta ultima no sigue la
convencion `validos`/`invalidos`, ver mas abajo).

## Cabecera obligatoria

```cps
// @caso: R12 argumentos de menos en una llamada
// @error: funcion            <- solo en los invalidos, 1 o mas lineas
```

- `validos/` — el runner exige **0 errores** (sintacticos y semanticos).
- `invalidos/` — exige **>= 1 error** y que **todas** las categorias
  declaradas en `@error:` aparezcan entre las reportadas. Evita el falso
  positivo de "fallo, pero por otra razon".

## Cobertura

Al menos un archivo valido y uno invalido por cada regla R1-R27 del plan
(§5), con la excepcion de R11, R14 y R15: son reglas estructurales sin una
condicion de error natural (un nuevo entorno, una recursion, una closure
que ya resuelve bien no tiene un "caso invalido" propio — sus fallas caen
en R7-R9), asi que solo tienen archivo `validos/`.

## `pruebas/demo/`

Dos archivos para la presentacion (guion en el plan §11), fuera de la
bateria automatica (`pruebas/runner.ejecutar_bateria()` no los incluye):

- `programa_completo.cps` — clases, herencia, closures, recursion,
  arreglos y todo el control de flujo. Debe dar **0 errores**.
- `programa_errores.cps` — exactamente **un error de cada una** de las 7
  categorias (`tipo`, `ambito`, `funcion`, `control_flujo`, `clase`,
  `lista`, `general`).

## Correr la bateria

```bash
python -m pytest tests/test_bateria.py -q
```

o desde codigo (lo mismo que usa el boton del IDE):

```python
from pruebas.runner import ejecutar_bateria

for resultado in ejecutar_bateria():
    print(resultado, resultado.razon)
```
