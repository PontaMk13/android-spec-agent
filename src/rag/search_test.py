from dotenv import load_dotenv
from google import genai
import chromadb

load_dotenv()

client = genai.Client()

# 保存済みのDBに接続（build_dbで作ったやつ）
chroma_client = chromadb.PersistentClient(path="vector_db")
collection = chroma_client.get_or_create_collection("asb")

# 質問
question = "重大な脆弱性が多かったのは?"

# 質問もGeminiでベクトル化（保存時と同じモデル！）
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question,
)
query_embedding = result.embeddings[0].values

# Chromaで「近いベクトル」を検索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
)

print("質問:", question)
print("見つかった要約:")
for doc in results["documents"][0]:
    print(" -", doc)