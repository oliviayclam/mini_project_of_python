# Network Cabling System

React + FastAPI app for rack/cabling inventory, vendor work orders, change requests, floor plans, reports, audit logs, and optional DWDM.

**Development location:**  
`/Users/oliviayclam/Documents/GitHub/mini_project_of_python/PythonTestProject/NetworkCabling`

## Demo users

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | all functions |
| operator | operator123 | view/approve work orders & change requests |
| operator2 | operator123 | second approver |
| vendor | vendor123 | draft/submit cable orders |
| deptadmin | dept123 | invoice/department reports |

## Setup

From the GitHub repo root:

```bash
cd /Users/oliviayclam/Documents/GitHub/mini_project_of_python/PythonTestProject/NetworkCabling
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

Optional: set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env`.

## Features included

- Auth with roles: admin / operator / vendor / department_admin
- Inventory: sites, floors, rooms, racks/ODF, cages, shelves, panels, ports, cables
- Rack/cage details: manufacturer, model, serial, install/expire dates, asset tag
- DB-driven cable types, service types, cost centres, port statuses (color picker)
- Work orders with 1 or N+1 full-path lines, suggestions for drafts, approve/reject emails
- Change requests with 1–2 approvers, then apply to inventory
- Search (2D first, optional 3D switch)
- Floor-plan drawing + path length estimate
- Admin reports, termination requests, audit log export
- Optional DWDM systems/links/channels

## Email

If SMTP is not configured, emails are **simulated** to console and stored in `email_outbox`.

Env vars: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM`.
