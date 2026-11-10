# Trading-B-S

**Your trading companion. Organize, analyze, improve.**

Trading-B-S is a local desktop application built for traders who want to systematize their process — from journaling every trade to documenting rules, reviewing lessons, and preparing for prop-firm evaluations. No cloud, no subscriptions, no internet required. Your data stays on your machine.

---

## User Guide

### ★ Account Security
Set a single password on first launch. All data is encrypted at rest using `werkzeug.security`. No hardcoded credentials — you create your own user on initial setup.

### ★ Dark & Night Mode
Full dark theme by default with a dedicated night mode toggle. Both themes persist across restarts and adapt to your session preference.

### ★ MT5 Statement Import
Parse any MT5 `.xml` or `.html` statement file directly in the app. The parser extracts balance history, trades, lots, P&L, and drawdown — then renders them into an interactive equity curve and trade table.

### ★ Rule Management
Write, edit, and pin your trading rules inside the app. Rules are stored as notes and always accessible from the dashboard — your checklist, visible every time you open the software.

### ★ Learn Vault
Store trading lessons with screenshots. Each entry supports a title, markdown body, and one or more images. Lessons are organized chronologically and searchable.

### ★ Multi-Account Journal
Manage unlimited trading accounts under one roof. For each account you can:
- Assign a strategy (with custom parameters)
- Track balance, equity, drawdown
- Log individual trades with entry/exit, lot size, P&L
- Export journal entries to Excel or PDF

### ★ Strategy Engine
Define strategies with cycle type, direction, and entry conditions. Each strategy run records the result — win/loss, R-multiples, and notes — so you can backtest ideas without leaving the app.

### ★ Backup & Sync
One-click backup zips your entire data directory (`TradingAppBS/`) into a portable archive. Restore on Windows, Android, or macOS from the same backup file. No cloud dependency.

### ★ Risk & Emotion Notes
Three dedicated note slots — Capital, Risk, and Emotion — for the non-technical side of trading. Pre-filled templates guide you through position sizing, daily P&L limits, and emotional state tracking.

### ★ Offline-First Architecture
Everything runs locally. Flask + FlaskWebGUI wraps the app in a desktop window. No API calls, no telemetry, no ads. If it fails on first open, close and reopen — the data directories self-heal on second launch.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, FlaskWebGUI |
| Data | Local JSON files under `%APPDATA%/TradingAppBS` |
| Export | openpyxl (Excel), reportlab (PDF) |
| Packaging | PyInstaller |

---

## Disclaimer

Trading financial markets involves significant risk. Trading-B-S is provided for educational and informational purposes only. It does not constitute financial or investment advice. Users are fully responsible for their own trading decisions, risk management, profits, and losses. Past performance does not guarantee future results.

## License

Personal use permitted. Commercial distribution, resale, reproduction, or republication of any part of this project requires prior written authorization from the author.

© 2026 Arad. All Rights Reserved.
