"""JSON 配置与采样数据导出模块"""

from __future__ import annotations

import json
from pathlib import Path

from .formula_engine import FormulaEngine
from .models import NPCCurveConfig


class Exporter:
    """将 NPCCurveConfig 导出为 JSON 配置文件和采样数据文件"""

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.engine = FormulaEngine()

    def export(
        self,
        configs: list[NPCCurveConfig],
        *,
        config_filename: str = "npc_curves.json",
        samples_filename: str = "curve_samples.json",
        n_points: int = 200,
    ) -> tuple[Path, Path]:
        """导出配置和采样数据

        Args:
            configs: NPC 曲线配置列表
            config_filename: 配置文件名
            samples_filename: 采样数据文件名
            n_points: 每条曲线采样点数

        Returns:
            (config_path, samples_path) 导出文件路径元组
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 配置文件
        config_data = [cfg.model_dump(mode="json") for cfg in configs]
        config_path = self.output_dir / config_filename
        config_path.write_text(
            json.dumps(config_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 2. 采样数据
        samples_data: list[dict] = []
        for cfg in configs:
            npc_samples: dict = {
                "npc_name": cfg.npc_name,
                "curves": [],
            }
            for uf in cfg.utility_functions:
                self.engine.validate_and_compile(uf.formula)
                points = self.engine.sample(
                    uf.formula,
                    n_points=n_points,
                    x_min=uf.input_range[0],
                    x_max=uf.input_range[1],
                )
                npc_samples["curves"].append({
                    "behavior": uf.behavior,
                    "formula": uf.formula,
                    "points": [{"x": p[0], "y": p[1]} for p in points],
                })
            samples_data.append(npc_samples)

        samples_path = self.output_dir / samples_filename
        samples_path.write_text(
            json.dumps(samples_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return config_path, samples_path
