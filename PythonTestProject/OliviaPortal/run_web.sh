#!/bin/bash
# Always run the website with this project's virtualenv.
cd "$(dirname "$0")"
source .venv/bin/activate
exec python web/app.py
