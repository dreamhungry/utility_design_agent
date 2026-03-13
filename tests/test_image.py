"""测试大模型 Vision API 图片处理性能

功能：
- 测试带图片的 API 调用速度
- 支持流式和非流式输出对比
- 支持多张图片同时发送
- 详细的性能统计（首字时间、总耗时、速度等）
"""

import asyncio
import base64
import os
import sys
import time
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI, OpenAI

# 设置输出编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ============================================================================
# 配置
# ============================================================================

API_KEY = os.getenv("OPENAI_API_KEY", "sk-28AWdj18YUvUwtF-nW2Rhw")
API_BASE = os.getenv("OPENAI_API_BASE", "http://litellm.sgra.woa.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "kimi-k2.5")

# 测试图片路径（请替换为实际图片）
TEST_IMAGE_PATH = "output/charts/test.png"  # 使用项目中已有的图片
TEST_PROMPT = "请描述一下你在这张图里看到了些什么，如果涉及到物体请描述出它们的空间关系（比如桌子在床的左边，在人的右边这样的）"


# ============================================================================
# 工具函数
# ============================================================================

def encode_image(image_path: str | Path) -> str:
    """将图片编码为 base64 字符串"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_size(image_path: str | Path) -> int:
    """获取图片文件大小（字节）"""
    return Path(image_path).stat().st_size


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """格式化时间"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    return f"{seconds:.2f}s"


# ============================================================================
# 测试1: 非流式调用（同步）
# ============================================================================

def test_sync_non_stream(image_path: str, prompt: str) -> dict[str, Any]:
    """测试同步非流式调用"""
    print("\n" + "=" * 70)
    print("测试1: 非流式调用（同步）")
    print("=" * 70)
    
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    
    # 编码图片
    print(f"正在编码图片: {image_path}")
    encode_start = time.time()
    base64_image = encode_image(image_path)
    encode_time = time.time() - encode_start
    
    image_size = get_image_size(image_path)
    base64_size = len(base64_image)
    
    print(f"  - 原始大小: {format_size(image_size)}")
    print(f"  - Base64 大小: {format_size(base64_size)}")
    print(f"  - 编码耗时: {format_duration(encode_time)}")
    
    # 发送请求
    print(f"\n正在调用 API (model={MODEL})...")
    api_start = time.time()
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    
    api_time = time.time() - api_start
    
    # 解析响应
    content = response.choices[0].message.content or ""
    total_tokens = response.usage.total_tokens if response.usage else 0
    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
    completion_tokens = response.usage.completion_tokens if response.usage else 0
    
    # 统计
    print("\n[结果]")
    print(f"  - API 耗时: {format_duration(api_time)}")
    print(f"  - 总耗时: {format_duration(encode_time + api_time)}")
    print(f"  - 响应长度: {len(content)} 字符")
    print(f"  - Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")
    if api_time > 0:
        print(f"  - 生成速度: {completion_tokens / api_time:.1f} tokens/s")
    
    print(f"\n[响应内容预览]")
    preview = content[:300] + "..." if len(content) > 300 else content
    print(f"{preview}")
    
    return {
        "method": "sync_non_stream",
        "encode_time": encode_time,
        "api_time": api_time,
        "total_time": encode_time + api_time,
        "content_length": len(content),
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


# ============================================================================
# 测试2: 流式调用（同步）
# ============================================================================

def test_sync_stream(image_path: str, prompt: str) -> dict[str, Any]:
    """测试同步流式调用"""
    print("\n" + "=" * 70)
    print("测试2: 流式调用（同步）")
    print("=" * 70)
    
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    
    # 编码图片
    print(f"正在编码图片: {image_path}")
    encode_start = time.time()
    base64_image = encode_image(image_path)
    encode_time = time.time() - encode_start
    print(f"  - 编码耗时: {format_duration(encode_time)}")
    
    # 发送请求
    print(f"\n正在调用 API (model={MODEL}, stream=True)...")
    api_start = time.time()
    first_chunk_time = None
    
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1000,
        stream=True,
        stream_options={"include_usage": True},  # 请求返回 usage 信息
    )
    
    print("\n[流式输出]")
    print("-" * 70)
    
    full_content = ""
    chunk_count = 0
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    
    for chunk in stream:
        if first_chunk_time is None:
            first_chunk_time = time.time() - api_start
        
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            print(content, end="", flush=True)
            chunk_count += 1
        
        # 流式响应的最后一个 chunk 包含 usage 信息
        if hasattr(chunk, 'usage') and chunk.usage:
            total_tokens = chunk.usage.total_tokens
            prompt_tokens = chunk.usage.prompt_tokens
            completion_tokens = chunk.usage.completion_tokens
    
    api_time = time.time() - api_start
    
    print("\n" + "-" * 70)
    
    # 统计
    print("\n[结果]")
    print(f"  - 首字时间 (TTFT): {format_duration(first_chunk_time or 0)}")
    print(f"  - API 总耗时: {format_duration(api_time)}")
    print(f"  - 总耗时: {format_duration(encode_time + api_time)}")
    print(f"  - 响应长度: {len(full_content)} 字符")
    print(f"  - 收到 chunks: {chunk_count}")
    print(f"  - Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")
    if api_time > 0 and completion_tokens > 0:
        print(f"  - 生成速度: {completion_tokens / api_time:.1f} tokens/s")
    
    return {
        "method": "sync_stream",
        "encode_time": encode_time,
        "first_chunk_time": first_chunk_time or 0,
        "api_time": api_time,
        "total_time": encode_time + api_time,
        "content_length": len(full_content),
        "chunk_count": chunk_count,
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


# ============================================================================
# 测试3: 异步非流式调用
# ============================================================================

async def test_async_non_stream(image_path: str, prompt: str) -> dict[str, Any]:
    """测试异步非流式调用"""
    print("\n" + "=" * 70)
    print("测试3: 异步非流式调用")
    print("=" * 70)
    
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE)
    
    # 编码图片
    print(f"正在编码图片: {image_path}")
    encode_start = time.time()
    base64_image = encode_image(image_path)
    encode_time = time.time() - encode_start
    print(f"  - 编码耗时: {format_duration(encode_time)}")
    
    # 发送请求
    print(f"\n正在调用 API (model={MODEL}, async)...")
    api_start = time.time()
    
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    
    api_time = time.time() - api_start
    
    # 解析响应
    content = response.choices[0].message.content or ""
    total_tokens = response.usage.total_tokens if response.usage else 0
    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
    completion_tokens = response.usage.completion_tokens if response.usage else 0
    
    print("\n[结果]")
    print(f"  - API 耗时: {format_duration(api_time)}")
    print(f"  - 总耗时: {format_duration(encode_time + api_time)}")
    print(f"  - 响应长度: {len(content)} 字符")
    print(f"  - Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")
    if api_time > 0 and completion_tokens > 0:
        print(f"  - 生成速度: {completion_tokens / api_time:.1f} tokens/s")
    
    return {
        "method": "async_non_stream",
        "encode_time": encode_time,
        "api_time": api_time,
        "total_time": encode_time + api_time,
        "content_length": len(content),
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


# ============================================================================
# 测试4: 异步流式调用
# ============================================================================

async def test_async_stream(image_path: str, prompt: str) -> dict[str, Any]:
    """测试异步流式调用"""
    print("\n" + "=" * 70)
    print("测试4: 异步流式调用")
    print("=" * 70)
    
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE)
    
    # 编码图片
    print(f"正在编码图片: {image_path}")
    encode_start = time.time()
    base64_image = encode_image(image_path)
    encode_time = time.time() - encode_start
    print(f"  - 编码耗时: {format_duration(encode_time)}")
    
    # 发送请求
    print(f"\n正在调用 API (model={MODEL}, stream=True, async)...")
    api_start = time.time()
    first_chunk_time = None
    
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=1000,
        stream=True,
        stream_options={"include_usage": True},  # 请求返回 usage 信息
    )
    
    print("\n[流式输出]")
    print("-" * 70)
    
    full_content = ""
    chunk_count = 0
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    
    async for chunk in stream:
        if first_chunk_time is None:
            first_chunk_time = time.time() - api_start
        
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            print(content, end="", flush=True)
            chunk_count += 1
        
        # 流式响应的最后一个 chunk 包含 usage 信息
        if hasattr(chunk, 'usage') and chunk.usage:
            total_tokens = chunk.usage.total_tokens
            prompt_tokens = chunk.usage.prompt_tokens
            completion_tokens = chunk.usage.completion_tokens
    
    api_time = time.time() - api_start
    
    print("\n" + "-" * 70)
    
    # 统计
    print("\n[结果]")
    print(f"  - 首字时间 (TTFT): {format_duration(first_chunk_time or 0)}")
    print(f"  - API 总耗时: {format_duration(api_time)}")
    print(f"  - 总耗时: {format_duration(encode_time + api_time)}")
    print(f"  - 响应长度: {len(full_content)} 字符")
    print(f"  - 收到 chunks: {chunk_count}")
    print(f"  - Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")
    if api_time > 0 and completion_tokens > 0:
        print(f"  - 生成速度: {completion_tokens / api_time:.1f} tokens/s")
    
    return {
        "method": "async_stream",
        "encode_time": encode_time,
        "first_chunk_time": first_chunk_time or 0,
        "api_time": api_time,
        "total_time": encode_time + api_time,
        "content_length": len(full_content),
        "chunk_count": chunk_count,
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


# ============================================================================
# 测试5: 多图片并发测试（非流式）
# ============================================================================

async def test_multiple_images(image_paths: list[str], prompt: str) -> dict[str, Any]:
    """测试多张图片同时发送（非流式）"""
    print("\n" + "=" * 70)
    print(f"测试5: 多图片并发测试 - 非流式 ({len(image_paths)} 张图片)")
    print("=" * 70)
    
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE)
    
    # 编码所有图片
    print("正在编码所有图片...")
    encode_start = time.time()
    content_parts = [{"type": "text", "text": prompt}]
    
    for idx, img_path in enumerate(image_paths, 1):
        if not Path(img_path).exists():
            print(f"  - 警告: 图片 {img_path} 不存在，跳过")
            continue
        
        base64_image = encode_image(img_path)
        img_size = get_image_size(img_path)
        print(f"  - 图片 {idx}: {Path(img_path).name} ({format_size(img_size)})")
        
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
    
    encode_time = time.time() - encode_start
    print(f"  - 总编码耗时: {format_duration(encode_time)}")
    
    # 发送请求
    print(f"\n正在调用 API (model={MODEL})...")
    api_start = time.time()
    
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content_parts}],
        temperature=0.7,
        max_tokens=2000,
    )
    
    api_time = time.time() - api_start
    
    # 解析响应
    content = response.choices[0].message.content or ""
    total_tokens = response.usage.total_tokens if response.usage else 0
    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
    completion_tokens = response.usage.completion_tokens if response.usage else 0
    
    print("\n[结果]")
    print(f"  - API 耗时: {format_duration(api_time)}")
    print(f"  - 总耗时: {format_duration(encode_time + api_time)}")
    print(f"  - 响应长度: {len(content)} 字符")
    print(f"  - Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")
    if api_time > 0 and completion_tokens > 0:
        print(f"  - 生成速度: {completion_tokens / api_time:.1f} tokens/s")
    
    print(f"\n[响应内容预览]")
    preview = content[:400] + "..." if len(content) > 400 else content
    print(f"{preview}")
    
    return {
        "method": "multiple_images",
        "image_count": len(image_paths),
        "encode_time": encode_time,
        "api_time": api_time,
        "total_time": encode_time + api_time,
        "content_length": len(content),
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


# ============================================================================
# 测试6: 多图片并发测试（流式）
# ============================================================================

async def test_multiple_images_stream(image_paths: list[str], prompt: str) -> dict[str, Any]:
    """测试多张图片同时发送（流式）"""
    print("\n" + "=" * 70)
    print(f"测试6: 多图片并发测试 - 流式 ({len(image_paths)} 张图片)")
    print("=" * 70)
    
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE)
    
    # 编码所有图片
    print("正在编码所有图片...")
    encode_start = time.time()
    content_parts = [{"type": "text", "text": prompt}]
    
    for idx, img_path in enumerate(image_paths, 1):
        if not Path(img_path).exists():
            print(f"  - 警告: 图片 {img_path} 不存在，跳过")
            continue
        
        base64_image = encode_image(img_path)
        img_size = get_image_size(img_path)
        print(f"  - 图片 {idx}: {Path(img_path).name} ({format_size(img_size)})")
        
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
    
    encode_time = time.time() - encode_start
    print(f"  - 总编码耗时: {format_duration(encode_time)}")
    
    # 发送请求
    print(f"\n正在调用 API (model={MODEL}, stream=True)...")
    api_start = time.time()
    first_chunk_time = None
    
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content_parts}],
        temperature=0.7,
        max_tokens=2000,
        stream=True,
        stream_options={"include_usage": True},  # 请求返回 usage 信息
    )
    
    print("\n[流式输出]")
    print("-" * 70)
    
    full_content = ""
    chunk_count = 0
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    
    async for chunk in stream:
        if first_chunk_time is None:
            first_chunk_time = time.time() - api_start
        
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            print(content, end="", flush=True)
            chunk_count += 1
        
        # 流式响应的最后一个 chunk 包含 usage 信息
        if hasattr(chunk, 'usage') and chunk.usage:
            total_tokens = chunk.usage.total_tokens
            prompt_tokens = chunk.usage.prompt_tokens
            completion_tokens = chunk.usage.completion_tokens
    
    api_time = time.time() - api_start
    
    print("\n" + "-" * 70)
    
    # 统计
    print("\n[结果]")
    print(f"  - 首字时间 (TTFT): {format_duration(first_chunk_time or 0)}")
    print(f"  - API 总耗时: {format_duration(api_time)}")
    print(f"  - 总耗时: {format_duration(encode_time + api_time)}")
    print(f"  - 响应长度: {len(full_content)} 字符")
    print(f"  - 收到 chunks: {chunk_count}")
    print(f"  - Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens})")
    if api_time > 0 and completion_tokens > 0:
        print(f"  - 生成速度: {completion_tokens / api_time:.1f} tokens/s")
    
    return {
        "method": "multiple_images_stream",
        "image_count": len(image_paths),
        "encode_time": encode_time,
        "first_chunk_time": first_chunk_time or 0,
        "api_time": api_time,
        "total_time": encode_time + api_time,
        "content_length": len(full_content),
        "chunk_count": chunk_count,
        "tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


# ============================================================================
# 主测试函数
# ============================================================================

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("OpenAI Vision API 性能测试")
    print("=" * 70)
    print(f"API Base: {API_BASE}")
    print(f"Model: {MODEL}")
    print(f"Test Image: {TEST_IMAGE_PATH}")
    
    # 检查测试图片是否存在
    if not Path(TEST_IMAGE_PATH).exists():
        print(f"\n[错误] 测试图片不存在: {TEST_IMAGE_PATH}")
        print("请修改脚本中的 TEST_IMAGE_PATH 指向一个有效的图片文件")
        return
    
    results = []
    
    try:
        # 测试1: 同步非流式
        result1 = test_sync_non_stream(TEST_IMAGE_PATH, TEST_PROMPT)
        results.append(result1)
        
        # 测试2: 同步流式
        result2 = test_sync_stream(TEST_IMAGE_PATH, TEST_PROMPT)
        results.append(result2)
        
        # 测试3: 异步非流式
        result3 = await test_async_non_stream(TEST_IMAGE_PATH, TEST_PROMPT)
        results.append(result3)
        
        # 测试4: 异步流式
        result4 = await test_async_stream(TEST_IMAGE_PATH, TEST_PROMPT)
        results.append(result4)
        
        # 测试5和6: 多图片测试（如果有其他图片）
        all_images = list(Path("output/charts").glob("*.png"))[:3]  # 最多3张
        if len(all_images) > 1:
            # 测试5: 多图片非流式
            result5 = await test_multiple_images(
                [str(p) for p in all_images],
                "请分别描述这些图片的内容"
            )
            results.append(result5)
            
            # 测试6: 多图片流式
            result6 = await test_multiple_images_stream(
                [str(p) for p in all_images],
                "请分别描述这些图片的内容"
            )
            results.append(result6)
        
    except Exception as e:
        print(f"\n[错误] 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 打印性能对比总结
    print("\n" + "=" * 70)
    print("性能对比总结")
    print("=" * 70)
    print(f"{'方法':<20} {'总耗时':<12} {'API耗时':<12} {'首字时间':<12} {'Total Tokens':<15} {'输入Tokens':<12} {'输出Tokens':<12}")
    print("-" * 70)
    
    for result in results:
        method = result['method']
        total = format_duration(result['total_time'])
        api = format_duration(result['api_time'])
        ttft = format_duration(result.get('first_chunk_time', 0)) if 'first_chunk_time' in result else "N/A"
        total_tokens = result.get('tokens', 0)
        prompt_tokens = result.get('prompt_tokens', 0)
        completion_tokens = result.get('completion_tokens', 0)
        print(f"{method:<20} {total:<12} {api:<12} {ttft:<12} {total_tokens:<15} {prompt_tokens:<12} {completion_tokens:<12}")


# ============================================================================
# 入口
# ============================================================================

if __name__ == "__main__":
    asyncio.run(run_all_tests())