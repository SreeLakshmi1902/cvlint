import time
import pytest
from timing import StepTimer

def test_records_steps_in_order():
    timer = StepTimer()
    with timer.step("a"):
        time.sleep(0.01)
    with timer.step("b"):
        pass
    summary = timer.summary()
    assert [s["step"] for s in summary["steps"]] == ["a", "b"]
    assert summary["steps"][0]["seconds"] >= 0.01
    assert summary["total_seconds"] >= summary["steps"][0]["seconds"]

def test_records_step_even_when_it_fails():
    timer = StepTimer()
    with pytest.raises(ValueError):
        with timer.step("boom"):
            raise ValueError("fail")
    assert timer.summary()["steps"][0]["step"] == "boom"