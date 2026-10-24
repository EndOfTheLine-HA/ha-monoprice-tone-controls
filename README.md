# Monoprice tone controls for Home Assistant (temporary)

Adds **bass, treble and balance** controls for each zone of a Monoprice-compatible
6-zone amplifier, on top of everything Home Assistant's built-in **Monoprice
6-Zone Amplifier** integration does (power, volume, mute, source,
snapshot/restore).

> **This repository is temporary.** It exists until Home Assistant's built-in
> integration offers tone controls. A contribution to add them to Home Assistant
> is planned. When that ships, uninstall this repository and the built-in
> integration takes over with the same entities and history (see below).

## How it works, and what that means for you

This is a copy of Home Assistant's built-in Monoprice integration with tone
controls added. It keeps the same `monoprice` domain on purpose, so:

- **Your existing amplifier entry and zone entities are reused as they are.**
  Nothing to re-add, no entity IDs change.
- **While installed, it replaces the built-in integration.** Home Assistant logs
  a warning about this at startup. That is expected.
- **Fixes to the built-in integration do not reach you** until they are copied
  here, or until this repository is retired.
- It is a custom repository only and is not submitted to the HACS default
  catalog, which does not accept replacements for built-in integrations.

Tone controls are configuration entities on each zone's device page. Their
values come from the zone status the media player already polls, so they add no
extra serial traffic; changing one sends a single command to the amp.

## Install

1. In HACS, open **Custom repositories** and add
   `https://github.com/EndOfTheLine-HA/ha-monoprice-tone-controls` as an
   **Integration**.
2. Download **Monoprice tone controls**, then restart Home Assistant.
3. If you already have a Monoprice amplifier entry, you are done: the tone
   controls appear on each zone. Otherwise add **Monoprice 6-Zone Amplifier
   (tone controls)** from **Settings > Devices & services**.

Do not install another custom integration that also provides
`custom_components/monoprice`. Home Assistant **2026.9.4 or newer** is required.

## Coming from No Hassle AV 0.2.x

No Hassle AV 0.2.x handled both the amplifier and the HDMI matrix in the
`monoprice` domain. From 0.3.0 the matrix has its own `nohassle_av` integration
and this repository carries the amplifier and tone controls. Follow the upgrade
steps in the [No Hassle AV README](https://github.com/EndOfTheLine-HA/ha-nohassle-av#upgrading-from-02x).

If this repository finds an HDMI matrix entry from 0.2.x, it does not load it.
It hands the entry to No Hassle AV, which imports it with its entity IDs and
history, or shows a notification asking you to update No Hassle AV first.

## When Home Assistant gains tone controls

The tone-control entities use the unique ID format
`<config entry ID>_<zone>_<bass|treble|balance>`, and zones use
`<config entry ID>_<zone>`, the built-in integration's own format. Any
implementation in Home Assistant that keeps these formats reuses your existing
entities. At that point: uninstall this repository in HACS, restart, and check
that your zones and tone controls are provided by the built-in integration. This
README will say so when it happens.

## Development and validation

See [AUDIT.md](AUDIT.md). CI runs the tests on Home Assistant 2026.9.4 and
2026.10.2, plus Ruff, HACS validation and Hassfest. Tests use simulated
amplifier responses and never open a serial port.

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
