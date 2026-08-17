from fetch import check_changed
from gemini_inv_asb import summarize_by_gemini
import json
import yaml
from datetime import datetime
import time
from google.genai import errors
from paths import CONFIG

def with_retry(func, max_retry=3):
    for attempt in range(max_retry):
        try:
            return func()
        except Exception:
            if attempt < max_retry - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def main():
    config = yaml.safe_load(open(CONFIG, encoding="utf-8"))
    base_url = config["source"]["base_url"]
    period = config["source"]["period"]          # 2026-06
    model = config["llm"]["model"]
    source_name = config["source"]["name"]   # android-security-bulletin

    # URL組み立て（period から年を取り出す）
    year = period[:4]                             # "2026"
    url = f"{base_url}/{year}/{period}-01"        # .../2026/2026-06-01

    print("URL:", url)

    # hashチェック
    changed, current_hash, meta_path = check_changed(url, source_name, period)
    if not changed:
        print("変化なし。スキップ")
        exit()

    print("変化あり。要約します")

    # 要約を試みる
    try:
        with_retry(lambda: summarize_by_gemini(url, model, source_name, period))
        status = "success"
        last_error = None
    except Exception as e:
        print(f"要約失敗: {e}")
        status = "error"
        last_error = str(e)

    # 処理状態を meta.json に保存
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "content_hash": current_hash if status == "success" else "",
        "detected_at": datetime.now().isoformat(),
        "retry_count": 0,
        "last_error": last_error,
        "status": status,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"meta保存: {meta_path}")


if __name__ == "__main__":
    main()