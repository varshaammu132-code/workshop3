"""
Student Management System - Server Launcher
Runs the FastAPI application using Uvicorn on http://127.0.0.1:8000
"""

import sys
import os
import webbrowser
import threading
import time
import uvicorn

# Ensure the root project directory and backend directory are in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def open_browser():
    """Wait 1.5 seconds for the server to bind, then launch browser."""
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n[INFO] Opening application in browser: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    print("=" * 65)
    print("🎓 EDU-TRACK: STUDENT MANAGEMENT SYSTEM")
    print("=" * 65)
    print("• Application UI:  http://127.0.0.1:8000")
    print("• Swagger API Docs: http://127.0.0.1:8000/docs")
    print("• ReDoc API Docs:   http://127.0.0.1:8000/redoc")
    print("=" * 65)
    print("Press CTRL+C in this terminal window to stop the server.\n")

    # Start browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Uvicorn ASGI server
    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
