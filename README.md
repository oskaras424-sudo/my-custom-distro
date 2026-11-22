# My Custom Distro

A personal gaming-focused Linux distribution built with [BlueBuild](https://blue-build.org/) on top of the Bazzite KDE desktop image.

> **Project status: foundation stage.** This image is experimental and is not ready to replace a daily-use operating system. Test it before relying on it.

## Desktop foundation

- **Base:** Bazzite stable KDE Plasma desktop
- **Graphics:** Bazzite NVIDIA-open image for supported NVIDIA GPUs, including GTX 16-series
- **Browser:** Firefox (the only additional app installed by default)
- **Gaming:** Steam, provided by the Bazzite base
- **File manager:** Dolphin, provided by KDE
- **Terminal:** Konsole, provided by KDE
- **Desktop configuration:** KDE System Settings
- **Software centre:** Discover
- **System monitor:** KDE System Monitor
- **Task Manager:** custom Windows-inspired Qt/PySide6 application

## What is intentionally not preinstalled

This image does not add Thunderbird, LibreOffice, VLC, GIMP, Krita, OBS Studio, Blender, Kdenlive, Lutris, ProtonUp-Qt, Mission Center, Flatseal, Warehouse, KCalc or extra terminal utilities.

Flathub is available in Discover so users can choose optional apps themselves. The image avoids installing a large collection of applications that may not be needed.

## My Custom Distro Center

The control centre provides shortcuts to the essentials: Task Manager, Firefox, Steam, KDE System Settings, Discover, Konsole, Dolphin, KDE System Monitor, screenshots and the Afterburn colour scheme.

## Custom Task Manager

A Windows-inspired Qt/PySide6 application with process, performance, app history, startup, users, details and services pages.

Its settings include colour presets, a custom accent colour, compact/comfortable/spacious density, refresh speed, graph history, optional NVIDIA telemetry, visible process columns, always-on-top mode, optional local usage tracking, and settings import/export.

## Custom artwork

- Afterburn 2560×1440 wallpaper
- Original distribution icon
- Afterburn KDE Plasma colour scheme

## Performance and customisation approach

The image keeps Bazzite's upstream gaming and driver configuration intact. It avoids aggressive kernel, CPU or GPU tweaks that could reduce stability or interfere with game compatibility.

KDE Plasma provides the main desktop customisation tools. Firefox and the custom Task Manager are the only additional applications in the default app setup; core KDE apps and Steam come from the Bazzite base.

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
- [x] Keep the default application set deliberately minimal
- [ ] Verify the automated image build and container signing
- [ ] Make the Afterburn desktop theme and wallpaper first-login defaults
- [ ] Expand desktop, panel, launcher and window-effect customisation
- [ ] Test the image in a virtual machine or spare installation
- [ ] Prepare installation media and release documentation

## Development

Edit `recipes/recipe.yml` to change the image build. The workflow in `.github/workflows/build.yml` runs automatically when relevant files are pushed and can also be started manually from GitHub Actions.

The workflow expects a GitHub Actions secret named `SIGNING_SECRET` for cosign signing. Never put private signing keys in the repository or share them in chat. See the [BlueBuild signing guide](https://blue-build.org/how-to/cosign/).

See the [BlueBuild recipe reference](https://blue-build.org/reference/recipe/), [Bazzite documentation](https://docs.bazzite.gg/) and [KDE documentation](https://apps.kde.org/) before changing the base image or adding packages.
