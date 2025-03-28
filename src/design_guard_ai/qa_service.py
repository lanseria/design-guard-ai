"""问答服务模块"""
import traceback
from typing import Optional
from .ai_utils import generate_with_ai
from .knowledge_service import KnowledgeService

class QAService:
    """处理问答流程的服务类"""
    
    @classmethod
    def format_question(cls, question: str) -> Optional[str]:
        """格式化用户问题"""
        prompt = f"请将以下问题简化为技术查询，移除问候语等非必要内容:\n{question}\n简化后的问题:"
        try:
            formatted_stream = generate_with_ai(prompt)
            return "".join(list(formatted_stream))
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"问题格式化失败: {e}")

    @classmethod
    def get_answer(cls, question: str) -> str:
        """获取问题答案"""
        try:
            # 1. 格式化问题
            formatted_question = cls.format_question(question)
            if not formatted_question:
                return "无法格式化问题"

            # 2. 查询知识库
            records = KnowledgeService.search_dify(formatted_question)
            if not records:
                return "未找到相关信息"

            # 3. 生成回答
            knowledge = KnowledgeService.format_results(records)
            answer_prompt = f"""根据以下知识库内容和用户原始问题，生成一个简洁友好的回答：
            
用户问题: {question}
知识库内容:
{knowledge}

请用中文回答，保持专业但友好的语气，直接回答问题要点。"""
            
            answer_stream = generate_with_ai(answer_prompt)
            return "".join(list(answer_stream))

        except Exception as e:
            traceback.print_exc()
            raise Exception(f"获取答案失败: {e}")
