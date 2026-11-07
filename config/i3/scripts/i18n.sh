# Sourced by the uBonsole scripts: loads ~/.config/i3/ubonsole.conf and the UI strings.
# English is always loaded first, so a missing translation falls back to English.
UBONSOLE_DIR="$HOME/.config/i3"
[ -f "$UBONSOLE_DIR/ubonsole.conf" ] && . "$UBONSOLE_DIR/ubonsole.conf"
UBONSOLE_LANG=${UBONSOLE_LANG:-en}
AIOV2_CTL=${AIOV2_CTL:-$HOME/aiov2_ctl/aiov2_ctl.py}
. "$UBONSOLE_DIR/lang/en.sh"
if [ "$UBONSOLE_LANG" != en ] && [ -f "$UBONSOLE_DIR/lang/$UBONSOLE_LANG.sh" ]; then
  . "$UBONSOLE_DIR/lang/$UBONSOLE_LANG.sh"
fi
ROFI_THEME="$UBONSOLE_DIR/scripts/rofi-pink.rasi"
