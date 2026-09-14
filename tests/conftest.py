import pytest

from gearshift.context import GearshiftContext


@pytest.fixture(autouse=True)
def reset_context_singleton():
    previous = GearshiftContext._instance
    GearshiftContext._instance = None
    yield
    GearshiftContext._instance = previous


@pytest.fixture
def test_context():
    return GearshiftContext(cfg={"security": {"key_system": "test"}})
