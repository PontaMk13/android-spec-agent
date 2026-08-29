from dotenv import load_dotenv
from google import genai
import chromadb
from pathlib import Path

load_dotenv()

client = genai.Client()

# パス
ROOT = Path(__file__).resolve().parent.parent.parent
ENTRIES = ROOT / "entries" / "android-security-bulletin"

# Chroma
chroma_client = chromadb.PersistentClient(path=str(ROOT / "vector_db"))
collection = chroma_client.get_or_create_collection("asb")


def parse_summary(path):
    """summary.md を frontmatter と本文に分ける。字下げも吸収。"""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    meta = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = i + 1
                break
            if ":" in line:
                key, _, value = line.strip().partition(":")
                meta[key.strip()] = value.strip()

    body = "\n".join(lines[body_start:]).strip()
    return meta, body


def embed_and_upsert(period, source_name, body):
    """要約本文をベクトル化して、その月だけ upsert（差分更新）。"""
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=body,
    )
    embedding = result.embeddings[0].values
    collection.upsert(
        ids=[f"asb-{period}"],
        embeddings=[embedding],
        documents=[body],
        metadatas=[{"period": period, "source": source_name}],
    )
    print(f"DB更新（差分）: asb-{period}")


def build_all():
    """全要約を一括で DB 化（単独実行用・初回構築）。"""
    for month_dir in sorted(ENTRIES.iterdir()):
        if not month_dir.is_dir():
            continue
        for md_file in month_dir.glob("*-summary.md"):
            meta, body = parse_summary(md_file)
            period = meta.get("period", month_dir.name)
            source_name = meta.get("source", "android-security-bulletin")
            embed_and_upsert(period, source_name, body)
    print("完了。件数:", collection.count())


if __name__ == "__main__":
    build_all()