from pathlib import Path
from typing import Optional

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--results-dir",
        action="store",
        default=None,
        help="Directory where performance tests should save results",
    )


@pytest.fixture(scope="session")
def results_dir(request) -> Optional[Path]:
    """Path to results dir provided via --results-dir (or None)."""
    val = request.config.getoption("results_dir")
    return Path(val) if val else None
