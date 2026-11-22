# My Custom Distro

A personal, gaming-focused Linux distribution built with [BlueBuild](https://blue-build.org/) on top of [Bazzite](https://bazzite.gg/).

> **Project status: foundation stage.** This image is experimental and is not ready to replace a daily-use operating system. We will build and test it in stages before recommending installation.

## Desktop foundation

- **Base:** Bazzite stable KDE desktop image
- **Graphics:** Bazzite NVIDIA-open image for Turing GPUs, including GTX 16-series
- **Desktop settings:** KDE System Settings and Plasma's built-in desktop customisation
- **File manager:** Dolphin
- **Terminal:** Konsole
- **Software centre:** KDE Discover with Flatpak support
- **System tools:** KDE System Monitor, Spectacle, Ark, Okular, Kate and KCalc

## Pre-installed applications

BlueBuild installs these Flathub applications system-wide during first boot. An internet connection is needed for the initial Flatpak setup.

| Category | Applications |
|---|---|
| Browser and communication | Firefox, Thunderbird |
| Productivity | LibreOffice |
| Media | VLC |
| Gaming | Steam (from Bazzite), Lutris, ProtonUp-Qt |
| Streaming and capture | OBS Studio |
| Creative | GIMP, Krita, Kdenlive, Blender |
| Customisation | Flatseal, Warehouse |
| Performance | Custom Task Manager, KDE System Monitor, Mission Center |

The first-boot Flatpak service installs apps from Flathub and keeps them independently updated. Discover remains available for installing anything else.

## My Custom Distro Center

The custom control centre provides shortcuts to everyday apps, gaming tools, creative tools, KDE system utilities, the Afterburn theme and customisation tools.

## Custom Task Manager

A Windows-inspired Qt/PySide6 application with process, performance, app history, startup, users, details and services pages.

Its settings include colour presets, a custom accent colour, compact/comfortable/spacious density, refresh speed, graph history, optional NVIDIA telemetry, visible process columns, always-on-top mode, optional local usage tracking, and settings import/export.

## Custom artwork

- Afterburn 2560×1440 wallpaper
- Original distribution icon
- Afterburn KDE Plasma colour scheme

## Performance and customisation approach

The image keeps Bazzite's upstream gaming and driver configuration intact. It adds monitoring and system-control tools without applying aggressive kernel, CPU or GPU tweaks that could reduce stability or interfere with game compatibility.

KDE Plasma provides the desktop's main customisation surface. Flatseal gives users control over Flatpak permissions; Warehouse manages installed Flatpaks and rollbacks.

## Build status

[![BlueBuild](https://github.com/oskaras424-sudo/my-custom-distro/actions/workflows/build.yml/badge.svg)](https://github.com/oskaras424-sudo/my-custom-distro/actions/workflows/build.yml)

A successful image build is not the same as hardware testing. Check the **Actions** tab before attempting to install an image.

## Image

```text
ghcr.io/oskaras424-sudo/my-custom-distro:latest
```

Do not rebase or install this image until its build and signing have succeeded and it has been tested. Keep a known-good recovery option and back up important data before installing an operating system.

## Roadmap

- [x] Create the BlueBuild repository and initial image recipe
- [x] Select Bazzite NVIDIA-open foundation for GTX 16-series hardware
- [x] Add original Afterburn wallpaper, icon and KDE colour scheme
- [x] Add the My Custom Distro desktop control centre
- [x] Add the first Windows-style Task Manager and its settings
- [x] Add KDE desktop utilities and a first-boot application suite
- [ ] Verify the automated image build and container signing
- [ ] Make the Afterburn desktop theme and wallpaper first-login defaults
- [ ] Expand desktop, panel, launcher and window-effect customisation
- [ ] Test the image in a virtual machine or spare installation
- [ ] Prepare installation media and release documentation

## Development

Edit `recipes/recipe.yml` to change the image build. The workflow in `.github/workflows/build.yml` runs automatically when relevant files are pushed and can also be started manually from GitHub Actions.

The workflow expects a GitHub Actions secret named `SIGNING_SECRET` for cosign signing. Never put private signing keys in the repository or share them in chat. See the [BlueBuild signing guide](https://blue-build.org/how-to/cosign/).

See the [BlueBuild recipe reference](https://blue-build.org/reference/recipe/), the [Bazzite documentation](https://docs.bazzite.gg/) and [KDE applications](https://apps.kde.org/) before adding packages or changing the base image.
