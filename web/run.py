"""
Запуск веб-платформи Learn Python

Використання:
    cd /Applications/XAMPP/xamppfiles/htdocs/learn_python
    python web/run.py

Відкрий: http://localhost:8000
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
