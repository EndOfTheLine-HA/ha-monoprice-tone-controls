"""A bare Home Assistant instance. No test opens a serial port."""

from __future__ import annotations

import pytest

from homeassistant.core import HomeAssistant


@pytest.fixture
async def hass(tmp_path):
    instance = HomeAssistant(str(tmp_path))
    yield instance
    await instance.async_stop(force=True)
