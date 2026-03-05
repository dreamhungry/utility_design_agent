"""matplotlib 曲线可视化模块"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

import matplotlib
import matplotlib.pyplot as plt

from .formula_engine import FormulaEngine
from .models import NPCCurveConfig, UtilityFunction

# 使用非交互式后端
matplotlib.use("Agg")

# 中文字体支持
import platform as _platform

if _platform.system() == "Windows":
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
else:
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


class Visualizer:
    """效用函数曲线可视化"""

    def __init__(self, n_points: int = 200) -> None:
        self.n_points = n_points
        self.engine = FormulaEngine()

    # ------------------------------------------------------------------
    # 单曲线
    # ------------------------------------------------------------------

    def plot_single(
        self,
        uf: UtilityFunction,
        *,
        title: str | None = None,
        figsize: tuple[float, float] = (8, 5),
    ) -> plt.Figure:
        """绘制单条效用函数曲线"""
        points = self.engine.sample(
            self.engine.validate_and_compile(uf.formula),
            n_points=self.n_points,
            x_min=uf.input_range[0],
            x_max=uf.input_range[1],
        )
        xs, ys = zip(*points)

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(xs, ys, linewidth=2)
        ax.set_xlabel("Input (x)")
        ax.set_ylabel("Utility (y)")
        ax.set_title(title or f"Utility: {uf.behavior}")
        ax.set_xlim(uf.input_range)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # 多曲线对比
    # ------------------------------------------------------------------

    def plot_comparison(
        self,
        utility_functions: list[UtilityFunction],
        *,
        title: str = "Utility Comparison",
        figsize: tuple[float, float] = (10, 6),
    ) -> plt.Figure:
        """在同一坐标系中叠加多条行为曲线"""
        fig, ax = plt.subplots(figsize=figsize)

        for uf in utility_functions:
            points = self.engine.sample(
                self.engine.validate_and_compile(uf.formula),
                n_points=self.n_points,
                x_min=uf.input_range[0],
                x_max=uf.input_range[1],
            )
            xs, ys = zip(*points)
            ax.plot(xs, ys, linewidth=2, label=uf.behavior)

        ax.set_xlabel("Input (x)")
        ax.set_ylabel("Utility (y)")
        ax.set_title(title)
        ax.set_ylim(-0.05, 1.05)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # NPC 全行为汇总
    # ------------------------------------------------------------------

    def plot_npc_summary(
        self,
        config: NPCCurveConfig,
        *,
        figsize_per_subplot: tuple[float, float] = (5, 4),
    ) -> plt.Figure:
        """为单个 NPC 生成包含所有行为曲线的汇总图"""
        n = len(config.utility_functions)
        if n == 0:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, "No utility functions", ha="center", va="center")
            return fig

        cols = min(n, 3)
        rows = math.ceil(n / cols)
        fig, axes = plt.subplots(
            rows, cols,
            figsize=(figsize_per_subplot[0] * cols, figsize_per_subplot[1] * rows),
            squeeze=False,
        )

        for idx, uf in enumerate(config.utility_functions):
            r, c = divmod(idx, cols)
            ax = axes[r][c]
            points = self.engine.sample(
                self.engine.validate_and_compile(uf.formula),
                n_points=self.n_points,
                x_min=uf.input_range[0],
                x_max=uf.input_range[1],
            )
            xs, ys = zip(*points)
            ax.plot(xs, ys, linewidth=2)
            ax.set_title(uf.behavior)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, alpha=0.3)

        # 隐藏多余子图
        for idx in range(n, rows * cols):
            r, c = divmod(idx, cols)
            axes[r][c].set_visible(False)

        fig.suptitle(f"NPC: {config.npc_name}", fontsize=14, fontweight="bold")
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # 保存辅助
    # ------------------------------------------------------------------

    @staticmethod
    def save(
        fig: plt.Figure,
        path: str | Path,
        fmt: Literal["png", "svg"] = "png",
        dpi: int = 150,
    ) -> Path:
        """保存图片到文件"""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(out), format=fmt, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return out
