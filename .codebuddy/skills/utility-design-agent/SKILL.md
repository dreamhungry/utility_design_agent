---
name: utility-design-agent
description: >
  This skill provides guidance for using the utility-design-agent library to auto-generate
  NPC utility functions for game AI. It should be used when working with NPC behavior design,
  utility function generation from natural language descriptions, or integrating the
  utility-design-agent library into game projects. Covers data source configuration (Feishu/Excel/CSV/Dict),
  LLM backend setup, AST-safe formula generation, JSON export, and matplotlib visualization.
---

# Utility Design Agent Skill

## Purpose

Guide the usage of the `utility-design-agent` Python library for automatically generating NPC utility functions from personality descriptions. The library reads NPC design data from multiple sources, generates mathematical expressions via LLM, validates them through AST whitelisting, and outputs standardized JSON configs with visualization.

## When to Use

- Setting up NPC behavior utility function generation pipelines
- Configuring data sources (Feishu Sheets, Excel/CSV, in-memory dict)
- Integrating the library into game AI projects
- Customizing Prompt templates for different game genres
- Troubleshooting formula validation or LLM output issues

## Library API Quick Reference

### Installation

```bash
pip install utility-design-agent
```

### Core Imports

```python
from utility_design_agent import (
    FormulaEngine, FeishuReader, LocalReader, DictReader, create_reader,
    create_llm_backend, PromptBuilder, Exporter, Visualizer,
    NPCData, UtilityFunction, NPCCurveConfig, AppConfig,
)
```

### Data Sources

Three reader types are available, all sharing the `BaseReader` interface:

1. **FeishuReader** — Read from Feishu online spreadsheets via Sheets API
   ```python
   reader = FeishuReader(app_id="xxx", app_secret="xxx")
   npcs = await reader.read(spreadsheet_token="xxx", sheet_id="xxx")
   ```

2. **LocalReader** — Read from local .xlsx or .csv files
   ```python
   reader = LocalReader()
   npcs = await reader.read(path="npcs.xlsx")
   ```

3. **DictReader** — Build NPCData directly from in-memory dicts
   ```python
   reader = DictReader()
   npcs = await reader.read(data=[
       {"name": "Goblin", "personality_tags": ["timid", "greedy"],
        "needs": ["flee", "loot"], "design_intent": "..."},
   ])
   ```

Use `create_reader(source_type, **kwargs)` factory function to create readers dynamically.

### Spreadsheet Column Naming

Auto-detection supports these column names (case-insensitive):
- **Name**: `NPC名称`, `name`, `npc_name`, `名称`, `npc`
- **Personality Tags**: `性格标签`, `personality_tags`, `personality`, `标签`
- **Needs**: `需求`, `needs`, `behavior`, `偏好`
- **Design Intent**: `设计意图`, `design_intent`, `intent`, `意图`

Tags can be separated by: `、` `,` `，` `;` `；`

### LLM Backend

Two backends are supported:

```python
# OpenAI native SDK (supports custom api_base for proxies)
backend = create_llm_backend("openai", api_key="xxx", api_base="https://...", model="gpt-4o")

# LiteLLM universal interface
backend = create_llm_backend("litellm", api_key="xxx", model="gpt-4o")
```

### Formula Engine — AST Whitelist

The formula engine validates LLM-generated expressions against a strict whitelist:

- **Allowed math functions**: `math.exp`, `math.log`, `math.log10`, `math.pow`, `math.sqrt`, `math.sin`, `math.cos`, `math.tan`, `math.fabs`
- **Allowed variable**: only `x` (input value, range 0~1)
- **Allowed operators**: `+`, `-`, `*`, `/`, `**`, `//`, `%`
- **Rejected**: any `import`, function calls outside `math.*`, unknown variables

```python
engine = FormulaEngine()
engine.validate_and_compile("1 / (1 + math.exp(-10 * (x - 0.3)))")  # OK
engine.evaluate("1 / (1 + math.exp(-10 * (x - 0.3)))", x=0.5)       # => float
engine.sample("x ** 2", n_points=100)                                  # => [(x, y), ...]
```

### Prompt Customization

Prompt templates are Python string constants in `utility_design_agent.prompts.templates`:

```python
from utility_design_agent.prompts import PromptBuilder, SYSTEM_PROMPT

# Use default prompts
builder = PromptBuilder()

# Override system prompt or few-shot examples
builder = PromptBuilder(
    system_prompt="Custom system prompt...",
    few_shot_examples=[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
)

messages = builder.build(npc_data)  # Returns OpenAI chat messages format
```

### Export and Visualization

```python
# Export JSON configs and sample data
exporter = Exporter(output_dir="output")
config_path, samples_path = exporter.export(configs, n_points=200)

# Visualization
viz = Visualizer()
fig = viz.plot_single(utility_function)           # Single curve
fig = viz.plot_comparison(utility_functions)       # Multi-curve overlay
fig = viz.plot_npc_summary(npc_curve_config)       # NPC summary grid
Visualizer.save(fig, "output/chart.png", fmt="png")
```

### CLI Commands

```bash
# Generate utility functions from local file
utility-design generate --source local --path npcs.xlsx --llm-backend openai --model gpt-4o

# Validate expressions in generated JSON
utility-design validate output/npc_curves.json

# Visualize curves from JSON
utility-design visualize output/npc_curves.json --format png
```

## Troubleshooting

- **FormulaValidationError**: LLM generated an unsafe expression. Check the `reason` field for the specific violation. The system auto-retries up to 3 times with corrective prompts.
- **Column detection failure**: Ensure spreadsheet headers match one of the supported column names listed above.
- **Chinese font warnings in matplotlib**: On Windows, the library auto-configures Microsoft YaHei font. On Linux, install `fonts-wqy-microhei` package.
