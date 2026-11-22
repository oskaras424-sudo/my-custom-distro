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

launch_command() {
  local command_name="$1"
  shift
  if command -v "$command_name" >/dev/null 2>&1; then
    nohup "$command_name" "$@" >/dev/null 2>&1 &
  else
    show_error "$command_name is not available in this Bazzite KDE installation."
  fi
}

while true; do
  choice="$(
    kdialog --title "$APP_TITLE" \
      --menu "My Custom Distro — choose an essential app or system tool:" \
      taskmanager "Task Manager" \
      optionalapps "Choose optional applications" \
      browser "Firefox browser" \
      steam "Steam gaming" \
      settings "KDE System Settings" \
      software "Discover software centre" \
      terminal "Konsole terminal" \
      files "Dolphin file manager" \
      monitor "KDE System Monitor" \
      screenshot "Screenshot tool" \
      theme "Apply Afterburn colours" \
      about "About this distribution" \
      quit "Close"
  )" || exit 0

  case "$choice" in
    taskmanager)
      launch_command /usr/bin/python3 /usr/libexec/my-custom-distro/task_manager.py
      ;;
    optionalapps)
      launch_command /usr/bin/python3 /usr/libexec/my-custom-distro/app_setup.py --manage
      ;;
    browser)
      if command -v flatpak >/dev/null 2>&1 && flatpak info org.mozilla.firefox >/dev/null 2>&1; then
        nohup flatpak run org.mozilla.firefox >/dev/null 2>&1 &
      else
        show_error "Firefox is being installed by the first-boot application setup. Connect to the internet and try again shortly, or install Firefox through Discover."
      fi
      ;;
    steam)
      launch_command steam
      ;;
    settings)
      launch_command systemsettings
      ;;
    software)
      launch_command plasma-discover
      ;;
    terminal)
      launch_command konsole
      ;;
    files)
      launch_command dolphin
      ;;
    monitor)
      launch_command plasma-systemmonitor
      ;;
    screenshot)
      launch_command spectacle
      ;;
    theme)
      if command -v plasma-apply-colorscheme >/dev/null 2>&1; then
        plasma-apply-colorscheme Afterburn
        kdialog --title "$APP_TITLE" --msgbox "Afterburn colours have been applied. Choose the Afterburn wallpaper in System Settings > Wallpaper."
      else
        show_error "The KDE colour-scheme utility is not available."
      fi
      ;;
    about)
      kdialog --title "$APP_TITLE" --msgbox \
        "My Custom Distro Gaming Edition\n\nBuilt on Bazzite KDE with NVIDIA drivers.\n\nIncludes Firefox, Steam, KDE desktop tools and the custom Task Manager.\n\nThis is an experimental community image. Back up important files and test it before installing it as your main operating system."
      ;;
    quit)
      exit 0
      ;;
  esac
done
