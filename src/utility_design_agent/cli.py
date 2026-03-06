"""Typer CLI 薄壳入口 — 仅参数解析 + 调用库 API"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import AppConfig
from .exporter import Exporter
from .formula_engine import FormulaEngine, FormulaValidationError
from .llm_backend import create_llm_backend
from .models import NPCCurveConfig, UtilityFunction
from .prompts import PromptBuilder
from .readers import create_reader

app = typer.Typer(
    name="utility-design",
    help="NPC 效用函数自动生成工具",
    add_completion=False,
)
console = Console()

logger = logging.getLogger("utility_design_agent")


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(name)s | %(levelname)s | %(message)s")


# ======================================================================
# generate 命令
# ======================================================================


@app.command()
def generate(
    source: str = typer.Option("local", help="数据源类型: feishu | local | dict"),
    path: Optional[str] = typer.Option(None, help="本地文件路径（source=local 时必填）"),
    spreadsheet_token: Optional[str] = typer.Option(None, help="飞书 spreadsheet_token"),
    sheet_id: Optional[str] = typer.Option(None, help="飞书 sheet_id"),
    llm_backend: Optional[str] = typer.Option(None, "--llm-backend", help="LLM 后端: openai | litellm"),
    model: Optional[str] = typer.Option(None, help="LLM 模型名称"),
    api_key: Optional[str] = typer.Option(None, help="LLM API Key"),
    api_base: Optional[str] = typer.Option(None, help="LLM API Base URL"),
    output_dir: str = typer.Option("output", help="输出目录"),
    max_retries: int = typer.Option(3, help="LLM 生成失败重试次数"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """从数据源读取 NPC 数据，通过 LLM 生成效用函数"""
    _setup_logging(verbose)
    config = AppConfig()

    # 合并 CLI 参数与 .env 配置
    backend_type = llm_backend or config.llm_backend
    actual_model = model or config.openai_model
    actual_key = api_key or config.openai_api_key
    actual_base = api_base or config.openai_api_base
    actual_output = output_dir or config.output_dir

    async def _run() -> None:
        # 1. 读取数据
        with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), console=console) as progress:
            task = progress.add_task("读取 NPC 数据...", total=None)
            reader = create_reader(source)
            reader_kwargs = {}
            if source == "local":
                if not path:
                    console.print("[red]source=local 时必须指定 --path 参数[/red]")
                    raise typer.Exit(1)
                reader_kwargs["path"] = path
            elif source == "feishu":
                reader_kwargs["spreadsheet_token"] = spreadsheet_token or config.feishu_app_id
                reader_kwargs["sheet_id"] = sheet_id or ""
            npcs = await reader.read(**reader_kwargs)
            progress.update(task, description=f"已读取 {len(npcs)} 个 NPC")

        if not npcs:
            console.print("[yellow]未读取到任何 NPC 数据[/yellow]")
            raise typer.Exit(0)

        # 显示读取结果
        table = Table(title="NPC 数据")
        table.add_column("名称", style="cyan")
        table.add_column("性格标签", style="green")
        table.add_column("需求", style="magenta")
        for npc in npcs:
            table.add_row(npc.name, ", ".join(npc.personality_tags), ", ".join(npc.needs))
        console.print(table)

        # 2. LLM 生成
        backend = create_llm_backend(backend_type, api_key=actual_key, api_base=actual_base, model=actual_model)
        prompt_builder = PromptBuilder()
        engine = FormulaEngine()

        all_configs: list[NPCCurveConfig] = []

        with Progress(SpinnerColumn(), TextColumn("[bold green]{task.description}"), console=console) as progress:
            task = progress.add_task("生成效用函数...", total=len(npcs))

            for npc in npcs:
                messages = prompt_builder.build(npc)
                utility_functions: list[UtilityFunction] = []

                for attempt in range(1, max_retries + 1):
                    try:
                        raw_response = await backend.generate(messages)
                        # 解析 JSON 响应
                        parsed = _parse_llm_response(raw_response)
                        # 校验每个表达式
                        for item in parsed:
                            formula = item.get("formula", "")
                            engine.validate_and_compile(formula)
                            utility_functions.append(UtilityFunction(**item))
                        break
                    except (FormulaValidationError, json.JSONDecodeError, Exception) as e:
                        logger.warning("NPC [%s] 第 %d 次生成失败: %s", npc.name, attempt, e)
                        if attempt == max_retries:
                            console.print(f"[red]NPC [{npc.name}] 生成失败，已重试 {max_retries} 次[/red]")

                cfg = NPCCurveConfig(
                    npc_name=npc.name,
                    personality_tags=npc.personality_tags,
                    utility_functions=utility_functions,
                ).with_metadata(model=actual_model, backend=backend_type)
                all_configs.append(cfg)
                progress.advance(task)

        # 3. 导出
        exporter = Exporter(output_dir=actual_output)
        config_path, samples_path = exporter.export(all_configs)
        console.print(f"\n[green]配置文件已导出: {config_path}[/green]")
        console.print(f"[green]采样数据已导出: {samples_path}[/green]")

    asyncio.run(_run())


def _parse_llm_response(raw: str) -> list[dict]:
    """从 LLM 响应中提取 JSON 数组"""
    text = raw.strip()
    # 尝试提取 ```json ... ``` 代码块
    if "```" in text:
        start = text.find("```")
        end = text.rfind("```")
        if start != end:
            inner = text[start:end]
            # 去掉首行的 ```json
            lines = inner.split("\n", 1)
            text = lines[1] if len(lines) > 1 else lines[0]
    # 找到 JSON 数组
    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1:
        text = text[bracket_start : bracket_end + 1]
    return json.loads(text)


# ======================================================================
# validate 命令
# ======================================================================


@app.command()
def validate(
    config_file: str = typer.Argument(..., help="JSON 配置文件路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """校验已生成的 JSON 配置文件中表达式的安全性"""
    _setup_logging(verbose)
    filepath = Path(config_file)
    if not filepath.exists():
        console.print(f"[red]文件不存在: {filepath}[/red]")
        raise typer.Exit(1)

    data = json.loads(filepath.read_text(encoding="utf-8"))
    engine = FormulaEngine()
    total = 0
    passed = 0
    failed = 0

    for npc_cfg in data:
        npc_name = npc_cfg.get("npc_name", "unknown")
        for uf in npc_cfg.get("utility_functions", []):
            total += 1
            formula = uf.get("formula", "")
            behavior = uf.get("behavior", "")
            try:
                engine.validate_and_compile(formula)
                passed += 1
                console.print(f"  [green]✓[/green] {npc_name}/{behavior}: {formula}")
            except FormulaValidationError as e:
                failed += 1
                console.print(f"  [red]✗[/red] {npc_name}/{behavior}: {e.reason}")

    console.print(f"\n共 {total} 条表达式，通过 {passed} 条，失败 {failed} 条")
    if failed > 0:
        raise typer.Exit(1)


# ======================================================================
# visualize 命令
# ======================================================================


@app.command()
def visualize(
    config_file: str = typer.Argument(..., help="JSON 配置文件路径"),
    output_dir: str = typer.Option("output", help="图片输出目录"),
    fmt: str = typer.Option("png", "--format", "-f", help="输出格式: png | svg"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """对已生成的 JSON 配置绘制曲线图"""
    _setup_logging(verbose)
    filepath = Path(config_file)
    if not filepath.exists():
        console.print(f"[red]文件不存在: {filepath}[/red]")
        raise typer.Exit(1)

    from .visualizer import Visualizer

    data = json.loads(filepath.read_text(encoding="utf-8"))
    configs = [NPCCurveConfig.model_validate(item) for item in data]
    viz = Visualizer()
    out_dir = Path(output_dir)

    for cfg in configs:
        if not cfg.utility_functions:
            continue

        # NPC 汇总图
        fig = viz.plot_npc_summary(cfg)
        out_path = viz.save(fig, out_dir / f"{cfg.npc_name}_summary.{fmt}", fmt=fmt)  # type: ignore[arg-type]
        console.print(f"[green]已生成: {out_path}[/green]")

        # 多曲线对比图
        if len(cfg.utility_functions) > 1:
            fig = viz.plot_comparison(cfg.utility_functions, title=f"{cfg.npc_name} - 行为对比")
            out_path = viz.save(fig, out_dir / f"{cfg.npc_name}_comparison.{fmt}", fmt=fmt)  # type: ignore[arg-type]
            console.print(f"[green]已生成: {out_path}[/green]")

    console.print(f"\n[green]所有图片已输出到 {out_dir}/[/green]")


if __name__ == "__main__":
    app()
