#!/usr/bin/env bash
# Install SafeCode SessionGuard for the current user (no root needed).
#   ./install.sh               install or upgrade
#   ./install.sh --uninstall   remove (settings are kept)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
APP_DIR="$HOME/.local/opt/SafeCodeSessionGuard"
BIN="$HOME/.local/bin/safecode-sessionguard"
DESKTOP="$DATA/applications/safecode-sessionguard.desktop"
ICON="$DATA/icons/hicolor/256x256/apps/safecode-sessionguard.png"

stop_running() {
  pkill -f "$APP_DIR/SafeCodeSessionGuard" 2>/dev/null || true
}

if [ "${1:-}" = "--uninstall" ]; then
  stop_running
  rm -rf "$APP_DIR"
  rm -f "$BIN" "$DESKTOP" "$ICON" "$CONFIG/autostart/safecode-sessionguard.desktop"
  echo "SafeCode SessionGuard uninstalled. Settings kept in $CONFIG/SafeCodeSessionGuard"
  exit 0
fi

if [ ! -x "$HERE/SafeCodeSessionGuard" ]; then
  echo "Run install.sh from the extracted SafeCodeSessionGuard folder." >&2
  exit 1
fi
if [ "$HERE" = "$APP_DIR" ]; then
  echo "Already installed here; run install.sh from a freshly extracted download to upgrade." >&2
  exit 1
fi

stop_running
rm -rf "$APP_DIR"
mkdir -p "$(dirname "$APP_DIR")" "$(dirname "$BIN")" "$(dirname "$DESKTOP")" "$(dirname "$ICON")"
cp -R "$HERE" "$APP_DIR"
ln -sf "$APP_DIR/SafeCodeSessionGuard" "$BIN"
cp "$HERE/safecode-sessionguard.png" "$ICON"
cat > "$DESKTOP" <<DESKTOP_ENTRY
[Desktop Entry]
Type=Application
Name=SafeCode SessionGuard
Comment=Keep your computer awake and your session active
Exec="$APP_DIR/SafeCodeSessionGuard"
Icon=safecode-sessionguard
Categories=Utility;
Terminal=false
DESKTOP_ENTRY
command -v update-desktop-database >/dev/null && update-desktop-database -q "$DATA/applications" || true

echo "SafeCode SessionGuard installed to $APP_DIR"
echo "Start it from your app menu, or run: safecode-sessionguard"
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "Note: add ~/.local/bin to your PATH to use the safecode-sessionguard command." ;;
esac
