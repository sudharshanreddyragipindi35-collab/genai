"""Start the local InterviewForge API."""

import logging

import uvicorn

from interviewforge.app import create_app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        app = create_app()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False)


if __name__ == "__main__":
    main()
