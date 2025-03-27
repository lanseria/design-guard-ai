from pathlib import Path
from typing import Optional
from google.genai import types
import typer
from markitdown import MarkItDown
from .const import (
    GEMINI_API_KEY,  # 新增Google API密钥
    LLM_MODEL
)

app = typer.Typer(help="Markdown转换工具")

def get_ai_client():
    """根据配置获取AI客户端"""
    try:
        from google import genai
    except ImportError:
        raise RuntimeError("请先安装Google AI库: pip install google-genai")
    # 配置Google客户端
    return genai.Client(api_key=GEMINI_API_KEY)

def generate_with_ai(prompt: str):
    """通用AI生成接口"""
    client = get_ai_client()
    response = []
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )
    try:
        # Google AI生成流式响应
        for chunk in client.models.generate_content_stream(
            model=LLM_MODEL,
            contents=[{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            config=generate_content_config
        ):
            if chunk.text:
                response.append(chunk.text)
                yield chunk.text
    except Exception as e:
        print(f"AI Generation Error: {e}") #可选： 打印错误信息到控制台
        raise  # 重新抛出异常，让上层函数处理

    return "".join(response)

def convert_file(input_path: str, output_path: str):
    """文件转换核心函数"""
    # 初始化AI客户端
    try:
        ai_client = get_ai_client()
    except (ImportError, ValueError) as e:
        raise RuntimeError(str(e))

    md = MarkItDown()
    # 执行转换
    try:
        result = md.convert(input_path)
        raw_markdown = result.markdown
    except Exception as e:
        raise RuntimeError(f"Markdown Conversion Error: {e}")

    # 使用优化后的 Prompt
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
{}"""  # 使用 format 格式化字符串

    try:
        optimized_content = "".join(
            generate_with_ai(prompt.format(raw_markdown))  # 将 raw_markdown 插入到 prompt 中
        )
    except Exception as e:
        raise RuntimeError(f"AI Optimization Error: {e}")

    # 写入文件
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if optimized_content:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
    else:
        print("Warning: AI returned empty content.  No file written.")

@app.command(name="convert")
def convert(
    input_file: Path = typer.Argument(
        ...,
        help="输入文件路径",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o", "--output",
        help="输出Markdown文件路径",
        file_okay=True,
        dir_okay=False,
        writable=True
    )
):
    """转换单个文件为Markdown"""
    # 路径验证
    if not input_file.exists():
        typer.echo(f"错误：输入文件 {input_file} 不存在", err=True)
        raise typer.Exit(code=2)
    
    # 生成输出路径
    final_output = output or input_file.with_suffix('.md')
    
    # 输出文件后缀检查
    if final_output.suffix.lower() != '.md':
        typer.echo(f"警告：输出文件后缀应为 .md，检测到 {final_output.suffix}", err=True, color=True)
    
    try:
        convert_file(str(input_file), str(final_output))
        typer.echo(f"成功转换: {input_file} -> {final_output}", color=True)
    except Exception as e:
        typer.echo(f"转换失败: {str(e)}", err=True, color=True)
        raise typer.Exit(code=1)

@app.command(name="legacy-convert")
def legacy_convert():
    """兼容旧版计算命令"""
    typer.run(convert)

if __name__ == '__main__':
    app()