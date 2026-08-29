from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

# 要約テキストを1個、数値に変換してみる
text = "2026年6月はCriticalが18件、Systemに集中していた"

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
)

# 数値の配列を確認
embedding = result.embeddings[0].values
print("次元数:", len(embedding))          # 何個の数字か
print("最初の5個:", embedding[:5])         # 中身をちょっと見る