"""JSON 导出测试"""

import json
import tempfile
from pathlib import Path

import pytest

from utility_design_agent.exporter import Exporter
from utility_design_agent.models import NPCCurveConfig


class TestExporter:
    def test_export_creates_files(self, sample_curve_config: NPCCurveConfig):
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(output_dir=tmpdir)
            config_path, samples_path = exporter.export([sample_curve_config])

            assert config_path.exists()
            assert samples_path.exists()

    def test_export_config_content(self, sample_curve_config: NPCCurveConfig):
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(output_dir=tmpdir)
            config_path, _ = exporter.export([sample_curve_config])

            data = json.loads(config_path.read_text(encoding="utf-8"))
            assert len(data) == 1
            assert data[0]["npc_name"] == "哥布林"
            assert len(data[0]["utility_functions"]) == 2

    def test_export_samples_content(self, sample_curve_config: NPCCurveConfig):
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(output_dir=tmpdir)
            _, samples_path = exporter.export([sample_curve_config], n_points=10)

            data = json.loads(samples_path.read_text(encoding="utf-8"))
            assert len(data) == 1
            curves = data[0]["curves"]
            assert len(curves) == 2
            # 每条曲线应有 10 个采样点
            assert len(curves[0]["points"]) == 10

    def test_export_empty_configs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = Exporter(output_dir=tmpdir)
            config_path, samples_path = exporter.export([])

            data = json.loads(config_path.read_text(encoding="utf-8"))
            assert data == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
