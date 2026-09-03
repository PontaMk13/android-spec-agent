from fetch import check_changed
from gemini_inv_asb import summarize_by_gemini
import json
import yaml
from datetime import datetime, date
import time
import sys
from google.genai import errors
from paths import CONFIG

from paths import ROOT
sys.path.append(str(ROOT /"src"/"rag"))   # or 適切な import 設定
from build_db import embed_and_upsert


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


def recent_periods():
    """今月と前月を返す（引数なし時の対象）。"""
    today = date.today()
    this_month = today.strftime("%Y-%m")
    if today.month == 1:
        prev = date(today.year - 1, 12, 1)
    else:
        prev = date(today.year, today.month - 1, 1)
    return [this_month, prev.strftime("%Y-%m")]


def process(period, config):
    """1つの period を処理する。"""
    base_url = config["source"]["base_url"]
    model = config["llm"]["model"]
    fallback_model = config["llm"]["fallback_model"]
    source_name = config["source"]["name"]
    max_retry = config["loop"]["max_retry"]

    year = period[:4]
    url = f"{base_url}/{year}/{period}-01"
    print("URL:", url)

    changed, current_hash, meta_path = check_changed(url, source_name, period)
    if not changed:
        print(f"変化なし。スキップ ({period})")
        return                                    # exit() → return に変更

    print("変化あり。要約します")

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

    update_count = 0
    if meta_path.exists():
        try:
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            update_count = prev.get("update_count", 0)
        except Exception:
            update_count = 0
    if status == "success":
        update_count += 1
        print(f"要約成功（{model_used}）") 

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

    """vector生成"""
    if status == "success":
        try:
            embed_and_upsert(period, source_name, summary)
        except Exception as e:
            print(f"DB更新失敗（要約は保存済み）: {e}")
            # DB更新の失敗は、要約の成功を巻き込まない



def main():
    config = yaml.safe_load(open(CONFIG, encoding="utf-8"))

    if len(sys.argv) > 1:
        periods = [sys.argv[1]]              # 引数指定 → その月だけ
    else:
        periods = recent_periods()           # 引数なし → 今月＋前月

    for period in periods:
        print(f"=== {period} を処理 ===")
        process(period, config)


if __name__ == "__main__":
    main()