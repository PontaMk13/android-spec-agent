import os
from dotenv import load_dotenv
from google import genai

# .env からキーを読む
load_dotenv()

# クライアント作成（GEMINI_API_KEY を自動で読む）
client = genai.Client()

# 要約テスト
response = client.models.generate_content(
    model="gemini-flash-lite-latest", 
    contents="こんにちは。1行で自己紹介して。",
)
print(response.text)