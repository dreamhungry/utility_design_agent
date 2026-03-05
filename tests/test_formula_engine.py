"""AST 白名单校验 + 表达式编译执行测试"""

import math

import pytest

from utility_design_agent.formula_engine import FormulaEngine, FormulaValidationError


class TestValidation:
    def setup_method(self):
        self.engine = FormulaEngine()

    def test_simple_expression(self):
        self.engine.validate("x")

    def test_math_functions(self):
        self.engine.validate("math.exp(x)")
        self.engine.validate("math.log(x)")
        self.engine.validate("math.sqrt(x)")
        self.engine.validate("math.pow(x, 2)")
        self.engine.validate("math.sin(x)")
        self.engine.validate("math.cos(x)")

    def test_complex_expression(self):
        self.engine.validate("1 / (1 + math.exp(-10 * (x - 0.3)))")

    def test_reject_import(self):
        with pytest.raises(FormulaValidationError):
            self.engine.validate("__import__('os')")

    def test_reject_unknown_function(self):
        with pytest.raises(FormulaValidationError):
            self.engine.validate("print(x)")

    def test_reject_unknown_variable(self):
        with pytest.raises(FormulaValidationError):
            self.engine.validate("y + 1")

    def test_reject_os_access(self):
        with pytest.raises(FormulaValidationError):
            self.engine.validate("os.system('ls')")

    def test_reject_syntax_error(self):
        with pytest.raises(FormulaValidationError, match="语法错误"):
            self.engine.validate("x +")


class TestCompileAndEvaluate:
    def setup_method(self):
        self.engine = FormulaEngine()

    def test_evaluate_linear(self):
        self.engine.validate_and_compile("x")
        assert self.engine.evaluate("x", 0.5) == pytest.approx(0.5)

    def test_evaluate_sigmoid(self):
        expr = "1 / (1 + math.exp(-10 * (x - 0.5)))"
        self.engine.validate_and_compile(expr)
        # x=0.5 => sigmoid 中心 => ~0.5
        assert self.engine.evaluate(expr, 0.5) == pytest.approx(0.5)
        # x=1.0 => 接近 1
        assert self.engine.evaluate(expr, 1.0) > 0.99

    def test_evaluate_sqrt(self):
        self.engine.validate_and_compile("math.pow(x, 0.5)")
        assert self.engine.evaluate("math.pow(x, 0.5)", 0.25) == pytest.approx(0.5)

    def test_sample(self):
        self.engine.validate_and_compile("x")
        points = self.engine.sample("x", n_points=11)
        assert len(points) == 11
        assert points[0] == pytest.approx((0.0, 0.0))
        assert points[-1] == pytest.approx((1.0, 1.0))

    def test_cache_reuse(self):
        expr = "x * 2"
        self.engine.validate_and_compile(expr)
        self.engine.validate_and_compile(expr)  # 应命中缓存
        assert self.engine.evaluate(expr, 0.5) == pytest.approx(1.0)
