import logging

import typer
import uvicorn

from ai_app.app import build_app
from ai_app.config import Stage, get_config


def launch_app(environment: Stage = Stage.dev, workers: int = 1):
    get_config().setup_logging()
    app = build_app()
    logging.info("Launching app server")
    uvicorn.run(
        app,
        host="0.0.0.0" if environment == Stage.prod else "localhost",
        port=get_config().port,
        workers=workers,
    )


def main():
    typer.run(launch_app)


if __name__ == "__main__":
    main()
