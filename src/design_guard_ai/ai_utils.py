import traceback
import httpx
import json
from google import genai
from google.genai import types
from .const import GEMINI_API_KEY, LLM_MODEL, OPENROUTER_API_KEY, OPENAI_MODEL, AI_VENDOR
from typing import Generator
import asyncio

class UnsupportedAIProviderError(Exception):
    """不支持的AI供应商异常"""
    pass


def sync_wrapper(async_gen):
    """将异步生成器转换为同步生成器的包装器"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        ait = async_gen.__aiter__()
        while True:
            try:
                yield loop.run_until_complete(ait.__anext__())
            except StopAsyncIteration:
                break
    finally:
        loop.close()


def generate_with_ai(prompt: str) -> Generator[str, None, None]:
    """通用AI生成接口
    
    根据AI_VENDOR配置选择具体的AI供应商实现
    
    Args:
        prompt: 输入的提示文本
        
    Returns:
        同步生成器，流式返回AI生成的文本
        
    Raises:
        UnsupportedAIProviderError: 当配置了不支持的AI供应商时
    """
    if AI_VENDOR == "google":
        return generate_with_google_ai(prompt)
    elif AI_VENDOR == "openai":
        return sync_wrapper(generate_with_openai(prompt))
    else:
        raise UnsupportedAIProviderError(f"不支持的AI供应商: {AI_VENDOR}")


def generate_with_google_ai(prompt: str):
    """Google AI专用生成接口"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = []
    try:
        # Google AI流式响应
        stream = client.models.generate_content_stream(
            contents=[{
                "role": "user",
                "parts": [
                    types.Part.from_text(text=prompt)
                ]
            }],
            model=LLM_MODEL,
        )
        for chunk in stream:
            if chunk.text:
                response.append(chunk.text)
                yield chunk.text
    except Exception as e:
        print(f"AI Generation Error: {e}") #可选： 打印错误信息到控制台
        traceback.print_exc()
        raise  # 重新抛出异常，让上层函数处理

    # 注意：流式处理时，通常不需要在最后返回完整字符串，
    # 但如果调用者需要，可以保留。这里暂时注释掉。
    # return "".join(response)


async def generate_with_openai(prompt: str):
    """OpenAI专用生成接口(通过OpenRouter)"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/your-repo",  # 可选但推荐
        "X-Title": "Design Guard AI"  # 可选但推荐
    }
    
    data = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data = chunk[6:]
                        if data != "[DONE]":
                            try:
                                chunk_json = json.loads(data)
                                if "choices" in chunk_json:
                                    content = chunk_json["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
    except Exception as e:
        print(f"OpenAI Generation Error: {e}")
        traceback.print_exc()
        raise
