#app.py

from flask import Flask, render_template, request, redirect, send_file, url_for, send_from_directory, make_response
from flaskwebgui import FlaskUI
from datetime import datetime
from io import BytesIO
import os
import sys
import json
import io
import zipfile
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from openpyxl import Workbook

app = Flask(__name__, static_url_path='/static')

# مسیرهای پایه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPDATA = os.getenv("APPDATA")
DATA_DIR = os.path.join(os.environ["APPDATA"], "TradingAppBS")
NOTES_DIR = os.path.join(DATA_DIR, "notes")
LEARN_IMG_DIR = os.path.join(DATA_DIR, "learn_images")
LEARN_DATA_FILE = os.path.join(DATA_DIR, "learn_data.json")

# ---------- ژورنال کامل ترید (چند حساب) ----------
JOURNAL_ACCOUNTS_FILE = os.path.join(DATA_DIR, "journal_accounts.json")
JOURNAL_FIELDS_FILE = os.path.join(DATA_DIR, "journal_fields.json")
JOURNAL_DIR = os.path.join(DATA_DIR, "journal")
JOURNAL_STRATEGIES_FILE = os.path.join(DATA_DIR, "journal_strategies.json")
JOURNAL_STRATEGY_FIELDS_DIR = os.path.join(DATA_DIR, "journal_strategy_fields")
JOURNAL_UPLOAD_DIR = os.path.join(DATA_DIR, "journal_uploads")

# پوشه‌های لازم
os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(LEARN_IMG_DIR, exist_ok=True)
os.makedirs(JOURNAL_DIR, exist_ok=True)
os.makedirs(JOURNAL_STRATEGY_FIELDS_DIR, exist_ok=True)
os.makedirs(JOURNAL_UPLOAD_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
CAPITAL_NOTE = os.path.join(NOTES_DIR, "capital.txt")
RISK_NOTE = os.path.join(NOTES_DIR, "risk.txt")
EMOTION_NOTE = os.path.join(NOTES_DIR, "emotion.txt")

# رمز و یوزر دیگه هاردکد نیست - بار اول که اپ باز میشه خودت می‌سازیش
AUTH_FILE = os.path.join(DATA_DIR, "auth.json")


def load_auth():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return None
    return None


def save_auth(username, password):
    data = {"username": username, "password_hash": generate_password_hash(password)}
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

current_risk = 0
cycle_count = 0
loss_count = 0
consecutive_wins = 0
max_cycle = 0
risk_start = 0.5
last_selected_start = None
MAX_RISK = 3.0

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
# تابع ذخیره یادداشت‌ها
def save_note(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# تابع بارگذاری یادداشت‌ها
def load_notes(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# بارگذاری تاریخچه نتایج
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# ذخیره رویداد جدید در تاریخچه
def save_history(row):
    history = load_history()
    history.append(row)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

# بارگذاری پست‌های آموزشی Learn
def load_learn_posts():
    if os.path.exists(LEARN_DATA_FILE):
        with open(LEARN_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ذخیره پست‌های آموزشی Learn
def save_learn_posts(posts):
    with open(LEARN_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

# ---------- توابع ژورنال کامل ----------
def load_journal_accounts():
    if os.path.exists(JOURNAL_ACCOUNTS_FILE):
        with open(JOURNAL_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_journal_accounts(accounts):
    with open(JOURNAL_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)


def journal_trades_path(account_id):
    return os.path.join(JOURNAL_DIR, f"{account_id}.json")


def load_journal_trades(account_id):
    path = journal_trades_path(account_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_journal_trades(account_id, trades):
    with open(journal_trades_path(account_id), "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2, ensure_ascii=False)


def load_journal_fields():
    if os.path.exists(JOURNAL_FIELDS_FILE):
        with open(JOURNAL_FIELDS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_journal_fields(fields):
    with open(JOURNAL_FIELDS_FILE, "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)


# ---------- استراتژی‌های ژورنال (بخش کاملاً جدا از صفحه‌ی Strategy قدیمی) ----------
def load_journal_strategies():
    if os.path.exists(JOURNAL_STRATEGIES_FILE):
        with open(JOURNAL_STRATEGIES_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_journal_strategies(strategies):
    with open(JOURNAL_STRATEGIES_FILE, "w", encoding="utf-8") as f:
        json.dump(strategies, f, indent=2, ensure_ascii=False)


def strategy_fields_path(strategy_id):
    return os.path.join(JOURNAL_STRATEGY_FIELDS_DIR, f"{strategy_id}.json")


def load_strategy_fields(strategy_id):
    path = strategy_fields_path(strategy_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_strategy_fields(strategy_id, fields):
    with open(strategy_fields_path(strategy_id), "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)


# نمایش تصویرهای Learn از پوشه دائمی
@app.route("/learn_images/<filename>")
def learn_image(filename):
    return send_from_directory(LEARN_IMG_DIR, filename)

# صفحه خوش‌آمدگویی و ورود (بار اول: ساخت حساب / بعدش: ورود عادی)
@app.route("/", methods=["GET", "POST"])
def welcome():
    auth = load_auth()

    # هنوز از تنظیمات رمزی نساخته - یه ولکام ساده با دکمه‌ی ورود (بدون فیلد) نشون بده
    if auth is None:
        return render_template("welcome.html", no_password=True)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == auth["username"] and check_password_hash(auth["password_hash"], password):
            resp = make_response(redirect("/dashboard"))
            resp.set_cookie("remember_login", "yes", max_age=60 * 60 * 24 * 365 * 10)
            return resp
        return render_template("welcome.html", error="نام کاربری یا رمز عبور اشتباه است!")

    if request.cookies.get("remember_login") == "yes":
        return redirect("/dashboard")
    return render_template("welcome.html")

# خروج از سیستم
@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    error = None
    success = None
    auth = load_auth()

    if request.method == "POST":
        new_username = request.form.get("new_username", "").strip()
        new_password = request.form.get("new_password", "")

        if auth is None:
            # اولین باره داره رمز ورود می‌سازه
            if not new_username or not new_password:
                error = "نام کاربری و رمز رو کامل بنویس"
            else:
                save_auth(new_username, new_password)
                success = "رمز ورود ساخته شد. از این به بعد هر بار اپ رو باز کنی رمز می‌خواد."
                auth = load_auth()
        else:
            current_password = request.form.get("current_password", "")
            if not check_password_hash(auth["password_hash"], current_password):
                error = "رمز فعلی اشتباهه"
            elif not new_username:
                error = "نام کاربری نمی‌تونه خالی باشه"
            else:
                final_password = new_password if new_password else current_password
                save_auth(new_username, final_password)
                success = "تغییرات ذخیره شد"
                auth = load_auth()

    return render_template(
        "settings.html",
        username=(auth["username"] if auth else ""),
        has_auth=(auth is not None),
        error=error,
        success=success,
    )


@app.route("/logout")
def logout():
    resp = make_response(redirect("/"))
    resp.set_cookie("remember_login", "", expires=0)
    return resp

# صفحه داشبورد مدیریت ریسک ترید
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    global current_risk, cycle_count, loss_count, max_cycle
    global risk_start, last_selected_start, consecutive_wins
    cycle_value = None
    risk_display = None
    message = None

    if request.method == "POST":
        result = request.form["result"]
        risk_start = float(request.form["risk_start"])
        max_cycle = int(request.form["cycle"])
        cycle_value = max_cycle

        if last_selected_start != risk_start:
            current_risk = risk_start
            last_selected_start = risk_start
            cycle_count = 0
            loss_count = 0
            consecutive_wins = 0

        if result == "win":
            cycle_count += 1
            consecutive_wins += 1
            loss_count = 0

            if cycle_count >= max_cycle:
                current_risk += 0.25
                cycle_count = 0
            if current_risk >= MAX_RISK:
                current_risk = MAX_RISK
                message = "به سقف ریسک (٪2) رسیدی، همینجا ثابت می‌مونه تا خودت ریست کنی"

        elif result == "loss":
            current_risk = max(risk_start, current_risk - 0.25)
            cycle_count = 0
            loss_count += 1
            consecutive_wins = 0

            if loss_count >= 2:
                message = "دو ضرر داشتی ببند ترید رو تمرین کن ضرر ها رو فردا بیا"

        risk_display = round(current_risk, 2)
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk": risk_display,
            "result": result
        }
        save_history(row)

    history = load_history()
    return render_template(
        "dashboard.html",
        risk=risk_display,
        message=message,
        cycle_value=cycle_value,
        history=history[::-1]
    )

# مدیریت یادداشت سرمایه
@app.route("/capital", methods=["GET", "POST"])
def capital():
    if request.method == "POST":
        note = request.form.get("note", "").strip()
        if note:
            save_note(CAPITAL_NOTE, note)
    notes = load_notes(CAPITAL_NOTE)
    return render_template("capital.html", notes=notes)

@app.route("/capital/delete/<int:index>", methods=["POST"])
def delete_capital_note(index):
    notes = load_notes(CAPITAL_NOTE)
    if 0 <= index < len(notes):
        del notes[index]
        with open(CAPITAL_NOTE, "w", encoding="utf-8") as f:
            f.write("\n".join(notes) + "\n")
    return redirect("/capital")

# مدیریت یادداشت ریسک
@app.route("/risk", methods=["GET", "POST"])
def risk():
    if request.method == "POST":
        note = request.form.get("note", "").strip()
        if note:
            save_note(RISK_NOTE, note)
    notes = load_notes(RISK_NOTE)
    return render_template("risk.html", notes=notes)

@app.route("/risk/delete/<int:index>", methods=["POST"])
def delete_risk_note(index):
    notes = load_notes(RISK_NOTE)
    if 0 <= index < len(notes):
        del notes[index]
        with open(RISK_NOTE, "w", encoding="utf-8") as f:
            f.write("\n".join(notes) + "\n")
    return redirect("/risk")

# مدیریت یادداشت احساسات
@app.route("/emotion", methods=["GET", "POST"])
def emotion():
    if request.method == "POST":
        note = request.form.get("note", "").strip()
        if note:
            save_note(EMOTION_NOTE, note)
    notes = load_notes(EMOTION_NOTE)
    return render_template("emotion.html", notes=notes)

@app.route("/emotion/delete/<int:index>", methods=["POST"])
def delete_emotion_note(index):
    notes = load_notes(EMOTION_NOTE)
    if 0 <= index < len(notes):
        del notes[index]
        with open(EMOTION_NOTE, "w", encoding="utf-8") as f:
            f.write("\n".join(notes) + "\n")
    return redirect("/emotion")

# صفحه نمایش تاریخچه تصمیمات ترید
@app.route("/history")
def history_view():
    history = load_history()
    return render_template("history.html", history=history[::-1])

# مسیر پاک‌سازی کل تاریخچه
@app.route("/clear-history", methods=["POST"])
def clear_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return redirect("/history")

# صفحه یادگیری تصویری (Learn)
@app.route("/learn", methods=["GET", "POST"])
def learn():
    sort_order = request.args.get("sort", "newest")
    posts = load_learn_posts()
    posts.sort(key=lambda x: x["timestamp"], reverse=(sort_order == "newest"))
    return render_template("learn.html", posts=posts, sort_order=sort_order)

# افزودن پست یادگیری جدید با تصویر
@app.route("/learn/add", methods=["POST"])
def add_learn_post():
    text = request.form.get("note", "").strip()
    file = request.files.get("image")
    if not file or file.filename == "":
        return redirect("/learn")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return redirect("/learn")
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(LEARN_IMG_DIR, filename)
    file.save(filepath)

    posts = load_learn_posts()
    posts.append({
        "image": filename,
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_learn_posts(posts)
    return redirect("/learn")

# حذف یک پست یادگیری
@app.route("/learn/delete/<int:index>", methods=["POST"])
def delete_learn_post(index):
    posts = load_learn_posts()
    if 0 <= index < len(posts):
        img = posts[index].get("image")
        if img:
            img_path = os.path.join(LEARN_IMG_DIR, img)
            if os.path.exists(img_path):
                os.remove(img_path)
        del posts[index]
        save_learn_posts(posts)
    return redirect("/learn")

# صفحه مشاهده بکاپ‌ها
@app.route("/export-backup")
def export_backup():
    notes_data = {
        "مدیریت سرمایه": load_notes(CAPITAL_NOTE),
        "مدیریت ریسک": load_notes(RISK_NOTE),
        "مدیریت احساسات": load_notes(EMOTION_NOTE)
    }
    return render_template("export_backup.html", notes_data=notes_data)

# خروجی گرفتن از یادداشت‌ها به فایل متنی TXT
@app.route("/export-txt")
def export_txt():
    content = ""
    for title, notes in [
        ("مدیریت سرمایه", load_notes(CAPITAL_NOTE)),
        ("مدیریت ریسک", load_notes(RISK_NOTE)),
        ("مدیریت احساسات", load_notes(EMOTION_NOTE))
    ]:
        content += f"{title}\n{'-'*30}\n"
        content += "\n".join(f"- {line}" for line in notes) + "\n\n"

    return send_file(
        io.BytesIO(content.encode("utf-8")),
        mimetype="text/plain",
        as_attachment=True,
        download_name="notes_export.txt"
    )

@app.route("/download/strategies")
def download_strategies():
    path = os.path.join(DATA_DIR, "strategies.json")
    return send_file(path, as_attachment=True, download_name="strategies_backup.json")

# خروجی گرفتن به ZIP از کل یادداشت‌ها
@app.route("/export-zip")
def export_zip():
    zip_stream = BytesIO()
    with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zf:
        files_to_zip = [
            "strategies.json", "learn_data.json",
            "journal_accounts.json", "journal_fields.json",
            "journal_strategies.json", "auth.json"
        ]
        for fname in files_to_zip:
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)

        # یادداشت‌های مدیریت سرمایه / ریسک / احساس (اینا توی notes/ هستن، نه ریشه‌ی DATA_DIR)
        for fname in ["capital.txt", "risk.txt", "emotion.txt"]:
            fpath = os.path.join(NOTES_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=os.path.join("notes", fname))

        # فایل‌های ژورنال هر حساب
        if os.path.isdir(JOURNAL_DIR):
            for fname in os.listdir(JOURNAL_DIR):
                zf.write(os.path.join(JOURNAL_DIR, fname), arcname=os.path.join("journal", fname))

        # باکس‌های هر استراتژی
        if os.path.isdir(JOURNAL_STRATEGY_FIELDS_DIR):
            for fname in os.listdir(JOURNAL_STRATEGY_FIELDS_DIR):
                zf.write(os.path.join(JOURNAL_STRATEGY_FIELDS_DIR, fname), arcname=os.path.join("journal_strategy_fields", fname))

        learn_img_folder = os.path.join("static", "learn_images")
        for root, dirs, files in os.walk(learn_img_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, "static")
                zf.write(full_path, arcname=os.path.join("static", rel_path))

        # عکس‌های آپلودشده‌ی ژورنال (journal_uploads/...)
        for root, dirs, files in os.walk(JOURNAL_UPLOAD_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DATA_DIR)
                zf.write(full_path, arcname=rel_path.replace(os.sep, "/"))

    zip_stream.seek(0)
    return send_file(zip_stream, as_attachment=True, download_name="notes_backup.zip")

# بازیابی یادداشت‌ها از فایل ZIP آپلود شده
@app.route("/restore-notes", methods=["POST"])
def restore_notes():
    file = request.files.get("backup_zip")
    if not file or not file.filename.endswith(".zip"):
        return "❌ فایل معتبر نبود."

    with zipfile.ZipFile(file) as zf:
        for member in zf.namelist():
            if member.startswith("static/"):
                # فایل‌های داخل static (عکس‌های آموزش، عکس‌های ژورنال) سر جای خودشون برگردن
                target_path = os.path.join("static", member[len("static/"):])
            else:
                # بقیه فایل‌ها (json/txt) برن داخل DATA_DIR
                target_path = os.path.join(DATA_DIR, member)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())

    return redirect("/export-backup")

# ---------- مدیریت استراتژی‌های ژورنال ----------
@app.route("/journal/strategies", methods=["GET"])
def journal_strategies_page():
    strategies = load_journal_strategies()
    return render_template("journal_strategies.html", strategies=strategies)


@app.route("/journal/strategies/add", methods=["POST"])
def journal_strategies_add():
    name = request.form.get("name", "").strip()
    if name:
        strategies = load_journal_strategies()
        strategies.append({"id": "st_" + uuid.uuid4().hex[:8], "name": name})
        save_journal_strategies(strategies)
    return redirect("/journal/strategies")


@app.route("/journal/strategies/rename/<strategy_id>", methods=["POST"])
def journal_strategies_rename(strategy_id):
    new_name = request.form.get("name", "").strip()
    strategies = load_journal_strategies()
    for s in strategies:
        if s["id"] == strategy_id and new_name:
            s["name"] = new_name
    save_journal_strategies(strategies)
    return redirect("/journal/strategies")


@app.route("/journal/strategies/delete/<strategy_id>", methods=["POST"])
def journal_strategies_delete(strategy_id):
    strategies = [s for s in load_journal_strategies() if s["id"] != strategy_id]
    save_journal_strategies(strategies)
    path = strategy_fields_path(strategy_id)
    if os.path.exists(path):
        os.remove(path)
    return redirect("/journal/strategies")


@app.route("/journal/strategies/<strategy_id>/fields", methods=["GET"])
def journal_strategy_fields_page(strategy_id):
    strategies = load_journal_strategies()
    strategy = next((s for s in strategies if s["id"] == strategy_id), None)
    if not strategy:
        return redirect("/journal/strategies")
    fields = load_strategy_fields(strategy_id)
    return render_template("journal_strategy_fields.html", strategy=strategy, fields=fields)


@app.route("/journal/strategies/<strategy_id>/fields/add", methods=["POST"])
def journal_strategy_fields_add(strategy_id):
    label = request.form.get("label", "").strip()
    field_type = request.form.get("type", "text")
    options_raw = request.form.get("options", "")
    options = [o.strip() for o in options_raw.splitlines() if o.strip()]

    if label:
        fields = load_strategy_fields(strategy_id)
        fields.append({
            "id": "f_" + uuid.uuid4().hex[:8],
            "label": label,
            "type": field_type,
            "options": options if field_type == "select" else [],
        })
        save_strategy_fields(strategy_id, fields)
    return redirect(f"/journal/strategies/{strategy_id}/fields")


@app.route("/journal/strategies/<strategy_id>/fields/edit/<field_id>", methods=["POST"])
def journal_strategy_fields_edit(strategy_id, field_id):
    label = request.form.get("label", "").strip()
    field_type = request.form.get("type", "text")
    options_raw = request.form.get("options", "")
    options = [o.strip() for o in options_raw.splitlines() if o.strip()]

    fields = load_strategy_fields(strategy_id)
    for f in fields:
        if f["id"] == field_id:
            if label:
                f["label"] = label
            f["type"] = field_type
            f["options"] = options if field_type == "select" else []
    save_strategy_fields(strategy_id, fields)
    return redirect(f"/journal/strategies/{strategy_id}/fields")


@app.route("/journal/strategies/<strategy_id>/fields/delete/<field_id>", methods=["POST"])
def journal_strategy_fields_delete(strategy_id, field_id):
    fields = [f for f in load_strategy_fields(strategy_id) if f["id"] != field_id]
    save_strategy_fields(strategy_id, fields)
    return redirect(f"/journal/strategies/{strategy_id}/fields")


@app.route("/journal/strategies/<strategy_id>/fields/move/<field_id>/<direction>", methods=["POST"])
def journal_strategy_fields_move(strategy_id, field_id, direction):
    fields = load_strategy_fields(strategy_id)
    idx = next((i for i, f in enumerate(fields) if f["id"] == field_id), None)
    if idx is not None:
        if direction == "up" and idx > 0:
            fields[idx - 1], fields[idx] = fields[idx], fields[idx - 1]
        elif direction == "down" and idx < len(fields) - 1:
            fields[idx + 1], fields[idx] = fields[idx], fields[idx + 1]
        save_strategy_fields(strategy_id, fields)
    return redirect(f"/journal/strategies/{strategy_id}/fields")


# ---------- مدیریت باکس‌های ژورنال (خودت اضافه/حذف/ادیت می‌کنی) ----------
@app.route("/journal/fields", methods=["GET"])
def journal_fields_page():
    fields = load_journal_fields()
    return render_template("journal_fields.html", fields=fields)


@app.route("/journal/fields/add", methods=["POST"])
def journal_fields_add():
    label = request.form.get("label", "").strip()
    field_type = request.form.get("type", "text")
    options_raw = request.form.get("options", "")
    options = [o.strip() for o in options_raw.splitlines() if o.strip()]

    if label:
        fields = load_journal_fields()
        fields.append({
            "id": "f_" + uuid.uuid4().hex[:8],
            "label": label,
            "type": field_type,
            "options": options if field_type == "select" else [],
        })
        save_journal_fields(fields)
    return redirect("/journal/fields")


@app.route("/journal/fields/edit/<field_id>", methods=["POST"])
def journal_fields_edit(field_id):
    label = request.form.get("label", "").strip()
    field_type = request.form.get("type", "text")
    options_raw = request.form.get("options", "")
    options = [o.strip() for o in options_raw.splitlines() if o.strip()]

    fields = load_journal_fields()
    for f in fields:
        if f["id"] == field_id:
            if label:
                f["label"] = label
            f["type"] = field_type
            f["options"] = options if field_type == "select" else []
    save_journal_fields(fields)
    return redirect("/journal/fields")


@app.route("/journal/fields/delete/<field_id>", methods=["POST"])
def journal_fields_delete(field_id):
    fields = [f for f in load_journal_fields() if f["id"] != field_id]
    save_journal_fields(fields)
    return redirect("/journal/fields")


# ---------- صفحه لیست حساب‌ها (اولین صفحه ژورنال) ----------
@app.route("/journal", methods=["GET"])
def journal_accounts_page():
    accounts = load_journal_accounts()
    return render_template("journal_accounts.html", accounts=accounts)


@app.route("/journal/add-account", methods=["POST"])
def journal_add_account():
    name = request.form.get("name", "").strip()
    if name:
        accounts = load_journal_accounts()
        accounts.append({"id": uuid.uuid4().hex[:8], "name": name})
        save_journal_accounts(accounts)
    return redirect("/journal")


@app.route("/journal/rename-account/<account_id>", methods=["POST"])
def journal_rename_account(account_id):
    new_name = request.form.get("name", "").strip()
    accounts = load_journal_accounts()
    for acc in accounts:
        if acc["id"] == account_id and new_name:
            acc["name"] = new_name
    save_journal_accounts(accounts)
    return redirect("/journal")


@app.route("/journal/delete-account/<account_id>", methods=["POST"])
def journal_delete_account(account_id):
    accounts = [a for a in load_journal_accounts() if a["id"] != account_id]
    save_journal_accounts(accounts)
    # فایل تریدهای همون حساب هم پاک بشه
    path = journal_trades_path(account_id)
    if os.path.exists(path):
        os.remove(path)
    return redirect("/journal")


# ---------- صفحه ژورنال یک حساب خاص ----------
@app.route("/journal/<account_id>", methods=["GET"])
def journal_account_page(account_id):
    accounts = load_journal_accounts()
    account = next((a for a in accounts if a["id"] == account_id), None)
    if not account:
        return redirect("/journal")
    trades = load_journal_trades(account_id)
    has_any_trade = len(trades) > 0
    strategies = load_journal_strategies()

    selected_id = request.args.get("strategy") or account.get("last_strategy_id")
    selected_strategy = next((s for s in strategies if s["id"] == selected_id), None)
    if not selected_strategy and strategies:
        selected_strategy = strategies[0]

    fields = load_strategy_fields(selected_strategy["id"]) if selected_strategy else []
    if selected_strategy:
        trades = [t for t in trades if t.get("strategy_id") == selected_strategy["id"]]

    return render_template(
        "journal_account.html",
        account=account,
        trades=trades[::-1],
        fields=fields,
        strategies=strategies,
        selected_strategy=selected_strategy,
        has_any_trade=has_any_trade,
        just_added=request.args.get("added"),
    )


@app.route("/journal/<account_id>/export-excel", methods=["GET"])
def journal_export_excel(account_id):
    accounts = load_journal_accounts()
    account = next((a for a in accounts if a["id"] == account_id), None)
    if not account:
        return redirect("/journal")

    trades = load_journal_trades(account_id)
    strategies = load_journal_strategies()

    selected_id = request.args.get("strategy") or account.get("last_strategy_id")
    selected_strategy = next((s for s in strategies if s["id"] == selected_id), None)
    if not selected_strategy and strategies:
        selected_strategy = strategies[0]

    fields = load_strategy_fields(selected_strategy["id"]) if selected_strategy else []
    if selected_strategy:
        trades = [t for t in trades if t.get("strategy_id") == selected_strategy["id"]]

    wb = Workbook()
    ws = wb.active
    ws.title = "Journal"

    headers = ["Date", "Strategy"] + [f["label"] for f in fields] + ["Notes", "Balance"]
    ws.append(headers)

    for t in trades:
        row = [t.get("date", ""), t.get("strategy_name", "")]
        row += [t.get(f["id"], "") for f in fields]
        row += [t.get("notes", ""), t.get("balance", "")]
        ws.append(row)

    for col in ws.columns:
        max_len = max((len(str(c.value)) if c.value else 0) for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 40)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    strategy_part = selected_strategy["name"] if selected_strategy else "journal"
    filename = f"{account['name']}_{strategy_part}.xlsx".replace(" ", "_")
    return send_file(stream, as_attachment=True, download_name=filename)


@app.route("/journal/<account_id>/set-starting-balance", methods=["POST"])
def journal_set_starting_balance(account_id):
    balance = request.form.get("starting_balance", "").strip()
    accounts = load_journal_accounts()
    for a in accounts:
        if a["id"] == account_id:
            a["starting_balance"] = balance
    save_journal_accounts(accounts)
    return redirect(f"/journal/{account_id}")


@app.route("/journal/<account_id>/add-trade", methods=["POST"])
def journal_add_trade(account_id):
    trades = load_journal_trades(account_id)
    strategy_id = request.form.get("strategy_id", "")
    strategies = load_journal_strategies()
    strategy = next((s for s in strategies if s["id"] == strategy_id), None)
    fields = load_strategy_fields(strategy_id) if strategy_id else []

    trade = {
        "id": uuid.uuid4().hex[:8],
        "date": request.form.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "strategy_id": strategy_id,
        "strategy_name": strategy["name"] if strategy else "",
        "notes": request.form.get("notes", ""),
        "balance": request.form.get("balance", ""),
        "photo": "",
    }
    for f in fields:
        trade[f["id"]] = request.form.get(f["id"], "")

    photo = request.files.get("photo")
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            account_upload_dir = os.path.join(JOURNAL_UPLOAD_DIR, account_id)
            os.makedirs(account_upload_dir, exist_ok=True)
            filename = f"{trade['id']}{ext}"
            photo.save(os.path.join(account_upload_dir, filename))
            trade["photo"] = filename

    trades.append(trade)
    save_journal_trades(account_id, trades)

    # یادش بمونه آخرین استراتژی‌ای که استفاده کردی چی بود
    if strategy_id:
        accounts = load_journal_accounts()
        for a in accounts:
            if a["id"] == account_id:
                a["last_strategy_id"] = strategy_id
        save_journal_accounts(accounts)

    return redirect(f"/journal/{account_id}?added=1")


@app.route("/journal/<account_id>/delete-trade/<trade_id>", methods=["POST"])
def journal_delete_trade(account_id, trade_id):
    trades = load_journal_trades(account_id)
    trade = next((t for t in trades if t["id"] == trade_id), None)
    if trade and trade.get("photo"):
        photo_path = os.path.join(JOURNAL_UPLOAD_DIR, account_id, trade["photo"])
        if os.path.exists(photo_path):
            os.remove(photo_path)
    trades = [t for t in trades if t["id"] != trade_id]
    save_journal_trades(account_id, trades)
    return redirect(f"/journal/{account_id}")


@app.route("/journal_uploads/<account_id>/<filename>")
def journal_uploaded_photo(account_id, filename):
    return send_from_directory(os.path.join(JOURNAL_UPLOAD_DIR, account_id), filename)


if __name__ == "__main__":
    ui = FlaskUI(app=app, server="flask", width=1000, height=900)
    ui.run()
