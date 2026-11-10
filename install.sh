#!/usr/bin/env bash
# uBonsole installer — i3 setup for the ClockworkPi uConsole
#
#   ./install.sh                       interactive
#   ./install.sh --lang fr --region fr --yes    non-interactive (French UI, France frequencies)
#
# Options:
#   --lang en|fr|de|es   interface language (bar menus + frequency cheat sheet)
#   --region CODE        frequency cheat sheet region: fr uk de es us ca eu (eu = other Europe)
#   --color NAME|#HEX    accent color: pink (default) blue red green yellow white, or a custom #RRGGBB
#   --terminal-colors    use the accent in the terminal (st reads X resources); --no-terminal-colors to skip
#   --qt-theme           also apply the dark Qt6 theme in the accent color (qt6ct)
#   --sdr-tools          also install the SDR tools (tools/install-sdr-tools.sh)
#   --yes                do not ask questions (keeps defaults for unset options)
set -euo pipefail

REPO=$(cd "$(dirname "$0")" && pwd)
I3_DIR="$HOME/.config/i3"
LANGS=(en fr de es)
LANG_NAMES=(English Français Deutsch Español)
REGIONS=(fr uk de es us ca eu)
REGION_NAMES=(France "United Kingdom" Germany Spain USA Canada "Other Europe (generic ITU Region 1)")
COLORS=(pink blue red green yellow white)

UB_LANG="" UB_REGION="" UB_COLOR="" TERM_COLORS="" QT_THEME="" SDR_TOOLS="" YES=0
while [ $# -gt 0 ]; do
  case $1 in
    --lang) UB_LANG=${2:-}; shift ;;
    --region) UB_REGION=${2:-}; shift ;;
    --color) UB_COLOR=${2:-}; shift ;;
    --terminal-colors) TERM_COLORS=yes ;;
    --no-terminal-colors) TERM_COLORS=no ;;
    --qt-theme) QT_THEME=1 ;;
    --sdr-tools) SDR_TOOLS=1 ;;
    --yes|-y) YES=1 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

say() { printf '\033[1;35m==>\033[0m %s\n' "$*"; }
ask() {  # ask "question" default(y/n) -> returns 0 for yes
  local def=$2 ans
  [ "$YES" = 1 ] && [ "$def" = y ] && return 0
  [ "$YES" = 1 ] && return 1
  read -rp "$1 [$([ "$def" = y ] && echo Y/n || echo y/N)] " ans
  ans=${ans:-$def}
  [[ $ans =~ ^[yYoO] ]]
}

# --- Existing settings ------------------------------------------------------
# A reinstall keeps the current ubonsole.conf values; flags and answers override them
CONF="$I3_DIR/ubonsole.conf"
declare -A OLD=()
if [ -f "$CONF" ]; then
  while IFS='=' read -r k v; do OLD[$k]=$v; done < <(grep -E '^[A-Z0-9_]+=' "$CONF")
  say "Keeping the settings from $CONF"
fi
old() { echo "${OLD[$1]:-}"; }

# --- Language ---------------------------------------------------------------
if [ -z "$UB_LANG" ]; then
  DEF=$(old UBONSOLE_LANG); DEF=${DEF:-en}
  if [ "$YES" = 1 ]; then
    UB_LANG=$DEF
  else
    echo "Interface language:"
    DEFN=1
    for i in "${!LANGS[@]}"; do
      echo "  $((i + 1))) ${LANG_NAMES[$i]} (${LANGS[$i]})"
      [ "${LANGS[$i]}" = "$DEF" ] && DEFN=$((i + 1))
    done
    read -rp "Choice [$DEFN]: " n
    n=${n:-$DEFN}
    [[ $n =~ ^[1-4]$ ]] || { echo "Invalid choice" >&2; exit 1; }
    UB_LANG=${LANGS[$((n - 1))]}
  fi
fi
[[ " ${LANGS[*]} " == *" $UB_LANG "* ]] || { echo "Unsupported language: $UB_LANG (en, fr, de, es)" >&2; exit 1; }
say "Language: $UB_LANG"

# --- Region (frequency cheat sheet) -------------------------------------------
# Band plans and rules differ by country: pick where the device is used
if [ -z "$UB_REGION" ]; then
  DEF=$(old UBONSOLE_REGION)
  [ -z "$DEF" ] && case $UB_LANG in fr|de|es) DEF=$UB_LANG ;; *) DEF=eu ;; esac
  if [ "$YES" = 1 ]; then
    UB_REGION=$DEF
  else
    echo "Region for the SDR frequency cheat sheet:"
    DEFN=7
    for i in "${!REGIONS[@]}"; do
      echo "  $((i + 1))) ${REGION_NAMES[$i]} (${REGIONS[$i]})"
      [ "${REGIONS[$i]}" = "$DEF" ] && DEFN=$((i + 1))
    done
    read -rp "Choice [$DEFN]: " n
    n=${n:-$DEFN}
    [[ $n =~ ^[1-7]$ ]] || { echo "Invalid choice" >&2; exit 1; }
    UB_REGION=${REGIONS[$((n - 1))]}
  fi
fi
[[ " ${REGIONS[*]} " == *" $UB_REGION "* ]] || { echo "Unsupported region: $UB_REGION (${REGIONS[*]})" >&2; exit 1; }
say "Region: $UB_REGION"

# --- Accent color -------------------------------------------------------------
if [ -z "$UB_COLOR" ]; then
  DEF=$(old UBONSOLE_COLOR); DEF=${DEF:-pink}
  if [ "$YES" = 1 ]; then
    UB_COLOR=$DEF
  else
    echo "Accent color (shown on black):"
    DEFN=7
    for i in "${!COLORS[@]}"; do
      echo "  $((i + 1))) ${COLORS[$i]}"
      [ "${COLORS[$i]}" = "$DEF" ] && DEFN=$((i + 1))
    done
    echo "  7) custom (#RRGGBB)$([ "$DEFN" = 7 ] && echo ": $DEF")"
    read -rp "Choice [$DEFN]: " n
    n=${n:-$DEFN}
    [[ $n =~ ^[1-7]$ ]] || { echo "Invalid choice" >&2; exit 1; }
    if [ "$n" = 7 ]; then
      read -rp "Color as #RRGGBB (pastel tones read best) [$DEF]: " UB_COLOR
      UB_COLOR=${UB_COLOR:-$DEF}
    else
      UB_COLOR=${COLORS[$((n - 1))]}
    fi
  fi
fi
# Pastel name or custom #RRGGBB; custom colors are checked for contrast on the black background
if [[ " ${COLORS[*]} " != *" $UB_COLOR "* ]]; then
  CHECK=$(python3 "$REPO/tools/recolor.py" --check "$UB_COLOR") \
    || { echo "Unsupported color: $UB_COLOR (${COLORS[*]} or #RRGGBB)" >&2; exit 1; }
  read -r UB_COLOR RATIO VERDICT <<< "$CHECK"
  if [ "$VERDICT" = low ]; then
    say "Warning: $UB_COLOR has a low contrast on black ($RATIO:1, 7:1 recommended), text may be hard to read."
    ask "Use it anyway?" n || { echo "Pick a lighter color." >&2; exit 1; }
  fi
fi
say "Accent color: $UB_COLOR"

# --- Terminal colors ----------------------------------------------------------
# st reads its colors from X resources: optionally load accent-colored ones over ~/.Xresources.
# Off unless the user accepts, since it overrides their own terminal colors.
if [ -z "$TERM_COLORS" ]; then
  DEF=$(old UBONSOLE_TERMINAL_COLORS); DEF=${DEF:-no}
  echo "The terminal (st) can use the same theme: black background, text and cursor in the accent"
  echo "color, pastel ANSI colors. It is loaded over ~/.Xresources and overrides its colors."
  if ask "Apply the same theme to the terminal?" "${DEF:0:1}"; then
    TERM_COLORS=yes
  else
    TERM_COLORS=no
  fi
fi
say "Terminal colors: $TERM_COLORS"

# --- Dependencies -------------------------------------------------------------
# command -> Debian package
declare -A DEPS=(
  [i3]=i3 [i3blocks]=i3blocks [rofi]=rofi [feh]=feh [maim]=maim [xdotool]=xdotool [xclip]=xclip
  [brightnessctl]=brightnessctl [wpctl]=wireplumber [nmcli]=network-manager [xrandr]=x11-xserver-utils
  [xrdb]=x11-xserver-utils [i3-nagbar]=i3-wm [python3]=python3 [firefox]=firefox-esr
)
MISSING=()
for cmd in "${!DEPS[@]}"; do command -v "$cmd" >/dev/null 2>&1 || MISSING+=("${DEPS[$cmd]}"); done
[ -x /usr/sbin/rfkill ] || MISSING+=(rfkill)
# Read the font list once: "fc-list | grep -q" fails under pipefail when grep exits early
FONTS=$(fc-list : family 2>/dev/null || true)
grep -qi fontawesome <<< "$FONTS" || MISSING+=(fonts-font-awesome)
grep -qi "DejaVu Sans Mono" <<< "$FONTS" || MISSING+=(fonts-dejavu-core)
if [ ${#MISSING[@]} -gt 0 ]; then
  mapfile -t MISSING < <(printf '%s\n' "${MISSING[@]}" | sort -u)
  say "Missing packages: ${MISSING[*]}"
  if ask "Install them with apt (sudo)?" y; then
    sudo apt-get update && sudo apt-get install -y "${MISSING[@]}"
  else
    echo "    Continuing without them; some blocks or menus will not work."
  fi
fi
command -v st >/dev/null 2>&1 || say "Note: the 'st' terminal is not installed (used by \$mod+Return and the radio decoders)."

# --- Backup -------------------------------------------------------------------
if [ -d "$I3_DIR" ]; then
  BACKUP="$I3_DIR.backup-$(date +%Y%m%d-%H%M%S)"
  # Two runs in the same second would otherwise copy into the previous backup
  n=1; while [ -e "$BACKUP" ]; do BACKUP="$I3_DIR.backup-$(date +%Y%m%d-%H%M%S)-$n"; n=$((n + 1)); done
  cp -a "$I3_DIR" "$BACKUP"
  say "Existing i3 config saved to $BACKUP"
fi

# --- Install files ------------------------------------------------------------
say "Installing i3 config to $I3_DIR"
mkdir -p "$I3_DIR"
cp -r "$REPO/config/i3/." "$I3_DIR/"
chmod +x "$I3_DIR"/scripts/*
# The copies hold the reference pink: swap it for the chosen accent
python3 "$REPO/tools/recolor.py" "$UB_COLOR" "$I3_DIR/config" "$I3_DIR/i3blocks.conf" "$I3_DIR/scripts/rofi-theme.rasi"
if [ "$TERM_COLORS" = yes ]; then
  cp "$REPO/config/xresources/ubonsole.Xresources" "$I3_DIR/Xresources"
  python3 "$REPO/tools/recolor.py" "$UB_COLOR" "$I3_DIR/Xresources"
else
  rm -f "$I3_DIR/Xresources"
fi

# --- Settings (ubonsole.conf) ---------------------------------------------------
# Detected values are only used when the setting is not already set
AIOV2_CTL=$(old AIOV2_CTL)
if [ -z "$AIOV2_CTL" ]; then
  if command -v aiov2_ctl >/dev/null 2>&1; then AIOV2_CTL=aiov2_ctl
  elif [ -f "$HOME/aiov2_ctl/aiov2_ctl.py" ]; then AIOV2_CTL=$HOME/aiov2_ctl/aiov2_ctl.py; fi
fi
ADSB_SERVICE=$(old ADSB_SERVICE)
if [ -z "$ADSB_SERVICE" ]; then
  ADSB_SERVICE=readsb
  for s in readsb dump1090-fa dump1090-mutability dump1090; do
    systemctl cat "$s.service" >/dev/null 2>&1 && { ADSB_SERVICE=$s; break; }
  done
fi
AUTORX_DIR=$(old AUTORX_DIR)
if [ -z "$AUTORX_DIR" ]; then
  AUTORX_DIR=$HOME/src/radiosonde_auto_rx/auto_rx
  for d in "$HOME/src/radiosonde_auto_rx/auto_rx" "$HOME/radiosonde_auto_rx/auto_rx"; do
    [ -f "$d/auto_rx.py" ] && { AUTORX_DIR=$d; break; }
  done
fi
BATTERY=$(old BATTERY)
if [ -z "$BATTERY" ]; then
  BATTERY=/sys/class/power_supply/axp20x-battery
  for b in /sys/class/power_supply/*; do
    [ "$(cat "$b/type" 2>/dev/null)" = Battery ] && { BATTERY=$b; break; }
  done
fi
WIFI_IFACE=$(old WIFI_IFACE)
if [ -z "$WIFI_IFACE" ]; then
  WIFI_IFACE=wlan0
  for d in /sys/class/net/*; do
    [ -d "$d/wireless" ] && { WIFI_IFACE=$(basename "$d"); break; }
  done
fi
SDR_DEVICE=$(old SDR_DEVICE); SDR_GAIN=$(old SDR_GAIN); TAR1090_URL=$(old TAR1090_URL)
# Kept as written (quotes included), empty = follow the region
DATE_FORMAT=$(old DATE_FORMAT)

cat > "$CONF" <<EOF
# uBonsole settings, read by ~/.config/i3/scripts/common.sh on every click.
# install.sh keeps these values when you reinstall or update.

# Interface language: en, fr, de, es
UBONSOLE_LANG=$UB_LANG
# Frequency cheat sheet region: fr, uk, de, es, us, ca, eu (other Europe)
UBONSOLE_REGION=$UB_REGION
# Date and time in the bar, date(1) syntax, e.g. '%Y-%m-%d %H:%M'. Empty = usual format of the region:
# fr/uk/es 31/12/2026 23:59, de 31.12.2026 23:59, us 12/31/2026 11:59 PM, ca/eu 2026-12-31 23:59
DATE_FORMAT=${DATE_FORMAT:-''}
# Accent color: pink, blue, red, green, yellow, white or a custom #RRGGBB. Applied by install.sh,
# so change it with "./install.sh --color <name|#RRGGBB>" rather than here.
UBONSOLE_COLOR=$UB_COLOR
# Terminal (st) uses the same theme through X resources: yes / no (default). Applied by install.sh.
UBONSOLE_TERMINAL_COLORS=$TERM_COLORS

# HackerGadgets AIO v2 control tool (GPS / LoRa / SDR / USB rails): the "aiov2_ctl" command or the
# path to aiov2_ctl.py. Empty = no AIO v2 board (those toggles are hidden).
AIOV2_CTL=$AIOV2_CTL

# RTL-SDR used by the text decoders (ACARS, VDL2, APRS, rtl_433): device index (rtl_test lists them)
# and tuner gain in dB. GQRX, SDR++, SatDump and auto_rx pick their device in their own settings.
SDR_DEVICE=${SDR_DEVICE:-0}
SDR_GAIN=${SDR_GAIN:-40}

# ADS-B: systemd service of the decoder (readsb, dump1090-fa...) and the tar1090 page
ADSB_SERVICE=$ADSB_SERVICE
TAR1090_URL=${TAR1090_URL:-http://localhost/tar1090}

# radiosonde_auto_rx folder (the one containing auto_rx.py)
AUTORX_DIR=$AUTORX_DIR

# Battery shown in the bar and the power menu
BATTERY=$BATTERY

# Wi-Fi interface shown in the bar (IP address)
WIFI_IFACE=$WIFI_IFACE
EOF

# --- What is available --------------------------------------------------------
has() { command -v "$1" >/dev/null 2>&1; }
FOUND=() ABSENT=()
for c in gqrx sdrpp satdump-ui acarsdec dumpvdl2 rtl_airband AIS-catcher welle-io rtl_power gpredict direwolf wsjtx js8call \
         qsstv fldigi rtl_fm rtl_433 meshcore-console gpspipe; do
  if has "$c"; then FOUND+=("$c"); else ABSENT+=("$c"); fi
done
systemctl cat "$ADSB_SERVICE.service" >/dev/null 2>&1 && FOUND+=("$ADSB_SERVICE (ADS-B)") || ABSENT+=("$ADSB_SERVICE (ADS-B)")
[ -f "$AUTORX_DIR/auto_rx.py" ] && FOUND+=(auto_rx) || ABSENT+=(auto_rx)
{ docker image inspect ghcr.io/sdr-enthusiasts/docker-acarshub:latest || sudo -n docker image inspect ghcr.io/sdr-enthusiasts/docker-acarshub:latest; } \
  >/dev/null 2>&1 && FOUND+=("ACARS Hub") || ABSENT+=("ACARS Hub")
say "Radio apps found: ${FOUND[*]:-none}"
[ ${#ABSENT[@]} -gt 0 ] && echo "    Not found (shown as not installed in the menu): ${ABSENT[*]}"
if [ -n "$AIOV2_CTL" ]; then
  say "AIO v2 control: $AIOV2_CTL"
else
  say "aiov2_ctl not found: GPS/LoRa/SDR/USB toggles are hidden (https://github.com/hackergadgets/aiov2_ctl)"
fi

mkdir -p "$HOME/.config/direwolf"
cp "$REPO/config/direwolf/sdr.conf" "$HOME/.config/direwolf/sdr.conf"

# --- Qt6 theme (optional) -----------------------------------------------------
QT=$HOME/.config/qt6ct
if [ -z "$QT_THEME" ] && [ ! -f "$QT/colors/ubonsole.conf" ] \
   && ask "Apply the dark Qt6 theme in the accent color (qt6ct, e.g. for GQRX)?" n; then QT_THEME=1; fi
# Already applied once: refresh the palette so it follows the accent color
[ -f "$QT/colors/ubonsole.conf" ] && QT_THEME=1
if [ "$QT_THEME" = 1 ]; then
  mkdir -p "$QT/colors"
  cp "$REPO/config/qt6ct/colors/ubonsole.conf" "$QT/colors/"
  python3 "$REPO/tools/recolor.py" "$UB_COLOR" "$QT/colors/ubonsole.conf"
  [ -f "$QT/qt6ct.conf" ] && cp "$QT/qt6ct.conf" "$QT/qt6ct.conf.backup-$(date +%Y%m%d-%H%M%S)"
  python3 - "$QT/qt6ct.conf" <<'PY'
import configparser, sys
path = sys.argv[1]
c = configparser.RawConfigParser(); c.optionxform = str; c.read(path)
if not c.has_section("Appearance"): c.add_section("Appearance")
c.set("Appearance", "color_scheme_path", "~/.config/qt6ct/colors/ubonsole.conf")
c.set("Appearance", "custom_palette", "true")
c.set("Appearance", "style", "Fusion")
# uConsole images set 20 pt Qt fonts; the old gtk2 style ignored them, Fusion applies them and GQRX
# overflows the 720 px screen. Cap the sizes at 10 pt.
if c.has_section("Fonts"):
    for key in ("general", "fixed"):
        if c.has_option("Fonts", key):
            parts = c.get("Fonts", key).strip('"').split(",")
            if len(parts) > 1 and parts[1].isdigit() and int(parts[1]) > 10:
                parts[1] = "10"
                c.set("Fonts", key, '"%s"' % ",".join(parts))
with open(path, "w") as f: c.write(f, space_around_delimiters=False)
PY
  say "Qt6 theme applied (restart Qt apps to see it)"
fi

# --- SDR tools (optional) -----------------------------------------------------
if [ -z "$SDR_TOOLS" ] && ask "Install the SDR tools (SDR++, SatDump, direwolf, acarsdec, dumpvdl2, auto_rx)? Takes a while." n; then SDR_TOOLS=1; fi
[ "$SDR_TOOLS" = 1 ] && bash "$REPO/tools/install-sdr-tools.sh"

# --- Reload -------------------------------------------------------------------
if pgrep -x i3 >/dev/null && command -v i3-msg >/dev/null; then
  i3-msg -q restart 2>/dev/null && say "i3 restarted"
fi
say "Done. Change the language or region in $CONF, the color with: ./install.sh --color <name|#RRGGBB>"
