"""知识库检索服务模块"""
from pprint import pprint
import requests
from typing import Dict, List, Optional
from .const import DIFY_API_KEY, DIFY_DATASET_ID

class KnowledgeService:
    """处理知识库检索的服务类"""
    
    DIFY_API_URL = "https://api.dify.ai/v1/datasets/{dataset_id}/retrieve"
    
    @classmethod
    def search_dify(cls, query: str, top_k: int = 8) -> Optional[List[Dict]]:
        """查询Dify知识库
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索结果列表或None
        """
        if not DIFY_API_KEY or not DIFY_DATASET_ID:
            raise ValueError("Dify API key or dataset ID not configured")
            
        url = cls.DIFY_API_URL.format(dataset_id=DIFY_DATASET_ID)
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "retrieval_model": {
                "search_method": "hybrid_search",
                "reranking_enable": False,
                "reranking_mode": "weighted_score",
                "reranking_model": {
                    "reranking_provider_name": "",
                    "reranking_model_name": ""
                },
                "weights": {
                    "weight_type": "customized",
                    "keyword_setting": {
                        "keyword_weight": 0.3
                    },
                    "vector_setting": {
                        "vector_weight": 0.7,
                        "embedding_model_name": "text-embedding-3-large",
                        "embedding_provider_name": "langgenius/openai/openai"
                    }
                },
                "top_k": top_k,
                "score_threshold_enabled": False,
                "score_threshold": 0
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("records", [])
        except Exception as e:
            print(f"知识库查询失败: {e}")
            return None

    @classmethod
    def format_results(cls, records: List[Dict]) -> str:
        """格式化检索结果为可读字符串"""
        if not records:
            return "未找到相关信息"
            
        formatted = []
        for record in records:
            # pprint(record)
            segment = record.get("segment", {})
            document = segment.get("document", {})
            doc_name = document.get("name", "未知文档")
            
            # 主内容
            main_content = segment.get("content", "无内容")
            
            # 子片段
            child_chunks = record.get("child_chunks", [])
            child_contents = [chunk["content"] for chunk in child_chunks if "content" in chunk]
            
            formatted.append(
                f"📄 文档: {doc_name}\n"
                f"🔍 相关度: {record.get('score', 0):.4f}\n"
                f"\n📌 主要内容:\n{main_content}\n"
            )
            
            if child_contents:
                formatted.append("🔍 相关片段:")
                for i, content in enumerate(child_contents, 1):
                    formatted.append(f"{i}. {content.strip()}")
                formatted.append("")
                
        return "\n".join(formatted).strip()
