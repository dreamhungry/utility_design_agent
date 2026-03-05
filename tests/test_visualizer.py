"""可视化模块测试"""

import tempfile
from pathlib import Path

import pytest

from utility_design_agent.models import NPCCurveConfig, UtilityFunction
from utility_design_agent.visualizer import Visualizer


class TestVisualizer:
    def setup_method(self):
        self.viz = Visualizer(n_points=50)

    def test_plot_single(self, sample_utility_functions):
        uf = sample_utility_functions[0]
        fig = self.viz.plot_single(uf)
        assert fig is not None

    def test_plot_comparison(self, sample_utility_functions):
        fig = self.viz.plot_comparison(sample_utility_functions, title="Test")
        assert fig is not None

    def test_plot_npc_summary(self, sample_curve_config):
        fig = self.viz.plot_npc_summary(sample_curve_config)
        assert fig is not None

    def test_plot_npc_summary_empty(self):
        cfg = NPCCurveConfig(npc_name="空NPC")
        fig = self.viz.plot_npc_summary(cfg)
        assert fig is not None

    def test_save_png(self, sample_utility_functions):
        uf = sample_utility_functions[0]
        fig = self.viz.plot_single(uf)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = self.viz.save(fig, Path(tmpdir) / "test.png", fmt="png")
            assert out.exists()
            assert out.suffix == ".png"

    def test_save_svg(self, sample_utility_functions):
        uf = sample_utility_functions[0]
        fig = self.viz.plot_single(uf)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = self.viz.save(fig, Path(tmpdir) / "test.svg", fmt="svg")
            assert out.exists()
            assert out.suffix == ".svg"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
