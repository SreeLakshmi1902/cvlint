import logging
import time
from contextlib import contextmanager

logger = logging.getLogger("cvlint.timing")

class StepTimer:
    """Records wall-clock time for each named pipeline step in one request."""

    def __init__(self) -> None:
        self.steps: list[dict] = []
        self._start = time.perf_counter()

    @contextmanager
    def step(self, name: str):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            seconds = time.perf_counter() - t0
            self.steps.append({"step": name, "seconds": round(seconds, 2)})
            logger.info("step=%s seconds=%.2f", name, seconds)

    def summary(self) -> dict:
        total = time.perf_counter() - self._start
        return {"total_seconds": round(total, 2), "steps": self.steps}