from pathlib import Path
from markitdown import MarkItDown
from .ai_utils import generate_with_ai

def convert_file(input_path: str, output_path: str):
    """
    文件转换核心函数：
    1. 使用 MarkItDown 将输入文件转换为 Markdown。
    2. 使用 AI 优化生成的 Markdown。
    3. 将优化后的内容写入输出文件。
    """
    md = MarkItDown()
    # 执行初始转换
    try:
        result = md.convert(input_path)
        raw_markdown = result.markdown
        if not raw_markdown:
            print(f"Warning: MarkItDown returned empty content for {input_path}. Skipping AI optimization.")
            # 可以选择写入空文件或直接返回
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("") # 写入空内容
            return # 提前返回
    except Exception as e:
        raise RuntimeError(f"Markdown Conversion Error for {input_path}: {e}")

    # 使用优化后的 Prompt 进行 AI 优化
    prompt = """你是专业的 Markdown 文档格式化助手。
你的任务是：
1.  接收一段文本内容。
2.  判断该文本是否已经是 Markdown 格式。
3.  如果不是，则将其转换为结构良好的 Markdown 格式。
4.  如果是，则进行必要的优化（例如：修复格式错误、调整标题级别、添加缺失的换行符）。
5.  确保输出的 Markdown 文档：
    *   具有清晰的标题结构（使用 #, ##, ### 等）。
    *   正确使用列表（有序列表和无序列表）。
    *   代码块使用正确的语法高亮。
    *   段落之间有适当的空行。
    *   链接和图片格式正确。
    *   避免任何多余的解释性文字。
只返回格式化后的 Markdown 内容，不要包含任何其他说明。

输入文本：
{}"""

    optimized_content_parts = []
    try:
        # AI 生成是流式的，需要收集所有部分
        for part in generate_with_ai(prompt.format(raw_markdown)):
            optimized_content_parts.append(part)
        optimized_content = "".join(optimized_content_parts)

    except Exception as e:
        # 如果 AI 优化失败，可以选择回退到原始 Markdown 或抛出错误
        print(f"Warning: AI Optimization Error for {input_path}: {e}. Falling back to raw Markdown.")
        optimized_content = raw_markdown # 回退到原始 Markdown
        # 或者直接抛出错误: raise RuntimeError(f"AI Optimization Error for {input_path}: {e}")

    # 写入文件
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if optimized_content:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
    else:
        # 即使 AI 优化失败并回退，raw_markdown 也可能为空
        print(f"Warning: Final content for {output_path} is empty. Writing empty file.")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("") # 写入空内容
