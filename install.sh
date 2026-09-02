#!/usr/bin/env bash
# Turbine — install the Zed theme family and keep it updated.
#
#   curl -fsSL https://raw.githubusercontent.com/chrisnicholson30/turbine-theme/main/install.sh | bash
#
# What it does
#   install    (default) download themes/turbine.json into Zed's user themes
#              folder, then register a daily updater (launchd on macOS,
#              a systemd user timer on Linux, cron as a fallback).
#   update     fetch the latest theme; replace it only if it changed.
#   status     show what is installed and when it last updated.
#   uninstall  remove the theme, the updater and its schedule.
#
# Options
#   --no-auto        install the theme without the daily updater
#   --ref <ref>      git branch or tag to fetch from (default: main, or $TURBINE_REF)
#   --variant <v>    print the settings.json snippet for hypersonic | supersonic | subsonic
#   -h, --help       this text
#
# Nothing here edits settings.json: Zed's settings allow comments, so the
# safest way to select a variant is the theme selector in Zed, or the
# snippet this script prints.
set -euo pipefail

REPO="chrisnicholson30/turbine-theme"
REF="${TURBINE_REF:-main}"
THEME_FILE="turbine.json"
LABEL="co.cn-design.turbine-theme"

CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
THEMES_DIR="$CONFIG_HOME/zed/themes"
APP_DIR="$DATA_HOME/turbine-theme"
STATE_DIR="$STATE_HOME/turbine-theme"
SCRIPT_PATH="$APP_DIR/turbine.sh"
LOG_FILE="$STATE_DIR/update.log"

ACTION="install"
AUTO=1
VARIANT=""

# ---------------------------------------------------------------- helpers
say()  { printf '\033[1;36m▸\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

raw_url() { printf 'https://raw.githubusercontent.com/%s/%s/%s' "$REPO" "$REF" "$1"; }

fetch() {  # fetch <url> <dest>
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 --retry-delay 2 -o "$2" "$1"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$2" "$1"
  else
    die "need curl or wget to download the theme"
  fi
}

checksum() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -c1-12
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | cut -c1-12
  else cksum "$1" | cut -d' ' -f1; fi
}

valid_theme() {  # a real Turbine theme file, not an HTML error page
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$1" <<'PY' 2>/dev/null
import json, sys
d = json.load(open(sys.argv[1]))
names = {t["name"] for t in d["themes"]}
sys.exit(0 if d.get("name") == "Turbine" and "Turbine Hypersonic" in names else 1)
PY
  else
    grep -q '"Turbine Hypersonic"' "$1" && head -c 1 "$1" | grep -q '{'
  fi
}

# ---------------------------------------------------------------- theme
install_theme() {  # returns 0 when the file changed, 2 when already current
  mkdir -p "$THEMES_DIR" "$STATE_DIR"
  local tmp; tmp="$(mktemp "${TMPDIR:-/tmp}/turbine.XXXXXX")"
  trap 'rm -f "$tmp"' RETURN
  fetch "$(raw_url "themes/$THEME_FILE")" "$tmp" || die "could not download themes/$THEME_FILE from $REPO@$REF"
  valid_theme "$tmp" || die "downloaded file is not a Turbine theme (ref '$REF' wrong?)"
  local dest="$THEMES_DIR/$THEME_FILE"
  if [ -f "$dest" ] && cmp -s "$tmp" "$dest"; then
    date -u +"%Y-%m-%dT%H:%M:%SZ checked $(checksum "$dest") unchanged" >> "$LOG_FILE"
    return 2
  fi
  mv -f "$tmp" "$dest"
  chmod 0644 "$dest"
  date -u +"%Y-%m-%dT%H:%M:%SZ installed $(checksum "$dest") from $REF" >> "$LOG_FILE"
  return 0
}

# ---------------------------------------------------------------- updater
store_script() {  # keep a local copy so the schedule never pipes remote code
  mkdir -p "$APP_DIR"
  if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    cp -f "${BASH_SOURCE[0]}" "$SCRIPT_PATH"
  else
    fetch "$(raw_url install.sh)" "$SCRIPT_PATH" || die "could not download install.sh for the updater"
  fi
  chmod 0755 "$SCRIPT_PATH"
  printf 'TURBINE_REF=%s\n' "$REF" > "$APP_DIR/env"
}

schedule() {
  local cmd="TURBINE_REF=$REF $SCRIPT_PATH update"
  if [ "$(uname -s)" = "Darwin" ]; then
    local plist="$HOME/Library/LaunchAgents/$LABEL.plist"
    mkdir -p "$HOME/Library/LaunchAgents"
    cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$SCRIPT_PATH</string><string>update</string></array>
  <key>EnvironmentVariables</key><dict><key>TURBINE_REF</key><string>$REF</string><key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string></dict>
  <key>StartInterval</key><integer>86400</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$LOG_FILE</string>
  <key>StandardErrorPath</key><string>$LOG_FILE</string>
</dict></plist>
EOF
    launchctl unload "$plist" >/dev/null 2>&1 || true
    launchctl load -w "$plist" >/dev/null 2>&1 || warn "launchctl could not load the agent; it will load at next login"
    ok "daily updater registered with launchd ($plist)"
  elif command -v systemctl >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1; then
    local unit_dir="$CONFIG_HOME/systemd/user"
    mkdir -p "$unit_dir"
    cat > "$unit_dir/turbine-theme.service" <<EOF
[Unit]
Description=Update the Turbine theme for Zed

[Service]
Type=oneshot
Environment=TURBINE_REF=$REF
ExecStart=/bin/bash $SCRIPT_PATH update
EOF
    cat > "$unit_dir/turbine-theme.timer" <<EOF
[Unit]
Description=Daily Turbine theme update

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now turbine-theme.timer >/dev/null
    ok "daily updater registered as a systemd user timer (turbine-theme.timer)"
  elif command -v crontab >/dev/null 2>&1; then
    local line="17 9 * * * $cmd >> $LOG_FILE 2>&1 # turbine-theme"
    ( crontab -l 2>/dev/null | grep -v '# turbine-theme' ; printf '%s\n' "$line" ) | crontab -
    ok "daily updater registered with cron (09:17 local time)"
  else
    warn "no launchd, systemd or cron found; run '$SCRIPT_PATH update' yourself to update"
  fi
}

unschedule() {
  if [ "$(uname -s)" = "Darwin" ]; then
    local plist="$HOME/Library/LaunchAgents/$LABEL.plist"
    [ -f "$plist" ] && { launchctl unload "$plist" >/dev/null 2>&1 || true; rm -f "$plist"; ok "launchd agent removed"; }
  fi
  if command -v systemctl >/dev/null 2>&1; then
    local unit_dir="$CONFIG_HOME/systemd/user"
    if [ -f "$unit_dir/turbine-theme.timer" ]; then
      systemctl --user disable --now turbine-theme.timer >/dev/null 2>&1 || true
      rm -f "$unit_dir/turbine-theme.timer" "$unit_dir/turbine-theme.service"
      systemctl --user daemon-reload >/dev/null 2>&1 || true
      ok "systemd timer removed"
    fi
  fi
  if command -v crontab >/dev/null 2>&1 && crontab -l 2>/dev/null | grep -q '# turbine-theme'; then
    crontab -l 2>/dev/null | grep -v '# turbine-theme' | crontab - || true
    ok "cron entry removed"
  fi
}

# ---------------------------------------------------------------- output
snippet() {
  local dark="Turbine Supersonic"
  case "$VARIANT" in
    hypersonic) dark="Turbine Hypersonic" ;;
    supersonic|"") dark="Turbine Supersonic" ;;
    subsonic) dark="Turbine Subsonic" ;;
    *) die "unknown variant '$VARIANT' (hypersonic | supersonic | subsonic)" ;;
  esac
  cat <<EOF

  To follow the OS, add this to Zed's settings.json (zed: open settings):

    "theme": {
      "mode": "system",
      "light": "Turbine Subsonic",
      "dark": "$dark"
    }

  Or run "theme selector" in Zed and pick a Turbine variant.
EOF
}

status() {
  local dest="$THEMES_DIR/$THEME_FILE"
  if [ -f "$dest" ]; then ok "theme installed: $dest ($(checksum "$dest"))"; else warn "theme not installed ($dest missing)"; fi
  if [ -f "$SCRIPT_PATH" ]; then ok "updater stored: $SCRIPT_PATH (ref $(cut -d= -f2 "$APP_DIR/env" 2>/dev/null || echo "$REF"))"; else warn "updater not stored"; fi
  if [ "$(uname -s)" = "Darwin" ] && [ -f "$HOME/Library/LaunchAgents/$LABEL.plist" ]; then ok "schedule: launchd, every 24h"
  elif command -v systemctl >/dev/null 2>&1 && systemctl --user is-enabled turbine-theme.timer >/dev/null 2>&1; then ok "schedule: systemd user timer, daily"
  elif command -v crontab >/dev/null 2>&1 && crontab -l 2>/dev/null | grep -q '# turbine-theme'; then ok "schedule: cron, daily 09:17"
  else warn "no daily schedule registered"; fi
  [ -f "$LOG_FILE" ] && { say "last activity:"; tail -n 3 "$LOG_FILE" | sed 's/^/    /'; }
}

usage() { sed -n '2,24p' "${BASH_SOURCE[0]:-/dev/null}" 2>/dev/null | sed 's/^# \{0,1\}//'; }

# ---------------------------------------------------------------- main
while [ $# -gt 0 ]; do
  case "$1" in
    install|update|status|uninstall) ACTION="$1" ;;
    --no-auto) AUTO=0 ;;
    --ref) shift; REF="${1:-}"; [ -n "$REF" ] || die "--ref needs a value" ;;
    --variant) shift; VARIANT="${1:-}" ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument '$1' (try --help)" ;;
  esac
  shift
done

case "$ACTION" in
  install)
    say "installing Turbine from $REPO@$REF into $THEMES_DIR"
    if install_theme; then ok "theme installed: $THEMES_DIR/$THEME_FILE"; else ok "theme already current"; fi
    if [ "$AUTO" -eq 1 ]; then store_script; schedule; else say "skipping the daily updater (--no-auto); rerun this script with 'update' to update"; fi
    snippet
    say "Zed picks up new files in $THEMES_DIR without a restart. Remove everything with: $SCRIPT_PATH uninstall"
    ;;
  update)
    mkdir -p "$STATE_DIR"
    if [ -f "$APP_DIR/env" ] && [ -z "${TURBINE_REF:-}" ]; then REF="$(cut -d= -f2 "$APP_DIR/env")"; fi
    if install_theme; then ok "theme updated from $REF"; else ok "theme already current"; fi
    ;;
  status) status ;;
  uninstall)
    unschedule
    rm -f "$THEMES_DIR/$THEME_FILE" && ok "theme removed from $THEMES_DIR"
    rm -rf "$APP_DIR" "$STATE_DIR"
    ok "Turbine uninstalled. Pick another theme in Zed with 'theme selector'."
    ;;
esac
