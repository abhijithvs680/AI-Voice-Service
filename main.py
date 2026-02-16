"""Entry point - runs the FastAPI app."""

import os

import uvicorn
from dotenv import load_dotenv
from loguru import logger

load_dotenv(override=True)


def main() -> None:
    port = int(os.getenv("PORT", "8520"))
    reload = os.getenv("ENV", "development").lower() == "development"
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
