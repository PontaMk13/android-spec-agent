import hashlib, requests
from bs4 import BeautifulSoup
from paths import STATE

def check_changed(url, source_name, period):
    # main取得 → hash計算
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    main_text = main.get_text() if main else ""
    current_hash = hashlib.sha256(main_text.encode("utf-8")).hexdigest()

    # 前回のmeta.jsonからhashを読む
    meta_path = (STATE / source_name / f"asb-{period}-meta.json")
    previous_hash = ""
    if meta_path.exists():
        import json
        previous_hash = json.loads(meta_path.read_text()).get("content_hash", "")

    changed = (current_hash != previous_hash)
    return changed, current_hash, meta_path