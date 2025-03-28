import traceback
from google import genai
from google.genai import types
from .const import GEMINI_API_KEY, LLM_MODEL


def generate_with_ai(prompt: str):
    """通用AI生成接口"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = []
    try:
        # Google AI生成流式响应
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
