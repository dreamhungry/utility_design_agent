"""AST 白名单校验 + 表达式编译 + 缓存执行"""

from __future__ import annotations

import ast
import math
from typing import Any

ALLOWED_MATH_FUNCS = frozenset({
    "exp", "log", "log10", "pow", "sqrt",
    "sin", "cos", "tan", "fabs",
})

ALLOWED_NODE_TYPES = frozenset({
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name,
    ast.Call, ast.Attribute, ast.Load,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.FloorDiv, ast.Mod,
    ast.USub, ast.UAdd,
})

ALLOWED_NAMES = frozenset({"x", "math"})

# 安全求值命名空间
_SAFE_NAMESPACE: dict[str, Any] = {"math": math, "__builtins__": {}}


class FormulaValidationError(Exception):
    """表达式安全校验失败"""

    def __init__(self, expr: str, reason: str) -> None:
        self.expr = expr
        self.reason = reason
        super().__init__(f"表达式校验失败: {reason} | 表达式: {expr}")


class FormulaEngine:
    """公式引擎：AST 白名单校验 → 编译 → 缓存执行"""

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # 校验
    # ------------------------------------------------------------------

    @staticmethod
    def validate(expr: str) -> None:
        """校验表达式是否安全（仅允许白名单 AST 节点）

        Raises:
            FormulaValidationError: 校验失败
        """
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise FormulaValidationError(expr, f"语法错误: {e}") from e

        for node in ast.walk(tree):
            node_type = type(node)
            if node_type not in ALLOWED_NODE_TYPES:
                raise FormulaValidationError(
                    expr, f"不允许的节点类型: {node_type.__name__}"
                )

            # Name 节点只允许 x 和 math
            if isinstance(node, ast.Name) and node.id not in ALLOWED_NAMES:
                raise FormulaValidationError(
                    expr, f"不允许的变量名: {node.id}"
                )

            # Attribute 节点只允许 math.xxx 白名单函数
            if isinstance(node, ast.Attribute):
                if not (
                    isinstance(node.value, ast.Name)
                    and node.value.id == "math"
                    and node.attr in ALLOWED_MATH_FUNCS
                ):
                    attr_name = getattr(node, "attr", "?")
                    raise FormulaValidationError(
                        expr, f"不允许的属性访问: {attr_name}"
                    )

    # ------------------------------------------------------------------
    # 编译 + 执行
    # ------------------------------------------------------------------

    def validate_and_compile(self, expr: str) -> str:
        """校验并编译表达式，返回原始表达式字符串

        Raises:
            FormulaValidationError: 校验失败
        """
        self.validate(expr)
        if expr not in self._cache:
            self._cache[expr] = compile(expr, "<formula>", "eval")
        return expr

    def evaluate(self, expr: str, x: float) -> float:
        """安全求值（需先通过 validate_and_compile）"""
        code_obj = self._cache.get(expr)
        if code_obj is None:
            self.validate_and_compile(expr)
            code_obj = self._cache[expr]
        return float(eval(code_obj, _SAFE_NAMESPACE, {"x": x}))

    def sample(
        self,
        expr: str,
        n_points: int = 200,
        x_min: float = 0.0,
        x_max: float = 100.0,
    ) -> list[tuple[float, float]]:
        """在指定范围内均匀采样

        Returns:
            [(x0, y0), (x1, y1), ...] 采样点列表
        """
        step = (x_max - x_min) / max(n_points - 1, 1)
        points: list[tuple[float, float]] = []
        for i in range(n_points):
            xi = x_min + i * step
            yi = self.evaluate(expr, xi)
            points.append((xi, yi))
        return points
