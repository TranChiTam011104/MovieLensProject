"""
Script để chạy FastAPI server.

CHẠY:
    python scripts/run_api.py

HOẶC (từ project root):
    uvicorn src.api.main:app --reload

DOCS:
    Swagger UI: http://localhost:8000/docs
    ReDoc:      http://localhost:8000/redoc
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


def main():
    """Run the API server."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎬 MovieLens Recommendation API                              ║
║                                                               ║
║   📖 Swagger UI:      http://localhost:8000/docs              ║
║   📚 ReDoc:          http://localhost:8000/redoc              ║
║   🏥 Health:        http://localhost:8000/health             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
