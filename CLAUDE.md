# uBonsole — repository rules

i3 setup for the ClockworkPi uConsole (CM4) built around SDR: i3bar + i3blocks status bar, rofi menus
(radio launcher, power menu, frequency cheat sheet), installer. Users install it with `./install.sh`,
which copies `config/` into `~/.config/i3` (and qt6ct / direwolf) and writes `~/.config/i3/ubonsole.conf`.

## Language

- Everything in the repository is in **English**: code, comments, commit messages, README, this file.
- User-facing strings are translated, never hardcoded in scripts:
  - UI strings live in `config/i3/lang/<lang>.sh` (`en`, `fr`, `de`, `es`). Add a new string to
    **all four** files in the same change; `en.sh` is the fallback.
  - Frequency cheat sheets are generated: edit `tools/gen-frequencies.py`, run it, commit the
    generated `config/i3/frequencies/<region>/<lang>.txt`. Never edit the `.txt` files by hand.

## Commits (Karma convention)

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**: `feat` (new feature), `fix` (bug fix), `docs` (documentation only), `style` (formatting,
  no code change), `refactor` (no feature, no fix), `perf`, `test`, `chore` (build, tooling, assets).
- **scope** (optional, lowercase): `bar`, `radio`, `power`, `session`, `launcher`, `freq`, `i18n`, `theme`,
  `install`, `sdr-tools`, `readme`. Use the part of the project the change is about.
- **subject**: imperative present tense ("add", not "added" / "adds"), lowercase first letter, no
  final period, 72 characters max for the whole first line.
- **body**: what changed and why, wrapped at 72 characters. Bullet lists are fine.
- **footer**: `BREAKING CHANGE: <what users must do>` when `install.sh` options, `ubonsole.conf`
  settings or installed file names change incompatibly; `Closes #<n>` for issues.
- One logical change per commit. A feature and its README update go in the same commit.
- Commit identity for this repository: `bt0r <22751731+bt0r@users.noreply.github.com>` (set in the
  local git config). Never commit with a personal or work e-mail.
- Do not rewrite history that is already on `origin/main`.

Examples:

```
feat(radio): add AIS-catcher to the radio launcher
fix(power): compute the power draw from voltage and current
docs(readme): document the SDR_DEVICE setting
```

## Keep the README up to date

Update `README.md` in the same commit whenever a change affects users:

| Change | Update in the README |
|---|---|
| New or removed dependency (`DEPS` in `install.sh`, `tools/install-sdr-tools.sh`, a new command used by a script) | the *Dependencies* tables |
| New, renamed or removed setting in `ubonsole.conf` | the *Configuration* table |
| New `install.sh` option or question | *Install* (and the non-interactive example) |
| New block, menu entry, radio app or keyboard shortcut | *Features*, *Using the radio apps*, *Keyboard shortcuts* |
| New language, region or color | the intro, *Configuration*, and the matching *Adding a …* section |
| New file or folder that users or contributors should know | *Layout* |
| Visible UI change | the screenshots in `docs/screenshots/` |
| Known problem and its fix | *Troubleshooting* |

## Code rules

- **Settings**: a new `ubonsole.conf` setting goes in three places: the default in
  `config/i3/scripts/common.sh`, the writer (with a comment) in `install.sh`, the README table.
  `install.sh` must keep the user's existing values on reinstall.
- **Scripts** source `~/.config/i3/scripts/common.sh` (settings, `aio`/`has_aio`, UI strings) and
  never hardcode paths, service names or devices that a setting already covers.
- **Colors**: files use the reference pink (`#E09AB4`, `#8A5A6E` and the shades listed in
  `tools/recolor.py`). Never add another hardcoded accent color: use those values (or `@accent` in
  rofi) so `recolor.py` can swap them, for named and custom `#RRGGBB` colors alike. Only the alert
  red `#E53935` and the fixed ANSI palette of `config/xresources/ubonsole.Xresources` are exempt;
  that palette must never reuse a reference shade, or it would be recolored too.
- **New themed file**: add it to the `recolor.py` calls in `install.sh`.
- **Icons**: FontAwesome 4.7 glyphs, written as `$'\uXXXX'` in scripts (raw glyphs only in
  `config/i3/config` and `i3blocks.conf`, which have no escape syntax).
- **Regions** drive more than the frequency sheet: a new region also needs its date format in
  `common.sh`. Anything shown to the user that depends on the country (units, date, time) must
  follow `UBONSOLE_REGION`, never a hardcoded French or US format.
- **Hardware**: optional hardware must degrade gracefully (no AIO v2 board, missing app → hidden or
  `(not installed)`, never an error).
- **Frequency data**: ranges must come from regulators, band plans or official project docs. Mark
  uncertain data as such or leave it out; the generator must report no layout error.

## Before committing

1. `bash -n` on every changed shell script; `python3 tools/gen-frequencies.py` if frequency data changed.
2. Test the installer in a throwaway home, never on the real config, and stub `sudo` so it cannot
   install packages:
   ```bash
   HOME=$(mktemp -d) bash -c 'sudo() { return 1; }; export -f sudo; ./install.sh --lang en --region us --color blue --yes'
   ```
   For a visual check on the uConsole, run the menus from that home (`HOME=... ~/.config/i3/scripts/sdr-menu`).
3. When testing on the device over SSH, stop processes with `pkill -x <name>`, never `pkill -f
   <pattern>` with a pattern that also appears in your own command line: it kills your shell before
   the cleanup steps run. Save and restore any shared state you touch (e.g. `xrdb -query` before,
   `xrdb -load` after).
4. Screenshots and committed files must not contain IP addresses, hostnames, e-mails, secrets or
   location data. Mask the Wi-Fi block (IP) in the bar before adding a screenshot.
5. Check the README against the table above.
