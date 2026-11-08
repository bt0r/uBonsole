# uBonsole

An i3 setup for the **ClockworkPi uConsole** (CM4) built around software-defined radio: a pastel-on-black
status bar, a one-click radio app launcher, an SDR frequency cheat sheet and a power menu for the
HackerGadgets **AIO v2** board (GPS, LoRa, SDR, USB rails).

The interface is available in **English, French, German and Spanish**, and the frequency cheat sheet
is tailored to where you use the device: **France, United Kingdom, Germany, Spain, USA, Canada** or
generic **Europe (ITU Region 1)**. The accent color is yours to pick among six pastels: **pink**
(default), **blue**, **red**, **green**, **yellow** and **white**. Choose all three at install time.

## Screenshots

**SDR frequency cheat sheet** (USA region) — click the antenna icon in the bar

![SDR frequency cheat sheet](docs/screenshots/frequencies.png)

**Radio app launcher** — click the ear icon

![Radio app launcher](docs/screenshots/radio-launcher.png)

**Power menu** — click the battery

![Power menu](docs/screenshots/power-menu.png)

## Features

**Status bar** (i3bar + i3blocks), left to right:

| Block | Display | Click |
|---|---|---|
| Radio | antenna icon | SDR frequency cheat sheet for your region: broadcast, amateur radio, hobby bands, what you may and may not listen to, with the mode to use |
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

**Theming** — one pastel accent color on black for the bar, the window borders, the rofi menus and
the `$mod+d` launcher (`scripts/rofi-theme.rasi`), plus an optional dark Qt6 palette that makes GQRX
readable in the same color.

## Install

```bash
git clone https://github.com/bt0r/uBonsole.git
cd uBonsole
./install.sh
```

The installer asks for the language, the region and the accent color, offers to install missing packages, backs up
your current `~/.config/i3` to `~/.config/i3.backup-<date>`, copies the config, writes
`~/.config/i3/ubonsole.conf` and restarts i3. It detects the AIO v2 tool, the ADS-B service and
auto_rx, then lists which radio apps it found. It can also apply the Qt6 theme and install the SDR tools.

Non-interactive: `./install.sh --lang en --region us --color blue --qt-theme --yes`

### Dependencies

Required (the installer offers to install the missing ones with apt):

| For | Debian packages |
|---|---|
| Desktop and bar | `i3` `i3blocks` `rofi` `feh` `x11-xserver-utils` `fonts-font-awesome` `fonts-dejavu-core` |
| Bar blocks | `brightnessctl` `wireplumber` (volume) `network-manager` (Wi-Fi) `rfkill` (Bluetooth) |
| Screenshots | `maim` `xdotool` `xclip` |
| ADS-B map, auto_rx page | `firefox-esr` |
| Scripts | `python3` |
| Terminal | `st` (not in Debian under that name: the uConsole images ship it in `/usr/local/bin`; `stterm` + a symlink also works) |

Optional, per radio app. A missing app is shown as `(not installed)` in the launcher:

| App | Package / source | Installed by `tools/install-sdr-tools.sh` |
|---|---|---|
| GQRX | `gqrx-sdr` | yes |
| SDR++ | official `.deb` (SDRPlusPlus nightly) | yes |
| SatDump | `satdump` | yes |
| APRS | `direwolf` + `rtl-sdr` (`rtl_fm`) | yes |
| 433 MHz sensors | `rtl-433` | yes |
| ACARS / VDL2 | `acarsdec` / `dumpvdl2` (+ `libacars`), built from source | yes |
| Radiosondes | radiosonde_auto_rx, built from source in `~/src` | yes |
| ADS-B | `readsb` (or `dump1090-fa`) + `tar1090` | no, see their install scripts |
| Meshcore | `meshcore-console` ([meshcore-uconsole](https://github.com/cwill747/meshcore-uconsole)) | no |
| GPS | `gpsd` + `gpsd-clients` (`xgps`) | no |

`tools/install-sdr-tools.sh` targets Debian trixie on arm64 and builds part of the tools from
source, which takes a while on a CM4.

### HackerGadgets AIO v2 board (optional)

The power menu and the radio launcher switch the board's GPS, LoRa, SDR and USB rails through
[aiov2_ctl](https://github.com/hackergadgets/aiov2_ctl):

```bash
git clone https://github.com/hackergadgets/aiov2_ctl.git ~/aiov2_ctl
sudo python3 ~/aiov2_ctl/aiov2_ctl.py --install    # optional: installs the "aiov2_ctl" command
```

The installer finds either the `aiov2_ctl` command or `~/aiov2_ctl/aiov2_ctl.py`. Elsewhere, set
`AIOV2_CTL` in `ubonsole.conf`. Without the board, those toggles are simply hidden.

### Update

```bash
cd uBonsole && git pull && ./install.sh
```

Each run makes a new backup. The installer copies files but never deletes any, so files from an
older config stay in `~/.config/i3` until you remove them.

### Uninstall

Put a backup back and restart i3 (`$mod+Shift+r`):

```bash
rm -rf ~/.config/i3
mv ~/.config/i3.backup-<date> ~/.config/i3
```

## Configuration

`~/.config/i3/ubonsole.conf` is read on every click, so changes apply without restarting.
Reinstalling or updating keeps your values.

| Setting | Default | What it does |
|---|---|---|
| `UBONSOLE_LANG` | `en` | interface language: `en` `fr` `de` `es` |
| `UBONSOLE_REGION` | from the language | frequency sheet: `fr` `uk` `de` `es` `us` `ca` `eu` |
| `UBONSOLE_COLOR` | `pink` | accent color: `pink` `blue` `red` `green` `yellow` `white`. Applied by the installer: change it with `./install.sh --color <name>` |
| `AIOV2_CTL` | detected | `aiov2_ctl` command or path to `aiov2_ctl.py`; empty = no AIO v2 board |
| `SDR_DEVICE` | `0` | RTL-SDR index used by the text decoders (`rtl_test` lists the dongles) |
| `SDR_GAIN` | `40` | tuner gain in dB for those decoders |
| `ADSB_SERVICE` | detected | systemd service of the ADS-B decoder (`readsb`, `dump1090-fa`…) |
| `TAR1090_URL` | `http://localhost/tar1090` | page opened for ADS-B |
| `AUTORX_DIR` | detected | radiosonde_auto_rx folder (the one with `auto_rx.py`) |
| `BATTERY` | detected | battery in `/sys/class/power_supply` |

### Other hardware, antennas and dongles

- **Antennas**: the scripts never assume which connector an antenna is on. They only open the
  RTL-SDR, so plug the antenna that suits the band (the frequency sheet tells you which band you are
  on). A 1090 MHz antenna will hear little on 137 MHz satellites or HF, and vice versa.
- **External or several SDR dongles**: set `SDR_DEVICE` to the dongle the text decoders should use.
  GQRX, SDR++ and SatDump choose their device in their own settings, auto_rx in `station.cfg`,
  readsb in its own config (`/etc/default/readsb`).
- **No AIO v2 board**: leave `AIOV2_CTL` empty. Everything else works the same.
- **Not a uConsole**: the i3 config rotates the display `DSI-1` and the Wi-Fi block reads `wlan0`;
  adjust `config/i3/config` and `config/i3/i3blocks.conf`.

## Keyboard shortcuts

`$mod` is **Alt**.

| Keys | Action |
|---|---|
| `$mod+Return` | terminal (`st`) |
| `$mod+d` | app launcher |
| `$mod+1` … `$mod+0` | go to workspace 1–10 (`$mod+Shift+<n>` moves the window there) |
| `$mod+Home` / `$mod+End`, `$mod+PgUp` / `$mod+PgDn` | first / last, previous / next workspace |
| `$mod+j k l ;` or arrows | move focus (`$mod+Shift+…` moves the window) |
| `$mod+h` / `$mod+v` | split horizontally / vertically |
| `$mod+f` | fullscreen |
| `$mod+s` / `$mod+w` / `$mod+e` | stacked / tabbed / split layout |
| `$mod+Shift+space` | toggle floating |
| `$mod+Shift+p` / `$mod+Shift+m` | snap a floating window to the right / left half |
| `$mod+r` | resize mode (arrows, then Return or Escape) |
| `$mod+,` / `$mod+.` | brightness down / up |
| Volume keys | volume, mute |
| `Print` | screenshot to `~/Pictures` (`$mod+Print`: active window, `Shift+Print`: selection; add `Ctrl` to copy to the clipboard) |
| `$mod+Shift+q` | close window |
| `$mod+Shift+c` / `$mod+Shift+r` / `$mod+Shift+e` | reload config / restart i3 / quit |

## Using the radio apps

- **One app at a time**: the RTL-SDR dongle can only be opened by one program. The launcher stops
  the running app (and readsb) before starting another; "Stop all" frees the dongle.
- **sudo**: ADS-B starts and stops the `ADSB_SERVICE` service (readsb by default) with `sudo`. The ADS-B terminal asks for
  your password if needed. Other menus only call `sudo -n` (never prompt).
- **Text decoders** (ACARS, VDL2, APRS, 433 MHz, radiosondes) print a "listening on …" line, then
  one block per decoded message. A quiet terminal means nothing was received yet: check the antenna,
  go outside, or confirm activity on the waterfall in GQRX first.
- **Radiosondes**: auto_rx opens its web map on <http://localhost:5000>. Set your position in
  `~/src/radiosonde_auto_rx/auto_rx/station.cfg` first.
- **APRS** is receive-only (`config/direwolf/sdr.conf` uses the placeholder call sign `N0CALL`).

## Troubleshooting

- **A menu does not open**: rofi runs one window at a time. Close the open one with Escape, or click
  its icon again.
- **GQRX (or another Qt6 app) is white and hard to read**: run `./install.sh --qt-theme` to apply
  the dark Qt6 palette, then restart the app.
- **Changing the color by hand in `ubonsole.conf` does nothing**: the color is written into the
  installed files, so run `./install.sh --color <name>` instead.
- **GPS on the AIO v2 shows nothing**: on some images the GPS UART (`/dev/ttyS0`) is also used by the
  serial console and a login prompt, so gpsd never gets the NMEA data (`journalctl` shows failed
  logins like `$GNGGA…`). Remove `console=serial0,115200` from `/boot/firmware/cmdline.txt`, disable
  `serial-getty@ttyS0`, point gpsd at `/dev/ttyS0` and reboot.
- **A decoder says "usb_claim_interface error" or finds no device**: another app still holds the
  dongle (use "Stop all"), or `SDR_DEVICE` points to a dongle that is not plugged in.

## Layout

```
config/i3/config              i3 config
config/i3/i3blocks.conf       status bar blocks
config/i3/scripts/            block scripts, menus, launcher, rofi theme (common.sh: settings + helpers)
config/i3/lang/<lang>.sh      UI strings (en is the fallback)
config/i3/frequencies/        frequency cheat sheets, <region>/<lang>.txt, generated
config/i3/wallpapers/         wallpaper
config/qt6ct/colors/          Qt6 palette
config/direwolf/sdr.conf      direwolf receive-only config for APRS
tools/gen-frequencies.py      edit the frequency tables here, then run it
tools/install-sdr-tools.sh    SDR tools installer
tools/recolor.py              accent colors: swaps the reference pink in the installed files
```

## Adding a language

1. Copy `config/i3/lang/en.sh` to `config/i3/lang/<code>.sh` and translate the strings.
2. Add the language to `tr()` and every table in `tools/gen-frequencies.py`, then run it.
3. Add the code to `LANGS` / `LANG_NAMES` in `install.sh`.

## Adding a region

Add an entry to `REGIONS` and `TITLE` in `tools/gen-frequencies.py`, run it (it reports any line
that does not fit the screen), then add the code to `REGIONS` / `REGION_NAMES` in `install.sh`.

## Adding a color

Add the pastel to `ACCENTS` in `tools/recolor.py` (the other shades are derived from it), then to
`COLORS` in `install.sh`. Keep it readable on black.

## Notes

- Ranges follow the ITU Region 1 / Region 2 band plans and national allocations (ARCEP, Ofcom,
  BNetzA, CNAF, FCC, ISED), checked in 2026. "Do not listen" ranges are indicative blocks, not an
  official list, and the law differs between countries: check your local regulations.
- Based on the community config [dzaczek/Uconsole-i3](https://github.com/dzaczek/Uconsole-i3)
  and the default i3 config.

## License

[MIT](LICENSE)
