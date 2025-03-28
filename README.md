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

### OCR 识别

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

## AI 提示

请按照以下步骤处理OCR识别出的文本内容：
1️⃣【广告水印过滤】
- 自动识别并删除包含以下模式的干扰内容：
  🔹 广告标识：如"联系QQ", "微信", "[赞助]", "扫码关注"等
  🔹 商业水印：连续符号（如★★★）、页眉页脚重复商标，名 师 ⾯ 授 精 华 、 央 企 内 训 、 考 点 串 讲 、 习 题 模 考 、 考 前 三 页 纸
  🔹 超链接：http/https链接、短链(如t.cn/xxx)
  🔹 推广二维码：保留文字描述但删除"【二维码】"等标注
  🔹 大标题
  🔹 主讲人

2️⃣【主题相关性过滤】
当前核心主题关键词组：["二建机电实务"] 

3️⃣【内容结构化处理】
保留：
✓ 完整段落逻辑 ✓ 标题层级 ✓ 必要标点符号
优化：
× 去除零散字符 × 合并断行文本 × 修正OCR错位
