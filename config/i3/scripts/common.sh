# Sourced by every uBonsole script: settings from ~/.config/i3/ubonsole.conf, helpers, UI strings.
# English strings load first, so a missing translation falls back to English.
UBONSOLE_DIR="$HOME/.config/i3"
[ -f "$UBONSOLE_DIR/ubonsole.conf" ] && . "$UBONSOLE_DIR/ubonsole.conf"

# Defaults for settings missing from ubonsole.conf (see that file for what each one does).
# AIOV2_CTL uses "-" so that an explicit empty value disables the AIO v2 features.
UBONSOLE_LANG=${UBONSOLE_LANG:-en}
UBONSOLE_REGION=${UBONSOLE_REGION:-eu}
AIOV2_CTL=${AIOV2_CTL-$HOME/aiov2_ctl/aiov2_ctl.py}
SDR_DEVICE=${SDR_DEVICE:-0}
SDR_GAIN=${SDR_GAIN:-40}
ADSB_SERVICE=${ADSB_SERVICE:-readsb}
TAR1090_URL=${TAR1090_URL:-http://localhost/tar1090}
AUTORX_DIR=${AUTORX_DIR:-$HOME/src/radiosonde_auto_rx/auto_rx}
BATTERY=${BATTERY:-/sys/class/power_supply/axp20x-battery}
WIFI_IFACE=${WIFI_IFACE:-wlan0}

# Date and time in the bar (date(1) syntax): the region's usual format unless DATE_FORMAT is set
if [ -z "${DATE_FORMAT:-}" ]; then
  case $UBONSOLE_REGION in
    us) DATE_FORMAT='%m/%d/%Y %I:%M %p' ;;
    de) DATE_FORMAT='%d.%m.%Y %H:%M' ;;
    ca|eu) DATE_FORMAT='%Y-%m-%d %H:%M' ;;
    *) DATE_FORMAT='%d/%m/%Y %H:%M' ;;
  esac
fi

. "$UBONSOLE_DIR/lang/en.sh"
if [ "$UBONSOLE_LANG" != en ] && [ -f "$UBONSOLE_DIR/lang/$UBONSOLE_LANG.sh" ]; then
  . "$UBONSOLE_DIR/lang/$UBONSOLE_LANG.sh"
fi
ROFI_THEME="$UBONSOLE_DIR/scripts/rofi-theme.rasi"

# HackerGadgets AIO v2 rails (GPS / LoRa / SDR / USB). AIOV2_CTL is either a command
# (installed with "aiov2_ctl --install") or the path to aiov2_ctl.py.
has_aio() {
  [ -n "$AIOV2_CTL" ] && { [ -f "$AIOV2_CTL" ] || command -v "$AIOV2_CTL" >/dev/null 2>&1; }
}
aio() {
  has_aio || return 1
  case $AIOV2_CTL in
    *.py) python3 "$AIOV2_CTL" "$@" ;;
    *) "$AIOV2_CTL" "$@" ;;
  esac
}
