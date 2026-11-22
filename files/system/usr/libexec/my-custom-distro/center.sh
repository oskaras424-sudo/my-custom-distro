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

pick() {
  kdialog --title "$APP_TITLE" --menu "$1" "${@:2}"
}

launch_command() {
  local command_name="$1"
  shift
  if command -v "$command_name" >/dev/null 2>&1; then
    nohup "$command_name" "$@" >/dev/null 2>&1 &
  else
    show_error "$command_name is not installed on this system."
  fi
}

launch_flatpak() {
  local app_id="$1"
  if command -v flatpak >/dev/null 2>&1 && flatpak info "$app_id" >/dev/null 2>&1; then
    nohup flatpak run "$app_id" >/dev/null 2>&1 &
  else
    show_error "$app_id is not installed yet. Connect to the internet and let the first-boot app setup finish, or install it through Discover."
  fi
}

while true; do
  choice="$(pick "Welcome to My Custom Distro. Select a category:" \
    taskmanager "Task Manager" \
    everyday "Everyday applications" \
    gaming "Gaming tools" \
    creative "Creative studio" \
    system "System tools" \
    customise "Customisation and app management" \
    theme "Apply Afterburn desktop colours" \
    about "About this distribution" \
    quit "Close")" || exit 0

  case "$choice" in
    taskmanager)
      launch_command /usr/bin/python3 /usr/libexec/my-custom-distro/task_manager.py
      ;;
    everyday)
      app="$(pick "Everyday applications" \
        browser "Firefox web browser" \
        mail "Thunderbird email" \
        office "LibreOffice suite" \
        media "VLC media player")" || continue
      case "$app" in
        browser) launch_flatpak org.mozilla.firefox ;;
        mail) launch_flatpak org.mozilla.thunderbird ;;
        office) launch_flatpak org.libreoffice.LibreOffice ;;
        media) launch_flatpak org.videolan.VLC ;;
      esac
      ;;
    gaming)
      app="$(pick "Gaming tools" \
        steam "Steam" \
        lutris "Lutris game manager" \
        proton "ProtonUp-Qt compatibility tools" \
        performance "Mission Center performance monitor")" || continue
      case "$app" in
        steam) launch_command steam ;;
        lutris) launch_flatpak net.lutris.Lutris ;;
        proton) launch_flatpak net.davidotek.pupgui2 ;;
        performance) launch_flatpak io.missioncenter.MissionCenter ;;
      esac
      ;;
    creative)
      app="$(pick "Creative applications" \
        obs "OBS Studio recording and streaming" \
        gimp "GIMP image editor" \
        krita "Krita digital painting" \
        kdenlive "Kdenlive video editor" \
        blender "Blender 3D creation")" || continue
      case "$app" in
        obs) launch_flatpak com.obsproject.Studio ;;
        gimp) launch_flatpak org.gimp.GIMP ;;
        krita) launch_flatpak org.kde.krita ;;
        kdenlive) launch_flatpak org.kde.kdenlive ;;
        blender) launch_flatpak org.blender.Blender ;;
      esac
      ;;
    system)
      app="$(pick "System tools" \
        settings "KDE System Settings" \
        software "Discover software centre" \
        terminal "Konsole terminal" \
        files "Dolphin file manager" \
        monitor "KDE System Monitor" \
        screenshot "Spectacle screenshot tool" \
        documents "Okular document viewer" \
        editor "Kate text editor" \
        overview "System overview (fastfetch)" \
        archive "Ark archive manager" \
        calculator "KCalc calculator")" || continue
      case "$app" in
        settings) launch_command systemsettings ;;
        software) launch_command plasma-discover ;;
        terminal) launch_command konsole ;;
        files) launch_command dolphin ;;
        monitor) launch_command plasma-systemmonitor ;;
        screenshot) launch_command spectacle ;;
        documents) launch_command okular ;;
        editor) launch_command kate ;;
        overview)
          if command -v konsole >/dev/null 2>&1 && command -v fastfetch >/dev/null 2>&1; then
            nohup konsole --hold -e fastfetch >/dev/null 2>&1 &
          else
            show_error "Konsole or fastfetch is not installed."
          fi
          ;;
        archive) launch_command ark ;;
        calculator) launch_command kcalc ;;
      esac
      ;;
    customise)
      app="$(pick "Customisation and app management" \
        settings "Desktop appearance and system settings" \
        flatseal "Flatseal application permissions" \
        warehouse "Warehouse Flatpak manager" \
        gtk "GTK application appearance settings" \
        discover "Browse more themes and applications")" || continue
      case "$app" in
        settings) launch_command systemsettings ;;
        flatseal) launch_flatpak com.github.tchx84.Flatseal ;;
        warehouse) launch_flatpak io.github.flattool.Warehouse ;;
        gtk) launch_command systemsettings kcm_gtk ;;
        discover) launch_command plasma-discover ;;
      esac
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
        "My Custom Distro Gaming Edition\n\nBuilt on Bazzite with BlueBuild.\n\nIncludes Firefox, KDE desktop tools, gaming utilities, creative apps and a custom Task Manager.\n\nThis is an experimental community image. Keep a recovery option and back up important files before installing it."
      ;;
    quit)
      exit 0
      ;;
  esac
done
