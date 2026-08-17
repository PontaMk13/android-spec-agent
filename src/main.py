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
            return func(), attempt
        except Exception:
            if attempt < max_retry - 1:
                print("Retry:", attempt)
                time.sleep(2 ** attempt)
            else:
                print("Retry out")
                raise

def main():
    import sys
    from datetime import date
    if len(sys.argv) > 1:
        period = sys.argv[1]              # python main.py 2026-06
    else:
        period = date.today().strftime("%Y-%m")   # 今月（ex: 2026-08）

    config = yaml.safe_load(open(CONFIG, encoding="utf-8"))
    base_url = config["source"]["base_url"]

    model = config["llm"]["model"]
    fallback_model = config["llm"]["fallback_model"]
    source_name = config["source"]["name"]   # android-security-bulletin
    max_retry = config["loop"]["max_retry"]

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
    model_used = model 
    try:
        summary, retry_count = with_retry(lambda: summarize_by_gemini(url, model_used, source_name, period))
        status = "success"
        last_error = None
    except Exception as e:
        print(f"要約失敗→フォールバック始動: {e}")
        try:
            summary, retry_count = with_retry(lambda: summarize_by_gemini(url, fallback_model, source_name, period))
            model_used = fallback_model
            status = "success"
            last_error = None

        except Exception as e2:
            print(f"フォールバックも失敗: {e2}")
            retry_count = max_retry
            status = "error"
            last_error = str(e2)

    # update_count: 成功時のみ、前回metaから引き継いで +1
    update_count = 0
    if meta_path.exists():
        try:
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            update_count = prev.get("update_count", 0)
        except Exception:
            update_count = 0
    if status == "success":
        update_count += 1
        print(f"要約成功")

    # 処理状態を meta.json に保存
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "content_hash": current_hash if status == "success" else "",
        "detected_at": datetime.now().isoformat(),
        "update_count": update_count,
        "retry_count": retry_count,
        "model_used": model_used,
        "last_error": last_error,
        "status": status,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"meta保存: {meta_path}")


if __name__ == "__main__":
    main()