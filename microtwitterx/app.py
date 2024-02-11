from fastapi import FastAPI
from .routes import main_router

app = FastAPI(
    title="Micro Twitter X",
    version="0.1.0",
    description="Microblog API developed with FastAPI Framework for Python to post texts like a Twitter/X",
)

app.include_router(main_router)

if __name__ == "__main__":
    app()