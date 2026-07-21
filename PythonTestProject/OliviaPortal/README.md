# Olivia Portal

Personal CLI + website with login, games, and expense BI reports.

## Demo login

- Username: `olivia`
- Password: `1234`

## Setup (once)

```bash
cd OliviaPortal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 1) Terminal app (Phases 1–4)

```bash
cd OliviaPortal
source .venv/bin/activate
python3 main.py
```

Menus:

1. **Games** — Number Guessing, Rock-Paper-Scissors  
2. **Data & BI** — view CSV, summary, chart, auto-export report  

Files:

- Sample data: `data/expenses.csv`
- Charts: `data/charts/`
- Auto reports: `data/reports/`

## 2) Website (Flask)

```bash
cd OliviaPortal
source .venv/bin/activate
python3 web/app.py
```

Open http://127.0.0.1:5000

- Login page
- Games page (Number Guessing + Rock-Paper-Scissors in the browser)
- Data & BI page (table, totals, create chart, auto-export report)

## How a website works here

```text
Browser  →  Flask (web/app.py)  →  same auth.py + bi/ code
   ↑                ↓
 HTML pages    users.json + expenses.csv
```

Your terminal app and website share the same login and BI logic.

## Project layout

```text
OliviaPortal/
  main.py auth.py menu.py users.json
  games/          # Phase 2 (CLI)
  bi/             # Phase 3 + 4
  data/           # CSV, charts, reports
  web/            # Flask website
  .venv/          # Python packages
```
