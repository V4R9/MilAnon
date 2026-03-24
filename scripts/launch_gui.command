#!/bin/bash
# MilAnon GUI Launcher
# Double-click to start the MilAnon web interface

export PATH="/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$PATH"

cd /Users/sd/Documents/GitHub/Anonymizer_Tool_Army

# Kill any existing Streamlit on port 8501
lsof -ti:8501 | xargs kill 2>/dev/null

# Use the venv Python directly (more reliable than source activate)
.venv/bin/python -m streamlit run src/milanon/gui/app.py --server.port 8501 &

# Wait for server to start, then open browser
sleep 3
open http://localhost:8501

# Keep terminal open
wait
