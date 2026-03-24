#!/bin/bash
# MilAnon GUI Launcher
# Double-click to start the MilAnon web interface

cd /Users/sd/Documents/GitHub/Anonymizer_Tool_Army
source .venv/bin/activate

# Kill any existing Streamlit on port 8501
lsof -ti:8501 | xargs kill 2>/dev/null

# Open browser after short delay
(sleep 2 && open http://localhost:8501) &

# Start Streamlit
milanon gui
