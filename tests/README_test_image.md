# Vision API 性能测试脚本使用说明

## 概述

`test_image.py` 是一个全面的 OpenAI Vision API 性能测试脚本，用于评估带图片的 LLM API 调用性能。

## 功能特性

### 1. **多种调用模式测试**
- ✅ 同步非流式调用
- ✅ 同步流式调用
- ✅ 异步非流式调用
- ✅ 异步流式调用
- ✅ 多图片并发测试

### 2. **详细性能指标**
- **编码时间**: 图片 Base64 编码耗时
- **首字时间 (TTFT)**: Time To First Token，流式调用专有指标
- **API 耗时**: 从请求发送到响应完成的时间
- **总耗时**: 包含编码和 API 调用的完整时间
- **生成速度**: tokens/s 或 字符/s
- **Token 统计**: prompt tokens, completion tokens, total tokens

### 3. **流式输出演示**
实时显示 LLM 返回的内容流，直观展示流式响应的体验

### 4. **自动对比总结**
测试结束后自动生成性能对比表格

## 使用方法

### 1. 配置环境变量（可选）

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key"
$env:OPENAI_API_BASE="http://your-api-base/v1"
$env:OPENAI_MODEL="gpt-4o"

# Linux / macOS
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="http://your-api-base/v1"
export OPENAI_MODEL="gpt-4o"
```

### 2. 修改脚本配置（如果需要）

编辑 `test_image.py` 中的配置：

```python
# 配置部分（第 30-37 行）
API_KEY = os.getenv("OPENAI_API_KEY", "sk-28AWdj18YUvUwtF-nW2Rhw")
API_BASE = os.getenv("OPENAI_API_BASE", "http://litellm.sgra.woa.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# 测试图片路径（请替换为实际图片）
TEST_IMAGE_PATH = "output/charts/捏捏扭_curves.png"
TEST_PROMPT = "请详细描述这张图片的内容，包括图表类型、数据趋势等信息。"
```

### 3. 运行测试

```bash
# 在项目根目录运行
python tests/test_image.py

# 或者使用虚拟环境
.\venv\Scripts\python.exe tests\test_image.py  # Windows
source venv/bin/activate && python tests/test_image.py  # Linux/macOS
```

## 输出示例

### 测试1: 非流式调用（同步）
```
======================================================================
测试1: 非流式调用（同步）
======================================================================
正在编码图片: output/charts/捏捏扭_curves.png
  - 原始大小: 45.32 KB
  - Base64 大小: 60.43 KB
  - 编码耗时: 5ms

正在调用 API (model=gpt-4o)...

[结果]
  - API 耗时: 2.34s
  - 总耗时: 2.35s
  - 响应长度: 523 字符
  - Tokens: 1245 (prompt: 1050, completion: 195)
  - 生成速度: 83.3 tokens/s

[响应内容预览]
这张图片展示了一个名为"捏捏扭"的 NPC 的效用函数曲线图...
```

### 测试2: 流式调用（同步）
```
======================================================================
测试2: 流式调用（同步）
======================================================================
正在编码图片: output/charts/捏捏扭_curves.png
  - 编码耗时: 4ms

正在调用 API (model=gpt-4o, stream=True)...

[流式输出]
----------------------------------------------------------------------
这张图片展示了一个名为"捏捏扭"的 NPC 的效用函数曲线图。
图表包含了5个子图，分别展示了不同需求维度的效用函数...
----------------------------------------------------------------------

[结果]
  - 首字时间 (TTFT): 450ms
  - API 总耗时: 2.10s
  - 总耗时: 2.11s
  - 响应长度: 523 字符
  - 收到 chunks: 87
  - 平均速度: 248.8 字符/s
```

### 性能对比总结
```
======================================================================
性能对比总结
======================================================================
方法                   总耗时       API耗时      首字时间    
----------------------------------------------------------------------
sync_non_stream      2.35s        2.34s        N/A         
sync_stream          2.11s        2.10s        450ms       
async_non_stream     2.28s        2.27s        N/A         
async_stream         2.05s        2.04s        420ms       
multiple_images      5.67s        5.45s        N/A         
```

## 性能指标解读

### 1. **首字时间 (TTFT)**
- **定义**: 从发送请求到收到第一个 token 的时间
- **重要性**: 决定用户感知的响应速度
- **优化方向**: 越低越好（通常 < 500ms 体验较佳）

### 2. **总耗时 vs API 耗时**
- **编码耗时**: 通常很小（< 50ms），Base64 编码很快
- **API 耗时**: 主要时间开销，取决于模型、图片大小、输出长度

### 3. **流式 vs 非流式**
- **流式优势**: 
  - 更低的首字时间
  - 更好的用户体验（逐字输出）
  - 可以提前取消长响应
- **非流式优势**:
  - 代码更简单
  - 更容易获取完整 token 统计

### 4. **同步 vs 异步**
- **异步优势**:
  - 支持并发（多个请求同时进行）
  - 不阻塞主线程
  - 更适合 Web 服务
- **同步优势**:
  - 代码更直观
  - 适合脚本和简单工具

## 自定义测试

### 测试不同大小的图片

```python
# 修改 TEST_IMAGE_PATH
TEST_IMAGE_PATH = "path/to/your/large_image.jpg"

# 运行测试，观察编码时间和 API 耗时的变化
```

### 测试多图片场景

```python
# 在 run_all_tests() 中修改
all_images = [
    "image1.png",
    "image2.png",
    "image3.png",
]
result5 = await test_multiple_images(all_images, "描述这些图片的共同点")
```

### 测试不同的 Prompt

```python
# 短 Prompt（快速测试）
TEST_PROMPT = "这是什么？"

# 长 Prompt（详细分析）
TEST_PROMPT = """
请详细分析这张图片，包括：
1. 图表类型和布局
2. 数据趋势和模式
3. 关键发现
4. 可能的改进建议
"""
```

## 常见问题

### Q1: 为什么流式调用的总耗时反而更长？
A: 流式调用在网络传输和处理上有额外开销，但首字时间更短，用户体验更好。

### Q2: 如何减少图片编码时间？
A: 
- 使用较小的图片（压缩或缩放）
- 提前编码并缓存 Base64 字符串
- 使用图片 URL 而非 Base64（如果 API 支持）

### Q3: Token 统计为什么不准确？
A: 图片消耗的 token 数取决于分辨率和内容复杂度，API 会自动计算。

### Q4: 如何测试本地模型？
A: 修改 `API_BASE` 指向本地服务（如 ollama、LM Studio 等）。

## 扩展建议

### 1. 添加批量测试
```python
async def batch_test():
    images = Path("test_images").glob("*.jpg")
    tasks = [test_async_stream(str(img), "描述图片") for img in images]
    results = await asyncio.gather(*tasks)
    # 统计平均性能
```

### 2. 添加成本估算
```python
# 根据 token 数和价格计算成本
def calculate_cost(tokens, price_per_1k=0.03):
    return tokens / 1000 * price_per_1k
```

### 3. 添加错误重试
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def test_with_retry(...):
    # 自动重试失败的请求
```

## 相关资源

- [OpenAI Vision API 文档](https://platform.openai.com/docs/guides/vision)
- [性能优化最佳实践](https://platform.openai.com/docs/guides/rate-limits)
- [流式输出指南](https://platform.openai.com/docs/api-reference/streaming)
