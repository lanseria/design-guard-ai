from pathlib import Path  
from typing import Optional
import typer
import traceback
from .converter import convert_file as perform_conversion
from .qa_service import QAService
from .pdf_analyzer import PDFAnalyzer

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
        typer.echo(f"警告：输出文件后缀应为 .md，检测到 {final_output.suffix}", err=True, color=typer.colors.YELLOW)

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
    
    try:
        answer = QAService.get_answer(question)
        typer.echo("\n回答:", color=typer.colors.GREEN)
        typer.echo(answer)
    except Exception as e:
        traceback.print_exc()
        typer.echo(f"获取答案失败: {e}", err=True, color=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command(name="analyze-pdf")
def analyze_pdf(
    input_file: Path = typer.Argument(
        ...,
        help="输入PDF文件路径",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    )
):
    """分析PDF文件中的设计规则问题"""
    try:
        typer.echo(f"开始分析: {input_file} ...", color=typer.colors.BLUE)
        
        # 1. 提取PDF文本
        pdf_text = PDFAnalyzer.extract_text(str(input_file))
        
        # 2. 分析规则问题
        issues = PDFAnalyzer.analyze_rules(pdf_text)
        
        # 3. 生成批注报告
        report = PDFAnalyzer.generate_annotations(issues)
        
        typer.echo("\n分析结果:", color=typer.colors.GREEN)
        typer.echo(report)
        
    except Exception as e:
        typer.echo(f"分析失败: {input_file}", err=True, color=typer.colors.RED)
        typer.echo(f"错误详情: {str(e)}", err=True, color=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()
