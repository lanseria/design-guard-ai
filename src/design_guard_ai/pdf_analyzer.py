"""PDF规则分析服务模块"""
import traceback
import tempfile
from typing import List, Dict, Optional
from pathlib import Path
from .ai_utils import generate_with_ai
from .knowledge_service import KnowledgeService
from .converter import convert_file as perform_conversion

class PDFAnalyzer:
    """处理PDF规则分析的服务类"""
    
    @classmethod
    def extract_text(cls, pdf_path: str) -> str:
        """从PDF提取文本内容"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp:
                temp_path = tmp.name
            
            # 转换PDF为Markdown
            perform_conversion(pdf_path, temp_path)
            
            # 读取Markdown内容
            with open(temp_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 删除临时文件
            Path(temp_path).unlink(missing_ok=True)
            
            return text
        except Exception as e:
            raise Exception(f"PDF解析失败: {e}")

    @classmethod
    def analyze_rules(cls, pdf_text: str) -> List[Dict]:
        """分析文本并返回规则问题列表"""
        try:
            # 1. 查询知识库获取相关规则
            records = KnowledgeService.search_dify("设计规范规则")
            if not records:
                return []
                
            # 2. 对每条规则检查PDF内容
            issues = []
            for record in records:
                rule_content = record.get("segment", {}).get("content", "")
                if not rule_content:
                    continue
                    
                # 检查规则是否被违反
                if cls._check_violation(pdf_text, rule_content):
                    issues.append({
                        "rule": rule_content,
                        "source": record.get("segment", {}).get("document", {}).get("name", "未知来源"),
                        "score": record.get("score", 0)
                    })
                    
            return issues
            
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"规则分析失败: {e}")

    @classmethod
    def _check_violation(cls, text: str, rule: str) -> bool:
        """检查文本是否违反规则"""
        # 简单实现：检查规则关键词是否出现在文本中
        # 实际应该使用更智能的匹配方式
        return rule.lower() in text.lower()

    @classmethod
    def generate_annotations(cls, issues: List[Dict]) -> str:
        """生成批注报告"""
        if not issues:
            return "未发现规则问题"
            
        report = ["发现以下规则问题:"]
        for i, issue in enumerate(issues, 1):
            report.append(
                f"{i}. [来源: {issue['source']}, 相关度: {issue['score']:.2f}]\n"
                f"   - 问题: {issue['rule']}\n"
                f"   - 建议修改: 请参考设计规范调整"
            )
            
        return "\n".join(report)
