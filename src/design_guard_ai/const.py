"""Configuration module with .env support"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（优先从项目根目录查找）
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

# AI 供应商配置（优先读取环境变量）
AI_VENDOR = os.getenv("AI_VENDOR", "google")  # 默认使用 Google

# API 密钥配置（优先读取环境变量）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DIFY_DATASET_ID = os.getenv("DIFY_DATASET_ID", "")

# 动态模型配置
_GOOGLE_DEFAULT_MODEL = "gemini-2.0-flash"

# 根据供应商选择默认模型
LLM_MODEL = os.getenv("LLM_MODEL")
