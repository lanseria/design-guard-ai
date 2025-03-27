from pathlib import Path
import typer
from markitdown import MarkItDown
from .const import OPENAI_API_KEY, LLM_MODEL

app = typer.Typer(help="Markdown转换工具")

def convert_file(input_path: str, output_path: str):
    """文件转换核心函数"""
    # 初始化LLM客户端
    llm_client = None
    if OPENAI_API_KEY:
        from openai import OpenAI  # 延迟导入
        llm_client = OpenAI(api_key=OPENAI_API_KEY)
    
    md = MarkItDown(llm_client=llm_client, llm_model=LLM_MODEL)
    result = md.convert(input_path)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.text_content)

@app.command()
def convert(
    input_file: str = typer.Argument(..., help="输入文件路径"),
    output: str = typer.Option(None, "-o", "--output", help="输出Markdown文件路径")
):
    """转换单个文件为Markdown"""
    try:
        # 自动生成输出路径
        final_output = Path(output) if output else Path(input_file).with_suffix('.md')
        
        convert_file(input_file, str(final_output))
        typer.echo(f"成功转换: {input_file} -> {final_output}")
    except Exception as e:
        typer.echo(f"转换失败: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="输入目录路径"),
    output_dir: str = typer.Option("./markdown_files", "--output-dir", help="输出目录"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="递归处理子目录")
):
    """批量转换目录中的文件为Markdown"""
    # 支持的扩展名列表
    supported_extensions = (
        '.pdf', '.pptx', '.docx', '.xlsx',
        '.jpg', '.jpeg', '.png', '.mp3', '.wav',
        '.html', '.csv', '.json', '.xml', '.zip'
    )

    # 准备输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 处理文件
    count = 0
    glob_pattern = '**/*' if recursive else '*'
    
    for input_file in Path(input_dir).glob(glob_pattern):
        if input_file.is_file() and input_file.suffix.lower() in supported_extensions:
            # 构建输出路径
            relative_path = input_file.relative_to(input_dir) if recursive else input_file.name
            output_file = output_path / relative_path.with_suffix('.md')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                convert_file(str(input_file), str(output_file))
                count += 1
                typer.echo(f"处理成功: {input_file}")
            except Exception as e:
                typer.echo(f"跳过 {input_file}: {str(e)}", err=True)
    
    typer.echo(f"完成! 共转换了{count}个文件")

if __name__ == '__main__':
    app()