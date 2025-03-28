# Design Guard AI - Markdown转换工具

## 安装

```bash
# 创建虚拟环境
python3.12 -m venv myenv
source myenv/bin/activate  # macOS/Linux
# .\myenv\Scripts\Activate.ps1  # Windows

# 安装依赖
pip install .
```

## 使用说明

### 单个文件转换
```bash
dga convert document.pdf -o output.md
# dga convert ./input/ej_1.pdf -o output/ej_1.md
# dga convert ./input/test1.pdf -o output/test1.md
```

### 批量转换
```bash
dga batch ./documents --output-dir ./markdown_files
```

### 问答库

使用 `ask` 命令向知识库提问。工具会先使用 AI 对您的问题进行格式化，以提高检索准确性，然后查询知识库（查询功能待实现）。

```bash
dga ask "你的问题是什么？"
# 例如: dga ask "如何在 Python 中使用 Typer 创建命令行选项？" 
```

## 功能特点
- 支持多种文件格式转换为Markdown
- 支持单个文件和批量转换
- 自动处理文件扩展名
- 错误处理和跳过无效文件

## 开发
```bash
# 开发模式安装
pip install -e ".[test]"

# 运行测试
pytest
```

## 依赖
- Python 3.7+
- typer
- markitdown
- rich
