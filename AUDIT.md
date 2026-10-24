# Audit

## Privacy boundary

A private Home Assistant installation was used only to verify compatibility.
This repository excludes personal names, network addresses, serial device paths,
configuration-entry identifiers, room and source labels, and entity inventories.
Tests use placeholder values and the documentation address 192.0.2.10.

## What this repository is

A copy of Home Assistant Core's `monoprice` integration (Apache-2.0) with a
`number` platform adding bass, treble and balance per zone. It keeps the core
domain deliberately, so existing amplifier entries and entities are reused, and
it is meant to be retired once core offers tone controls.

## Behaviour confirmed by tests

- Zone unique IDs are `<entry ID>_<zone>` (core's format) and tone-control unique
  IDs are `<entry ID>_<zone>_<bass|treble|balance>`. Both are pinned by a test,
  because keeping them is what lets core (or this repository) reuse the same
  registry entries later.
- Tone controls read the zone status the media player already caches; setting
  one sends a single command with the amplifier's offset.
- An existing amplifier entry sets up as an amplifier with its data unchanged.
- The config flow is amplifier-only and refuses a second entry for the same
  connection.
- An HDMI matrix entry left by No Hassle AV 0.2.x is never loaded. Setup fails
  with a clear error (so its entities stay unloaded and can be moved), then
  hands the entry to the `nohassle_av` import flow, or creates a notification
  when No Hassle AV is not installed.

## Deliberate exclusions

- No HDMI matrix code (it lives in `ha-nohassle-av`).
- Not submitted to the HACS default catalog.

## Validation boundary

Automated tests use simulated amplifier responses and never open a serial port.
CI runs Ruff, the tests on Home Assistant 2026.9.4 and 2026.10.2, HACS
validation and Hassfest. Long-term behaviour with every amplifier firmware is
not claimed.
