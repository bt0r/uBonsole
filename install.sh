#!/usr/bin/env bash
# uBonsole installer — i3 setup for the ClockworkPi uConsole
#
#   ./install.sh                       interactive
#   ./install.sh --lang fr --yes       non-interactive (French UI, default answers)
#
# Options:
#   --lang en|fr|de|es   interface language (bar menus + frequency cheat sheet)
#   --qt-theme           also apply the pink/black Qt6 theme (qt6ct)
#   --sdr-tools          also install the SDR tools (tools/install-sdr-tools.sh)
#   --yes                do not ask questions (keeps defaults for unset options)
set -euo pipefail

REPO=$(cd "$(dirname "$0")" && pwd)
I3_DIR="$HOME/.config/i3"
LANGS=(en fr de es)
LANG_NAMES=(English Français Deutsch Español)

UB_LANG="" QT_THEME="" SDR_TOOLS="" YES=0
while [ $# -gt 0 ]; do
  case $1 in
    --lang) UB_LANG=${2:-}; shift ;;
    --qt-theme) QT_THEME=1 ;;
    --sdr-tools) SDR_TOOLS=1 ;;
    --yes|-y) YES=1 ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
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

# --- Language ---------------------------------------------------------------
if [ -z "$UB_LANG" ]; then
  if [ "$YES" = 1 ]; then
    UB_LANG=en
  else
    echo "Interface language:"
    for i in "${!LANGS[@]}"; do echo "  $((i + 1))) ${LANG_NAMES[$i]} (${LANGS[$i]})"; done
    read -rp "Choice [1]: " n
    n=${n:-1}
    [[ $n =~ ^[1-4]$ ]] || { echo "Invalid choice" >&2; exit 1; }
    UB_LANG=${LANGS[$((n - 1))]}
  fi
fi
[[ " ${LANGS[*]} " == *" $UB_LANG "* ]] || { echo "Unsupported language: $UB_LANG (en, fr, de, es)" >&2; exit 1; }
say "Language: $UB_LANG"

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
  cp -a "$I3_DIR" "$BACKUP"
  say "Existing i3 config saved to $BACKUP"
fi

# --- Install files ------------------------------------------------------------
say "Installing i3 config to $I3_DIR"
mkdir -p "$I3_DIR"
cp -r "$REPO/config/i3/." "$I3_DIR/"
chmod +x "$I3_DIR"/scripts/*

AIOV2_CTL=""
for p in "$HOME/aiov2_ctl/aiov2_ctl.py" /usr/local/bin/aiov2_ctl; do
  [ -f "$p" ] && { AIOV2_CTL=$p; break; }
done
cat > "$I3_DIR/ubonsole.conf" <<EOF
# uBonsole settings (read by ~/.config/i3/scripts/i18n.sh)
# Interface language: en, fr, de, es
UBONSOLE_LANG=$UB_LANG
# HackerGadgets AIO v2 control tool (GPS / LoRa / SDR / USB rails); empty = not available
AIOV2_CTL=$AIOV2_CTL
EOF
[ -z "$AIOV2_CTL" ] && say "aiov2_ctl not found: GPS/LoRa/SDR/USB toggles are hidden in the power menu."

mkdir -p "$HOME/.config/direwolf"
cp "$REPO/config/direwolf/sdr.conf" "$HOME/.config/direwolf/sdr.conf"

# --- Qt6 theme (optional) -----------------------------------------------------
if [ -z "$QT_THEME" ] && ask "Apply the pink/black Qt6 theme (qt6ct, e.g. for GQRX)?" n; then QT_THEME=1; fi
if [ "$QT_THEME" = 1 ]; then
  QT=$HOME/.config/qt6ct
  mkdir -p "$QT/colors"
  cp "$REPO/config/qt6ct/colors/ubonsole-pink.conf" "$QT/colors/"
  [ -f "$QT/qt6ct.conf" ] && cp "$QT/qt6ct.conf" "$QT/qt6ct.conf.backup-$(date +%Y%m%d-%H%M%S)"
  python3 - "$QT/qt6ct.conf" <<'PY'
import configparser, sys
path = sys.argv[1]
c = configparser.RawConfigParser(); c.optionxform = str; c.read(path)
if not c.has_section("Appearance"): c.add_section("Appearance")
c.set("Appearance", "color_scheme_path", "~/.config/qt6ct/colors/ubonsole-pink.conf")
c.set("Appearance", "custom_palette", "true")
c.set("Appearance", "style", "Fusion")
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
say "Done. Change the language later in $I3_DIR/ubonsole.conf"
