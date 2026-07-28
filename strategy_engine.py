#strategy_engine.py
import os
import json
from datetime import datetime

APPDATA = os.getenv("APPDATA")
DATA_DIR = os.path.join(APPDATA, "TradingAppData")
STRATEGY_FILE = os.path.join(DATA_DIR, "strategies.json")

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(STRATEGY_FILE):
    with open(STRATEGY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def load_strategies():
    try:
        with open(STRATEGY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_strategy(name, cycle_type, direction, conditions, result):
    strategies = load_strategies()
    strategies.append({
        "name": name,
        "cycle_type": cycle_type,
        "direction": direction,
        "conditions": conditions,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    with open(STRATEGY_FILE, "w", encoding="utf-8") as f:
        json.dump(strategies, f, indent=2, ensure_ascii=False)

def delete_strategy(index):
    strategies = load_strategies()
    if 0 <= index < len(strategies):
        del strategies[index]
        with open(STRATEGY_FILE, "w", encoding="utf-8") as f:
            json.dump(strategies, f, indent=2, ensure_ascii=False)
    return strategies
