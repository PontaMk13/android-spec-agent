from dotenv import load_dotenv
from google import genai
import chromadb

load_dotenv()

client = genai.Client()

chroma_client = chromadb.PersistentClient(path="vector_db")
collection = chroma_client.get_or_create_collection("asb")

question = "重大な脆弱性が多かったのは?"

# 1. 質問をベクトル化
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question,
)
query_embedding = result.embeddings[0].values

# 2. 近い要約を検索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
)
found_docs = results["documents"][0]

# 3. 見つけた要約を1つにまとめる
context = "\n\n".join(found_docs)

# 4. 要約＋質問をGeminiに渡して答えさせる
prompt = f"""以下の情報を元に、質問に日本語で答えてください。

情報:
{context}

質問: {question}
"""

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt,
)

print("質問:", question)
print("回答:", response.text)