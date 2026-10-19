from fastapi import FastAPI
from dotenv import load_dotenv

from app.configs.settings import get_settings

load_dotenv()

settings = get_settings()

app = FastAPI(
    title = settings.app_name
)

@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello, World!"}


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
