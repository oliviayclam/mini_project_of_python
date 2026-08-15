# mini_project_of_python

Python learning / mini projects.

## Projects

- `PythonTestProject/OliviaPortal` — login portal with games and simple BI reports
- `PythonTestProject/NetworkCabling` — Network & Cabling system (React + FastAPI)

### Run Network Cabling

```bash
cd PythonTestProject/NetworkCabling/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
cd PythonTestProject/NetworkCabling/frontend
npm install
npm run dev
```
