# uBonsole

An i3 setup for the **ClockworkPi uConsole** (CM4) built around software-defined radio: a pink-on-black
status bar, a one-click radio app launcher, an SDR frequency cheat sheet and a power menu for the
HackerGadgets **AIO v2** board (GPS, LoRa, SDR, USB rails).

The interface is available in **English, French, German and Spanish**: pick the language at install time.

## Screenshots

**SDR frequency cheat sheet** — click the antenna icon in the bar

![SDR frequency cheat sheet](docs/screenshots/frequencies.png)

**Radio app launcher** — click the ear icon

![Radio app launcher](docs/screenshots/radio-launcher.png)

**Power menu** — click the battery

![Power menu](docs/screenshots/power-menu.png)

## Features

**Status bar** (i3bar + i3blocks), left to right:

| Block | Display | Click |
|---|---|---|
| Radio | antenna icon | SDR frequency cheat sheet: broadcast, amateur radio, hobby bands, tolerated and forbidden ranges, with the mode to use |
| Ear | running SDR app (`ADS-B`, `GQRX`…) | radio app launcher |
| Brightness | `☀ 22%` | left +1 / right −1 |
| Volume | speaker icon follows the level | left = mute, wheel = ±5 % |
| CPU / RAM | fixed-width percentages | |
| Temperature, Wi-Fi IP, date | | |
| Battery | icon follows the level, red below 15 %, warning at 10 % | power menu |

**Radio launcher** — ADS-B (readsb + tar1090), GQRX, SDR++, SatDump, radiosondes (auto_rx), ACARS,
VDL2, APRS (direwolf), 433 MHz sensors (rtl_433), Meshcore, GPS. Only one app can use the SDR dongle,
so the launcher stops the running one first. Text-mode decoders open in a terminal on workspace 3.
Missing apps are flagged `(not installed)`.

**Power menu** — shows battery level, state and power draw, and toggles Wi-Fi, Bluetooth and the
AIO v2 rails (GPS, LoRa, SDR, USB, via [aiov2_ctl](https://github.com/hackergadgets/aiov2_ctl)).

**Workspaces** — 1 terminal, 2 web, 3 radio (GQRX, SDR++, SatDump, decoders), 4 ADS-B
(tar1090 runs in its own Firefox instance so it always lands on workspace 4).

**Theming** — rofi menus and the `$mod+d` launcher share one theme (`scripts/rofi-pink.rasi`);
an optional Qt6 palette makes GQRX readable in the same colors.

## Install

```bash
git clone https://github.com/bt0r/uBonsole.git
cd uBonsole
./install.sh
```

The installer asks for the language, offers to install missing packages, backs up your current
`~/.config/i3` to `~/.config/i3.backup-<date>`, copies the config and restarts i3. It can also apply
the Qt6 theme and install the SDR tools.

Non-interactive: `./install.sh --lang de --qt-theme --yes`

Change the language later in `~/.config/i3/ubonsole.conf` (`UBONSOLE_LANG=en|fr|de|es`).

### Requirements

- uConsole with Debian / Raspberry Pi OS trixie, i3, i3blocks, rofi, FontAwesome and DejaVu fonts
- `st` terminal
- Optional: HackerGadgets AIO v2 board and `aiov2_ctl` (`~/aiov2_ctl/aiov2_ctl.py`)
- Optional SDR tools: `tools/install-sdr-tools.sh` (SDR++, SatDump, direwolf, acarsdec, dumpvdl2,
  radiosonde_auto_rx; readsb + tar1090 for ADS-B are not installed by it)

## Layout

```
config/i3/config              i3 config
config/i3/i3blocks.conf       status bar blocks
config/i3/scripts/            block scripts, menus, launcher, rofi theme
config/i3/lang/<lang>.sh      UI strings (en is the fallback)
config/i3/frequencies/        frequency cheat sheets, generated
config/i3/wallpapers/         wallpaper
config/qt6ct/colors/          Qt6 palette
config/direwolf/sdr.conf      direwolf receive-only config for APRS
tools/gen-frequencies.py      edit the frequency tables here, then run it
tools/install-sdr-tools.sh    SDR tools installer
```

## Adding a language

1. Copy `config/i3/lang/en.sh` to `config/i3/lang/<code>.sh` and translate the strings.
2. Add the language to the tables in `tools/gen-frequencies.py` and run it.
3. Add the code to `LANGS` / `LANG_NAMES` in `install.sh`.

## Notes

- The frequency ranges follow the ITU/IARU Region 1 band plans and French allocations. The
  "do not listen" ranges are indicative blocks, not an official list. Check your local regulations.
- Based on the community config [dzaczek/Uconsole-i3](https://github.com/dzaczek/Uconsole-i3)
  and the default i3 config.
