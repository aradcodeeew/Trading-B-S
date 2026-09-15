# mcp_server.py
# سرور MCP برای ژورنال ترید — این فایل رو کنار app.py توی همون پوشه‌ی پروژه بذار.
# فقط همون فایل‌های JSON که app.py استفاده می‌کنه رو می‌خونه/می‌نویسه (توی %APPDATA%\TradingAppBS)
# هیچ ربطی به خود اجرای app.py نداره - جدا و مستقل کار می‌کنه.

import os
import json
import uuid
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ---------- مسیرهای دیتا (دقیقاً همونایی که app.py استفاده می‌کنه) ----------
DATA_DIR = os.path.join(os.environ["APPDATA"], "TradingAppBS")
JOURNAL_ACCOUNTS_FILE = os.path.join(DATA_DIR, "journal_accounts.json")
JOURNAL_DIR = os.path.join(DATA_DIR, "journal")
JOURNAL_STRATEGIES_FILE = os.path.join(DATA_DIR, "journal_strategies.json")
JOURNAL_STRATEGY_FIELDS_DIR = os.path.join(DATA_DIR, "journal_strategy_fields")
LEARN_DATA_FILE = os.path.join(DATA_DIR, "learn_data.json")


def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


mcp = FastMCP("trading-journal")


# ============================= حساب‌ها (Accounts) =============================

@mcp.tool()
def list_accounts() -> list:
    """لیست همه‌ی حساب‌های ژورنال (id, name, بالانس شروع، آخرین استراتژی استفاده‌شده) رو برمی‌گردونه."""
    return _load_json(JOURNAL_ACCOUNTS_FILE, [])


@mcp.tool()
def add_account(name: str) -> dict:
    """یه حساب جدید توی ژورنال می‌سازه. name: اسم حساب، مثلاً '3171541'."""
    accounts = _load_json(JOURNAL_ACCOUNTS_FILE, [])
    new_account = {"id": uuid.uuid4().hex[:8], "name": name}
    accounts.append(new_account)
    _save_json(JOURNAL_ACCOUNTS_FILE, accounts)
    return new_account


@mcp.tool()
def delete_account(account_id: str, confirm: bool = False) -> str:
    """
    یه حساب و همه‌ی تریدهاش رو کامل حذف می‌کنه - این کار غیرقابل‌برگشته.
    قبل از صدا زدن این تابع با confirm=True، حتماً باید از کاربر تأیید صریح گرفته بشه
    و اسم/مشخصات دقیق همون حساب بهش نشون داده بشه.
    """
    if not confirm:
        return "❌ عملیات لغو شد: باید confirm=True پاس داده بشه (فقط بعد از تأیید صریح کاربر)."
    accounts = _load_json(JOURNAL_ACCOUNTS_FILE, [])
    accounts = [a for a in accounts if a["id"] != account_id]
    _save_json(JOURNAL_ACCOUNTS_FILE, accounts)
    trades_path = os.path.join(JOURNAL_DIR, f"{account_id}.json")
    if os.path.exists(trades_path):
        os.remove(trades_path)
    return f"✅ حساب {account_id} و همه‌ی تریدهاش حذف شد."


# ============================= استراتژی‌ها (Strategies) =============================

@mcp.tool()
def list_strategies() -> list:
    """لیست همه‌ی استراتژی‌های ژورنال رو برمی‌گردونه (id, name)."""
    return _load_json(JOURNAL_STRATEGIES_FILE, [])


@mcp.tool()
def get_strategy_fields(strategy_id: str) -> list:
    """باکس‌های (فیلدهای) تعریف‌شده برای یه استراتژی خاص رو برمی‌گردونه."""
    path = os.path.join(JOURNAL_STRATEGY_FIELDS_DIR, f"{strategy_id}.json")
    return _load_json(path, [])


@mcp.tool()
def add_strategy(name: str) -> dict:
    """یه استراتژی جدید توی ژورنال می‌سازه. name: مثلاً 'Pro BTB'."""
    strategies = _load_json(JOURNAL_STRATEGIES_FILE, [])
    new_strategy = {"id": "st_" + uuid.uuid4().hex[:8], "name": name}
    strategies.append(new_strategy)
    _save_json(JOURNAL_STRATEGIES_FILE, strategies)
    return new_strategy


@mcp.tool()
def delete_strategy(strategy_id: str, confirm: bool = False) -> str:
    """
    یه استراتژی و همه‌ی باکس‌هاش رو حذف می‌کنه - غیرقابل‌برگشته.
    فقط بعد از تأیید صریح کاربر، confirm=True پاس داده بشه.
    """
    if not confirm:
        return "❌ عملیات لغو شد: باید confirm=True پاس داده بشه (فقط بعد از تأیید صریح کاربر)."
    strategies = _load_json(JOURNAL_STRATEGIES_FILE, [])
    strategies = [s for s in strategies if s["id"] != strategy_id]
    _save_json(JOURNAL_STRATEGIES_FILE, strategies)
    fields_path = os.path.join(JOURNAL_STRATEGY_FIELDS_DIR, f"{strategy_id}.json")
    if os.path.exists(fields_path):
        os.remove(fields_path)
    return f"✅ استراتژی {strategy_id} و باکس‌هاش حذف شد."


# ============================= تریدها (Trades) =============================

@mcp.tool()
def list_trades(account_id: str, strategy_id: str = "", limit: int = 20) -> list:
    """
    تریدهای یه حساب رو برمی‌گردونه (جدیدترین‌ها اول).
    strategy_id اختیاریه - اگه بدی، فقط تریدهای همون استراتژی رو فیلتر می‌کنه.
    limit: حداکثر تعداد تریدی که برمی‌گرده.
    """
    path = os.path.join(JOURNAL_DIR, f"{account_id}.json")
    trades = _load_json(path, [])
    if strategy_id:
        trades = [t for t in trades if t.get("strategy_id") == strategy_id]
    return trades[::-1][:limit]


@mcp.tool()
def add_trade(account_id: str, strategy_id: str, notes: str = "", balance: str = "", fields: dict = None) -> dict:
    """
    یه ترید جدید به ژورنال یه حساب اضافه می‌کنه.
    fields: دیکشنری از باکس‌های همون استراتژی، مثلاً {"back_context": "spike up", "setup_session": "LN"}.
    کلیدها باید همون id باکس‌هایی باشن که با get_strategy_fields گرفتی.
    """
    path = os.path.join(JOURNAL_DIR, f"{account_id}.json")
    trades = _load_json(path, [])

    strategies = _load_json(JOURNAL_STRATEGIES_FILE, [])
    strategy = next((s for s in strategies if s["id"] == strategy_id), None)

    trade = {
        "id": uuid.uuid4().hex[:8],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "strategy_id": strategy_id,
        "strategy_name": strategy["name"] if strategy else "",
        "notes": notes,
        "balance": balance,
        "photo": "",
    }
    if fields:
        trade.update(fields)

    trades.append(trade)
    _save_json(path, trades)
    return trade


@mcp.tool()
def delete_trade(account_id: str, trade_id: str, confirm: bool = False) -> str:
    """
    یه ترید خاص رو از ژورنال یه حساب حذف می‌کنه - غیرقابل‌برگشته.
    قبل از confirm=True، حتماً مشخصات همون ترید (تاریخ، استراتژی، نتیجه) به کاربر نشون داده بشه و تأیید گرفته بشه.
    """
    if not confirm:
        return "❌ عملیات لغو شد: باید confirm=True پاس داده بشه (فقط بعد از تأیید صریح کاربر)."
    path = os.path.join(JOURNAL_DIR, f"{account_id}.json")
    trades = _load_json(path, [])
    trades = [t for t in trades if t["id"] != trade_id]
    _save_json(path, trades)
    return f"✅ ترید {trade_id} حذف شد."


# ============================= آموزش (Learn) =============================

@mcp.tool()
def list_learn_posts() -> list:
    """لیست همه‌ی پست‌های بخش Learn رو برمی‌گردونه."""
    return _load_json(LEARN_DATA_FILE, [])


if __name__ == "__main__":
    mcp.run()
