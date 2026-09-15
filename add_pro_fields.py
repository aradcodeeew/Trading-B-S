#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اضافہ کردن خودکار فیلدهای بهینہ sp2L PRO
این script تمام 10 فیلد بهینہ PRO رو اضافہ می‌کند!
"""

import json
import os
import uuid

# مسیرها (همان app.py میں است)
APPDATA = os.getenv("APPDATA")
DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "TradingAppBS")
JOURNAL_STRATEGY_FIELDS_DIR = os.path.join(DATA_DIR, "journal_strategy_fields")

# مطمئن شو که پوشه وجود دارد
os.makedirs(JOURNAL_STRATEGY_FIELDS_DIR, exist_ok=True)

# Strategy ID برای sp2L PRO
STRATEGY_ID = "st_f0616590"  # ID استراتژی PRO

# تمام 10 فیلد بهینہ
PRO_FIELDS = [
    {
        "id": "f_8c1b049f",
        "label": "back pattern type",
        "type": "select",
        "options": ["spike", "chanel", "range"],
        "pro_note": "✅ ONLY: spike (85%) | ❌ SKIP: chanel, range"
    },
    {
        "id": "f_2f9307d9",
        "label": "sp2l in seasion first",
        "type": "select",
        "options": ["yes", "no"],
        "pro_note": "✅ yes (اولین/دومین) | ⚠ no (فقط در جهت)"
    },
    {
        "id": "f_fddf288e",
        "label": "num candle (leg)",
        "type": "select",
        "options": ["(2)", "3", "4", "5", "6"],
        "pro_note": "✅ (2), 3, 4 بهترین | ⚠ 5 | ❌ 6+"
    },
    {
        "id": "f_270ae89e",
        "label": "body ratio candles leg 1",
        "type": "select",
        "options": [
            "full body some shadow",
            "full body no shadow",
            "full body large shadow",
            "body and som shadow",
            "body no shaadow",
            "breakout spike",
            "breakout trend (some shadow)"
        ],
        "pro_note": "✅ full body no shadow (87%) | ✅ breakout spike (84%) | ❌ full body large shadow (25%)"
    },
    {
        "id": "f_811c19f2",
        "label": "trend context",
        "type": "select",
        "options": ["context up", "context down"],
        "pro_note": "✅ Aligned (بدون توجه up/down) | ❌ هیچوقت خلاف جهت"
    },
    {
        "id": "f_2445054b",
        "label": "signal bar",
        "type": "select",
        "options": ["small candle", "fix candle", "shadow candle"],
        "pro_note": "✅ small candle (79%) | ✅ fix candle (77%) | ❌ shadow candle (52%)"
    },
    {
        "id": "f_ba7fd868",
        "label": "leg 2",
        "type": "select",
        "options": ["in vertex", "off vertex"],
        "pro_note": "✅ ONLY: in vertex (82%) | ❌ SKIP: off vertex (45%)"
    },
    {
        "id": "f_7bc43ca4",
        "label": "time trade (broker)",
        "type": "select",
        "options": [
            "tk 20 / 6",
            "LN 7 / 12",
            "LN window 8 / 12",
            "ny 12 / 19 pm",
            "ny window 13 / 17"
        ],
        "pro_note": "✅ BEST: LN window 8/12 (78%) | ✅ LN 7/12 (76%) | ❌ tk 20/6 (42%)"
    },
    {
        "id": "f_e55fe4d5",
        "label": "risk",
        "type": "select",
        "options": ["0.5", "0.75", "1", "1.25", "1.5", "1.75", "2"],
        "pro_note": "✅ 0.5 یا 0.75 (74%) | ❌ 1.0+ (55-62%)"
    },
    {
        "id": "f_a51eaf39",
        "label": "Reasult",
        "type": "select",
        "options": [
            "win buy tp 1",
            "win buy tp 2",
            "win buy tp 3",
            "win sell tp 1",
            "win sell tp 2",
            "win sell tp 3",
            "stop loss",
            "not order",
            "free risk"
        ],
        "pro_note": "✅ win ... tp 1 (71% بهترین) | ✅ win ... tp 2 (65%) | ❌ stop loss (ضرر)"
    }
]


def add_fields_to_strategy(strategy_id, fields):
    """
    فیلدها رو به یک استراتژی اضافہ می‌کند
    """
    file_path = os.path.join(JOURNAL_STRATEGY_FIELDS_DIR, f"{strategy_id}.json")
    
    # اگر فایل وجود داشت، بارگذاری کن
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                existing_fields = json.load(f)
                print(f"📋 فایل موجود پیدا شد: {len(existing_fields)} فیلد")
            except:
                existing_fields = []
                print("⚠️ فایل خراب بود، دوباره می‌سازم...")
    else:
        existing_fields = []
        print("📁 فایل جدید می‌سازم...")
    
    # فیلدهای جدید اضافہ کن (بدون تکرار)
    existing_ids = {f["id"] for f in existing_fields}
    
    for field in fields:
        if field["id"] not in existing_ids:
            # pro_note رو برای نمایش حفظ کن (اختیاری)
            field_to_add = {
                "id": field["id"],
                "label": field["label"],
                "type": field["type"],
                "options": field["options"]
            }
            existing_fields.append(field_to_add)
            print(f"✅ اضافہ شد: {field['label']}")
        else:
            print(f"⏭️ پروپ: {field['label']} (موجود است)")
    
    # ذخیره کن
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_fields, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ تمام {len(existing_fields)} فیلد ذخیره شد!")
    print(f"📍 فایل: {file_path}")


def main():
    print("=" * 60)
    print("🚀 اضافہ کردن فیلدهای بهینہ sp2L PRO")
    print("=" * 60)
    print(f"\n📌 Strategy ID: {STRATEGY_ID}")
    print(f"📁 Data Directory: {DATA_DIR}")
    print(f"📂 Fields Directory: {JOURNAL_STRATEGY_FIELDS_DIR}\n")
    
    if not os.path.exists(DATA_DIR):
        print(f"❌ خطا: دایرکتوری یافت نشد: {DATA_DIR}")
        print("💡 برنامه Trading App رو حداقل یکبار اجرا کن تا دایرکتوری ایجاد شود.")
        return False
    
    print("📝 فیلدهای قرار‌الداده شدہ:\n")
    for i, field in enumerate(PRO_FIELDS, 1):
        print(f"{i}. {field['label']}")
        print(f"   {field['pro_note']}\n")
    
    # کاربر تایید کند
    response = input("\n✅ تایید کنید (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ لغو شد.")
        return False
    
    # فیلدها رو اضافہ کن
    print("\n⏳ در حال اضافہ کردن...\n")
    add_fields_to_strategy(STRATEGY_ID, PRO_FIELDS)
    
    print("\n" + "=" * 60)
    print("🎉 کار تمام!")
    print("=" * 60)
    print("\n📌 اگر Trading App باز است، صفحہ رو refresh کن (F5)")
    print("📌 بعد به: Journal → Strategies → sp2L PRO → Boxes\n")


if __name__ == "__main__":
    main()
