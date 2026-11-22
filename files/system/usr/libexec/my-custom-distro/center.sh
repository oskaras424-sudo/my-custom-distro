#!/usr/bin/bash
set -u

APP_TITLE="My Custom Distro Center"

if ! command -v kdialog >/dev/null 2>&1; then
  printf '%s\n' "KDialog is required to open the desktop control center."
  exit 1
fi

show_error() {
  kdialog --title "$APP_TITLE" --sorry "$1"
}

while true; do
  choice="$(
    kdialog --title "$APP_TITLE" \
      --menu "Welcome to My Custom Distro. Choose a tool to open:" \
      steam "Launch Steam" \
      monitor "System monitor (btop)" \
      overview "System overview (fastfetch)" \
      settings "KDE system settings" \
      about "About this distribution" \
      quit "Close"
  )" || exit 0

  case "$choice" in
    steam)
      if command -v steam >/dev/null 2>&1; then
        nohup steam >/dev/null 2>&1 &
      else
        show_error "Steam was not found. Install or enable Steam from the Bazzite application tools."
      fi
      ;;
    monitor)
      if command -v btop >/dev/null 2>&1 && command -v konsole >/dev/null 2>&1; then
        konsole --hold -e btop >/dev/null 2>&1 &
      else
        show_error "The system monitor or Konsole terminal is not available."
      fi
      ;;
    overview)
      if command -v fastfetch >/dev/null 2>&1 && command -v konsole >/dev/null 2>&1; then
        konsole --hold -e fastfetch >/dev/null 2>&1 &
      else
        show_error "Fastfetch or Konsole terminal is not available."
      fi
      ;;
    settings)
      if command -v systemsettings >/dev/null 2>&1; then
        nohup systemsettings >/dev/null 2>&1 &
      else
        show_error "KDE System Settings was not found."
      fi
      ;;
    about)
      kdialog --title "$APP_TITLE" --msgbox \
        "My Custom Distro Gaming Edition\n\nBuilt on Bazzite with BlueBuild.\n\nProject stage: foundation and first desktop assets.\n\nThis is an experimental community image. Keep a recovery option and back up important files before installing it."
      ;;
    quit)
      exit 0
      ;;
  esac
done
