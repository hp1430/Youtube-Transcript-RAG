from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello, World!"}


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
