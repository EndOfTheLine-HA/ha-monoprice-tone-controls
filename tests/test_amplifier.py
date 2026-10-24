"""Amplifier, tone controls and the HDMI matrix hand-over."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.monoprice import async_setup_entry
from custom_components.monoprice.config_flow import MonoPriceConfigFlow
from custom_components.monoprice.media_player import MonopriceZone
from custom_components.monoprice.number import NUMBERS, MonopriceZoneNumber
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.exceptions import ConfigEntryError
from homeassistant.loader import IntegrationNotFound

SOURCES = [{1: "Input 1"}, {"Input 1": 1}, ["Input 1"]]


def test_unique_ids_are_pinned():
    """These formats must match the eventual core implementation exactly.

    They are what lets core's built-in integration, or this repository, provide
    the same registry entries, so zone and tone-control entities keep their
    entity IDs and history whichever code is installed.
    """
    runtime = SimpleNamespace(client=Mock(), zone_status={})
    zone = MonopriceZone(runtime.client, SOURCES, "entry-1", 11, runtime)
    assert zone.unique_id == "entry-1_11"
    assert {description.key for description in NUMBERS} == {"bass", "treble", "balance"}
    for description in NUMBERS:
        number = MonopriceZoneNumber(runtime, "entry-1", 11, description)
        assert number.unique_id == f"entry-1_11_{description.key}"


def test_tone_controls_send_one_command_with_the_amp_offset():
    amp = Mock()
    runtime = SimpleNamespace(client=amp, zone_status={})
    for description in NUMBERS:
        number = MonopriceZoneNumber(runtime, "entry-1", 11, description)
        number.schedule_update_ha_state = Mock()
        number.set_native_value(0)
        getattr(amp, description.setter).assert_called_with(11, description.offset)


def test_zone_power_reaches_the_amp():
    amp = Mock()
    runtime = SimpleNamespace(client=amp, zone_status={})
    zone = MonopriceZone(amp, SOURCES, "entry-1", 11, runtime)
    zone.turn_on()
    amp.set_power.assert_called_with(11, True)


async def test_existing_amp_entry_sets_up_as_an_amplifier():
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_forward_entry_setups=AsyncMock()),
        async_add_executor_job=AsyncMock(return_value=Mock()),
    )
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={"port": "/dev/ttyUSB0", "not_first_run": True},
        async_on_unload=Mock(),
        add_update_listener=Mock(),
    )
    await async_setup_entry(hass, entry)
    assert hass.config_entries.async_forward_entry_setups.call_args.args[1] == [
        "media_player",
        "number",
    ]
    assert entry.data == {"port": "/dev/ttyUSB0", "not_first_run": True}
    assert entry.runtime_data.first_run is False


def _matrix_entry():
    return SimpleNamespace(
        entry_id="matrix-entry",
        data={
            "device_type": "matrix",
            "host": "192.0.2.10",
            "http_port": 80,
            "input_names": [f"Input {i}" for i in range(1, 9)],
        },
    )


async def test_matrix_entry_is_refused_and_handed_to_no_hassle_av(hass):
    entry = _matrix_entry()
    init = AsyncMock()
    # A bare instance has no config entries manager; only the flow is needed.
    hass.config_entries = SimpleNamespace(flow=SimpleNamespace(async_init=init))
    with patch("custom_components.monoprice.async_get_integration", new=AsyncMock()):
        with pytest.raises(ConfigEntryError, match="No Hassle AV"):
            await async_setup_entry(hass, entry)
        # The hand-over starts only after the refusal, so the matrix entities
        # are never loaded by this integration.
        init.assert_not_awaited()
        await hass.async_block_till_done()
    init.assert_awaited_once_with(
        "nohassle_av",
        context={"source": SOURCE_IMPORT},
        data={"legacy_entry_id": "matrix-entry"},
    )


async def test_matrix_without_no_hassle_av_installed_explains_what_to_do(hass):
    entry = _matrix_entry()
    with (
        patch(
            "custom_components.monoprice.async_get_integration",
            new=AsyncMock(side_effect=IntegrationNotFound("nohassle_av")),
        ),
        patch(
            "custom_components.monoprice.persistent_notification.async_create"
        ) as notify,
    ):
        with pytest.raises(ConfigEntryError):
            await async_setup_entry(hass, entry)
        await hass.async_block_till_done()
    assert notify.call_args.kwargs["notification_id"] == (
        "monoprice_matrix_moved_matrix-entry"
    )


async def test_config_flow_is_amplifier_only_and_blocks_duplicates():
    flow = MonoPriceConfigFlow()
    flow.hass = SimpleNamespace()
    result = await flow.async_step_user()
    assert result["type"] == "form" and result["step_id"] == "user"
    flow._async_current_entries = lambda: [SimpleNamespace(data={"port": "same-port"})]
    with patch(
        "custom_components.monoprice.config_flow.validate_input", new=AsyncMock()
    ) as connect:
        result = await flow.async_step_user({"port": "same-port"})
    assert result["reason"] == "already_configured"
    connect.assert_not_called()
