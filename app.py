#app.py

from flask import Flask, render_template, request, redirect, send_file, url_for, send_from_directory
from flaskwebgui import FlaskUI
from strategy_engine import load_strategies, save_strategy, delete_strategy
from datetime import datetime
from io import BytesIO
import os
import sys
import json
import io
import zipfile
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__, static_url_path='/static')

# مسیرهای پایه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPDATA = os.getenv("APPDATA")
DATA_DIR = os.path.join(os.environ["APPDATA"], "TradingAppBS")
NOTES_DIR = os.path.join(DATA_DIR, "notes")
LEARN_IMG_DIR = os.path.join(DATA_DIR, "learn_images")
LEARN_DATA_FILE = os.path.join(DATA_DIR, "learn_data.json")

# پوشه‌های لازم
os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(LEARN_IMG_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
CAPITAL_NOTE = os.path.join(NOTES_DIR, "capital.txt")
RISK_NOTE = os.path.join(NOTES_DIR, "risk.txt")
EMOTION_NOTE = os.path.join(NOTES_DIR, "emotion.txt")

# pasword welcome
VALID_USERNAME = "mehdi"
VALID_PASSWORD = "1382"

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

# نمایش تصویرهای Learn از پوشه دائمی
@app.route("/learn_images/<filename>")
def learn_image(filename):
    return send_from_directory(LEARN_IMG_DIR, filename)

# صفحه خوش‌آمدگویی و ورود
@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user == VALID_USERNAME and pwd == VALID_PASSWORD:
            return redirect("/dashboard")
        return render_template("welcome.html", error="نام کاربری یا رمز عبور اشتباه است!")
    return render_template("welcome.html")

# خروج از سیستم
@app.route("/logout")
def logout():
    return redirect("/")

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
            if current_risk >= MAX_RISK:
                current_risk = risk_start
                cycle_count = 0
            if consecutive_wins >= 5:
                current_risk = max(risk_start, current_risk - 0.25)
                message = "یک سود استراحت"
                consecutive_wins = 0

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

# صفحه استراتژی‌ها
@app.route("/strategies", methods=["GET"])
def strategies_page():
    strategies = load_strategies()
    return render_template("strategies.html", strategies=strategies)

@app.route("/strategies/test", methods=["POST"])
def strategies_test():
    cycle = request.form.get("cycle")
    direction = request.form.get("direction")
    strategies = load_strategies()

    filtered = [s for s in strategies if s["cycle_type"] == cycle and s["direction"] == direction]

    i = 0
    while f"condition_{i}" in request.form:
        cond_value = request.form.get(f"condition_{i}")
        filtered = [s for s in filtered if len(s["conditions"]) > i and s["conditions"][i] == cond_value]
        i += 1

    if not filtered:
        return render_template("strategies.html", strategies=strategies, test_result="❌ هیچ استراتژی با این شرایط پیدا نشد")

    return render_template("strategies.html", strategies=strategies, test_result=filtered[0]["result"])

@app.route("/strategies/add", methods=["POST"])
def strategies_add():
    name = request.form.get("name")
    cycle_type = request.form.get("cycle_type")
    direction = request.form.get("direction")
    titles = request.form.getlist("condition_titles")
    values = request.form.getlist("condition_values")
    result = request.form.get("result")
    conditions = request.form.getlist("condition_values")
    save_strategy(name, cycle_type, direction, conditions, result)
    return redirect("/strategies")

@app.route("/strategies/delete/<int:index>", methods=["POST"])
def delete_strategy_route(index):
    delete_strategy(index)
    return redirect("/strategies")
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
            "capital.txt", "risk.txt", "emotion.txt",
            "strategies.json", "learn_data.json"
        ]
        for fname in files_to_zip:
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)

        learn_img_folder = os.path.join("static", "learn_images")
        for root, dirs, files in os.walk(learn_img_folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, "static")
                zf.write(full_path, arcname=os.path.join("static", rel_path))

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
            if member.startswith("static/learn_images/"):
                # تصاویر آموزش برگرده به static/learn_images/
                target_path = os.path.join("static", member[len("static/"):])
            else:
                # بقیه فایل‌ها برن داخل DATA_DIR
                target_path = os.path.join(DATA_DIR, member)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())

    return redirect("/export-backup")

if __name__ == "__main__":
    ui = FlaskUI(app=app, server="flask", width=1000, height=900)
    ui.run()
