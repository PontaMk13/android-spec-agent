# paths.py（新規。パス定義を一元化）
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # このファイルの位置基準で1回

PROMPTS = ROOT / "prompts"
ENTRIES = ROOT / "entries"
STATE = ROOT / "state"
CONFIG = ROOT / "config.yaml"