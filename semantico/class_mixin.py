"""
Clases y objetos (Persona 4). Cubre R20-R22 de
docs/PLAN_IMPLEMENTACION.md §5.

Nota de integracion (para F5, misma trampa que documenta function_mixin.py
para `_aplicar_llamada`): `_aplicar_propiedad` esta implementado aqui de
verdad, pero `semantico/type_mixin.py` (F2) ya define un stub con el mismo
nombre que devuelve ERROR. Como `SemanticVisitor` hereda
`(ScopeMixin, TypeMixin, FunctionMixin, ClassMixin, CompiscriptVisitor)`,
TypeMixin queda ANTES que ClassMixin en el MRO y su stub gana en silencio:
ahora mismo `obj.campo` y `obj.metodo()` evaluan siempre a ERROR via el fold
de `visitLeftHandSide`, sin reportar nada (por diseno de ERROR, DEC-4). Por
eso `_aplicar_propiedad` se prueba aqui llamandolo directo, no con acceso
`.` real de punta a punta. `visitNewExpr` y `visitThisExpr` no colisionan
con nada y si funcionan de punta a punta.
"""

from __future__ import annotations

from core.symbols import Symbol
from core.types import ClassType, ERROR, FunctionType, VOID
from generated.CompiscriptParser import CompiscriptParser


class ClassMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.clases: dict[str, ClassType] -- registro de clases declaradas
        # (plan §4.2). No hay prepass todavia (F5): una clase que hereda de
        # otra declarada MAS ADELANTE en el archivo no se resuelve hasta esa
        # fase; es una limitacion conocida y documentada, no un bug de F4.
        self.clases: dict[str, ClassType] = {}

    # ------------------------------------------------------------------
    # Declaracion de clases (R20-R22)
    # ------------------------------------------------------------------

    def visitClassDeclaration(self, ctx: "CompiscriptParser.ClassDeclarationContext") -> None:
        nombre = ctx.Identifier(0).getText()

        if nombre in self.clases:
            self.reporter.error(ctx, "clase", f"la clase '{nombre}' ya esta declarada")
            tipo_clase = self.clases[nombre]
        else:
            tipo_clase = ClassType(name=nombre)
            self.clases[nombre] = tipo_clase
            simbolo = Symbol(
                name=nombre,
                type=tipo_clase,
                kind="class",
                initialized=True,
                line=ctx.Identifier(0).getSymbol().line,
                column=ctx.Identifier(0).getSymbol().column,
            )
            self.define_or_error(simbolo, ctx)

        if ctx.Identifier(1) is not None:
            nombre_padre = ctx.Identifier(1).getText()
            padre = self.clases.get(nombre_padre)
            if padre is None:
                self.reporter.error(ctx, "clase", f"la clase padre '{nombre_padre}' no esta declarada")
            elif padre is tipo_clase:
                self.reporter.error(ctx, "clase", f"la clase '{nombre}' no puede heredar de si misma")
            else:
                tipo_clase.parent = padre

        clase_anterior = self.current_class
        self.current_class = tipo_clase
        self.enter_scope("class")
        for miembro in ctx.classMember():
            self.visit(miembro)
        self.exit_scope()
        self.current_class = clase_anterior

    def visitClassMember(self, ctx: "CompiscriptParser.ClassMemberContext") -> None:
        if ctx.functionDeclaration() is not None:
            fn_ctx = ctx.functionDeclaration()
            nombre = fn_ctx.Identifier().getText()
            # Se registra ANTES de visitar el cuerpo para que el metodo sea
            # invocable via `this.<nombre>()`; 'constructor' es una
            # functionDeclaration comun con este nombre especial (DEC-6).
            self.current_class.methods[nombre] = self._firma_metodo(fn_ctx)
            self.visit(fn_ctx)
        elif ctx.variableDeclaration() is not None:
            vd_ctx = ctx.variableDeclaration()
            self.visit(vd_ctx)
            simbolo = self.table.current().resolve_local(vd_ctx.Identifier().getText())
            if simbolo is not None:
                self.current_class.fields[simbolo.name] = simbolo.type
        else:
            cd_ctx = ctx.constantDeclaration()
            self.visit(cd_ctx)
            simbolo = self.table.current().resolve_local(cd_ctx.Identifier().getText())
            if simbolo is not None:
                self.current_class.fields[simbolo.name] = simbolo.type

    def _firma_metodo(self, fn_ctx: "CompiscriptParser.FunctionDeclarationContext") -> FunctionType:
        """
        Misma logica de firma que `visitFunctionDeclaration` (P3,
        function_mixin.py): no se puede reusar directamente porque ese
        metodo no devuelve el FunctionType que calcula, y F4 solo puede
        tocar este archivo.
        """
        tipos_param = []
        if fn_ctx.parameters() is not None:
            for p in fn_ctx.parameters().parameter():
                tipos_param.append(self._tipo_parametro(p))

        if fn_ctx.Identifier().getText() == "constructor":
            tipo_retorno = VOID  # DEC-6: constructor -> retorno VOID implicito
        elif fn_ctx.type_() is not None:
            tipo_retorno = self.resolve_type_annotation(fn_ctx.type_())
        else:
            tipo_retorno = VOID

        return FunctionType(param_types=tuple(tipos_param), return_type=tipo_retorno)

    # ------------------------------------------------------------------
    # this / new (R21, R22)
    # ------------------------------------------------------------------

    def visitThisExpr(self, ctx: "CompiscriptParser.ThisExprContext"):
        if self.current_class is None:
            self.reporter.error(ctx, "clase", "'this' solo es valido dentro de una clase")
            t = ERROR
        else:
            t = self.current_class
        ctx.tipo = t
        return t

    def visitNewExpr(self, ctx: "CompiscriptParser.NewExprContext"):
        nombre = ctx.Identifier().getText()
        tipo_clase = self.clases.get(nombre)
        if tipo_clase is None:
            self.reporter.error(ctx, "clase", f"la clase '{nombre}' no esta declarada")
            if ctx.arguments() is not None:
                for arg in ctx.arguments().expression():
                    self.get_type(arg)
            t = ERROR
            ctx.tipo = t
            return t

        constructor = tipo_clase.methods.get("constructor")
        if constructor is not None:
            self.check_call_args(constructor, ctx.arguments(), ctx)
        else:
            # R21: sin constructor declarado se exigen 0 argumentos.
            num_args = len(ctx.arguments().expression()) if ctx.arguments() is not None else 0
            if num_args != 0:
                self.reporter.error(
                    ctx, "clase", f"'{nombre}' no declara constructor, se esperaban 0 argumentos"
                )

        ctx.tipo = tipo_clase
        return tipo_clase

    # ------------------------------------------------------------------
    # Acceso a miembros (R20), fold de leftHandSide
    # ------------------------------------------------------------------

    def _aplicar_propiedad(self, tipo_base, ctx):
        if tipo_base == ERROR:
            return ERROR
        if not isinstance(tipo_base, ClassType):
            self.reporter.error(ctx, "clase", f"no se puede acceder a un miembro de un valor de tipo {tipo_base!r}")
            return ERROR
        nombre = ctx.Identifier().getText()
        miembro = tipo_base.lookup_member(nombre)
        if miembro is None:
            self.reporter.error(ctx, "clase", f"'{tipo_base.name}' no tiene el miembro '{nombre}'")
            return ERROR
        return miembro
