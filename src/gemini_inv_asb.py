from dotenv import load_dotenv
from google import genai
from google.genai.types import Tool, GenerateContentConfig
from paths import PROMPTS, ENTRIES
from datetime import datetime

def summarize_by_gemini(url, model, source_name, period):

    load_dotenv()

    client = genai.Client()

    # URL Context ツールを有効化
    tools = [{"url_context": {}}]

    # プロンプトをファイルから読む
    prompt_path = PROMPTS / source_name / "summary.md"
    prompt_template = prompt_path.read_text(encoding="utf-8")

    # {url} を実際のURLに置き換える
    prompt = prompt_template.format(url=url)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=GenerateContentConfig(tools=tools,
                                    temperature=0.2,),
    )
    summary = response.text

    # 保存先（月ディレクトリ）
    entry_dir = ENTRIES / source_name / period
    entry_dir.mkdir(parents=True, exist_ok=True)

    # frontmatter + 本文
    content = f"""---
source: {source_name}
source_url: {url}
period: {period}
detected_at: {datetime.now().isoformat()}
---

{summary}
"""

    #保存
    filename = f"asb-{period}-summary.md"
    (entry_dir / filename).write_text(content, encoding="utf-8")
    print(f"保存: {entry_dir / filename}")

    return summary