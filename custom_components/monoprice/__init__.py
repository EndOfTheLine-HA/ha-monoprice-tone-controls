"""The Monoprice 6-Zone Amplifier integration, with bass, treble and balance.

Temporary stand-in for Home Assistant's built-in Monoprice integration until it
offers tone controls. Derived from Home Assistant Core's integration (see NOTICE).
"""

from dataclasses import dataclass, field
import logging
from typing import Any

from pymonoprice import Monoprice, get_monoprice
from serialx import SerialException

from homeassistant.components import persistent_notification
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import IntegrationNotFound, async_get_integration

from .const import CONF_NOT_FIRST_RUN, DOMAIN
from .services import async_setup_services

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.NUMBER]

# HDMI matrix entries made by No Hassle AV 0.2.x, which used this domain. They
# belong to the `nohassle_av` integration now.
MATRIX_DEVICE_TYPE = "matrix"
MATRIX_DOMAIN = "nohassle_av"

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type MonopriceConfigEntry = ConfigEntry[MonopriceRuntimeData]


@dataclass
class MonopriceRuntimeData:
    """Data stored in the config entry for a Monoprice entry."""

    client: Monoprice
    first_run: bool
    # Latest ZoneStatus per zone id, written by the media_player poll and read
    # by the number entities so bass/treble/balance add no serial queries.
    zone_status: dict[int, Any] = field(default_factory=dict)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MonopriceConfigEntry) -> bool:
    """Set up Monoprice 6-Zone Amplifier from a config entry."""
    if entry.data.get("device_type") == MATRIX_DEVICE_TYPE:
        # Never load a matrix here: its entities must stay unloaded so the
        # No Hassle AV import can move them, keeping their entity IDs. The
        # hand-over runs after this setup has finished failing.
        hass.async_create_task(
            async_hand_over_matrix(hass, entry),
            "Hand HDMI matrix to No Hassle AV",
            eager_start=False,
        )
        raise ConfigEntryError(
            "This HDMI matrix entry belongs to the No Hassle AV integration "
            "(nohassle_av) from version 0.3.0"
        )

    port = entry.data[CONF_PORT]

    try:
        monoprice = await hass.async_add_executor_job(get_monoprice, port)
    except SerialException as err:
        _LOGGER.error("Error connecting to Monoprice controller at %s", port)
        raise ConfigEntryNotReady from err

    # double negative to handle absence of value
    first_run = not bool(entry.data.get(CONF_NOT_FIRST_RUN))

    if first_run:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_NOT_FIRST_RUN: True}
        )

    entry.async_on_unload(entry.add_update_listener(_update_listener))

    entry.runtime_data = MonopriceRuntimeData(
        client=monoprice,
        first_run=first_run,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_hand_over_matrix(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Start the No Hassle AV import for an old matrix entry, or say what to do."""
    try:
        await async_get_integration(hass, MATRIX_DOMAIN)
    except IntegrationNotFound:
        persistent_notification.async_create(
            hass,
            "An HDMI matrix set up with No Hassle AV 0.2.x was found. From 0.3.0 the "
            "matrix has its own integration: update No Hassle AV in HACS, restart, "
            "and it is imported automatically with its entity IDs and history.",
            title="HDMI matrix moved to No Hassle AV",
            notification_id=f"monoprice_matrix_moved_{entry.entry_id}",
        )
        return
    await hass.config_entries.flow.async_init(
        MATRIX_DOMAIN,
        context={"source": SOURCE_IMPORT},
        data={"legacy_entry_id": entry.entry_id},
    )


async def async_unload_entry(hass: HomeAssistant, entry: MonopriceConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    def _cleanup(monoprice) -> None:
        """Destroy the Monoprice object.

        Destroying the Monoprice closes the serial connection,
        do it in an executor so the garbage collection
        does not block.
        """
        del monoprice

    await hass.async_add_executor_job(_cleanup, entry.runtime_data.client)

    return True


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
