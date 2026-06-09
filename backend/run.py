import uvicorn
from app.main import create_app
from app.core.config import get_settings

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
