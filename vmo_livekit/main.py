"""VMO LiveKit — main entry point.

Usage:
    python -m vmo_livekit

Environment variables control all configuration. See config.py.
LiveKit SIP is handled at the server level — no special worker config needed.
"""

from livekit.agents.cli import run_worker

from .agent import create_worker
from .metrics import init_otel, setup_logging


def main() -> None:
    setup_logging()
    init_otel()

    worker = create_worker()
    run_worker(worker)


if __name__ == "__main__":
    main()
