# Monoprice tone controls for Home Assistant (retired)

> **This repository is retired.** It was a temporary stand-in that added bass,
> treble and balance to Home Assistant's Monoprice 6-zone amplifier integration.
> The same thing is now a permanent integration of its own:
> **[No Hassle AV Amplifier](https://github.com/EndOfTheLine-HA/ha-nohassle-amp)**
> (`nohassle_amp`). Please move to it. Nothing new will be released here.

## Moving to No Hassle AV Amplifier

No Hassle AV Amplifier imports your existing amplifier and keeps every zone,
bass, treble and balance control, name, area, disabled zone and the history.

1. Make a full Home Assistant backup.
2. In HACS, add `https://github.com/EndOfTheLine-HA/ha-nohassle-amp` as a custom
   **Integration**, download it, and restart Home Assistant.
3. Open **Settings > Devices & services > Add integration > No Hassle AV
   Amplifier** and choose **Import the existing amplifier**.
4. Check that your zones and sliders are back with their old names, then
   uninstall **Monoprice tone controls** in HACS and restart.

The details, including what to do if the import cannot remove the old entry, are
in the [No Hassle AV Amplifier README](https://github.com/EndOfTheLine-HA/ha-nohassle-amp#moving-from-the-monoprice-integration).

Anything of yours that calls `monoprice.snapshot` or `monoprice.restore` must call
`nohassle_amp.snapshot` or `nohassle_amp.restore` instead.

## What this was

A copy of Home Assistant's built-in Monoprice integration with tone controls
added, keeping the `monoprice` domain so existing entries and entities carried over
unchanged. Because it replaced a built-in integration it could only ever be a custom
repository and could not be listed in the HACS default catalog, which is why the
amplifier moved to its own domain. See [AUDIT.md](AUDIT.md) and [NOTICE](NOTICE).

Apache-2.0. See [LICENSE](LICENSE).
