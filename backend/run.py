"""Chạy server ở chế độ phát triển: python run.py"""

from __future__ import annotations

import sys

import uvicorn

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
