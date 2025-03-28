from pathlib import Path
from typing import Optional
import typer
import traceback
from .converter import convert_file as perform_conversion
from .ai_utils import generate_with_ai
from .knowledge_service import KnowledgeService

app = typer.Typer(help="Design Guard AI 工具集")

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
    """转换单个文件为优化后的Markdown"""
    final_output = output or input_file.with_suffix('.md')
    
    if final_output.suffix.lower() != '.md':
        typer.echo(f"警告：输出文件后缀应为 .md，检测到 {final_output.suffix}", 
                  err=True, color=typer.colors.YELLOW)

    try:
        typer.echo(f"开始转换: {input_file} -> {final_output} ...", color=typer.colors.BLUE)
        perform_conversion(str(input_file), str(final_output))
        typer.echo(f"成功转换: {input_file} -> {final_output}", color=typer.colors.GREEN)
    except Exception as e:
        typer.echo(f"转换失败: {input_file}", err=True, color=typer.colors.RED)
        typer.echo(f"错误详情: {str(e)}", err=True, color=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command(name="ask")
def ask_question(question: str = typer.Argument(..., help="您的问题")):
    """从问答库中获取答案"""
    typer.echo(f"原始问题: '{question}'")

    # 1. 使用 AI 格式化问题
    formatting_prompt = f"""请将以下用户问题格式化，使其更适合在技术知识库中进行检索。
    移除不必要的寒暄，提炼核心技术疑问，不需要 markdown 格式。
    用户问题：{question}
    格式化后的问题："""
    
    typer.echo("正在使用 AI 格式化问题...")
    try:
        formatted_question_stream = generate_with_ai(formatting_prompt)
        formatted_question = "".join(list(formatted_question_stream))
        typer.echo(f"格式化后的问题: '{formatted_question}'")
    except Exception as e:
        traceback.print_exc()
        typer.echo(f"使用 AI 格式化问题时出错: {e}", err=True, color=typer.colors.RED)
        raise typer.Exit(code=1)

    # 2. 使用格式化后的问题查询知识库
    typer.echo("正在查询知识库...")
    try:
        records = KnowledgeService.search_dify(formatted_question)
        if records:
            knowledge = KnowledgeService.format_results(records)
            
            # 使用AI生成友好回答
            answer_prompt = f"""根据以下知识库内容和用户原始问题，生成一个简洁友好的回答：
            
用户问题: {question}
知识库内容:
{knowledge}

知识库内容:
{knowledge}

请用中文回答，保持专业但友好的语气，直接回答问题要点。"""
            
            typer.echo("\n正在生成回答...", color=typer.colors.BLUE)
            try:
                answer_stream = generate_with_ai(answer_prompt)
                answer = "".join(list(answer_stream))
                typer.echo("\n回答:", color=typer.colors.GREEN)
                typer.echo(answer)
            except Exception as e:
                typer.echo(f"回答生成失败: {e}", err=True, color=typer.colors.YELLOW)
                typer.echo("\n知识库原始内容:", color=typer.colors.BLUE)
                typer.echo(knowledge)
        else:
            typer.echo("未找到相关信息", color=typer.colors.YELLOW)
    except Exception as e:
        traceback.print_exc()
        typer.echo(f"知识库查询失败: {e}", err=True, color=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()
