# My Custom Distro

A personal, gaming-focused Linux distribution built with [BlueBuild](https://blue-build.org/) on top of [Bazzite](https://bazzite.gg/).

> **Project status: foundation stage.** This image is experimental and is not ready to replace a daily-use operating system. We will build and test it in stages before recommending installation.

## Current foundation

- **Base:** Bazzite stable desktop image
- **Graphics:** NVIDIA-open driver image for Turing and newer GPUs (including GTX 16-series)
- **Desktop:** KDE Plasma, inherited from Bazzite
- **System utilities:** btop, fastfetch, git and micro
- **Task Manager:** custom Qt/PySide6 application with process, performance, usage history, startup, users, details and services pages
- **Task Manager customisation:** colour presets, custom accent, density, refresh speed, graph history, optional GPU telemetry, column visibility, always-on-top, local usage tracking, and settings import/export
- **Custom artwork:** Afterburn wallpaper, distribution icon and KDE colour scheme
- **Image builder:** BlueBuild
- **Build automation:** GitHub Actions

Bazzite provides the gaming-focused base. This project adds its own desktop tools, visual identity, settings and gaming-focused applications.

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
- [ ] Verify the automated image build and container signing
- [ ] Make the Afterburn desktop theme and wallpaper first-login defaults
- [ ] Create a richer gaming and performance control centre
- [ ] Add more desktop, panel, launcher and window-effect customisation
- [ ] Test the image in a virtual machine or spare installation
- [ ] Prepare installation media and release documentation

## Development

Edit `recipes/recipe.yml` to change the image build. The workflow in `.github/workflows/build.yml` runs automatically when relevant files are pushed and can also be started manually from GitHub Actions.

The workflow expects a GitHub Actions secret named `SIGNING_SECRET` for cosign signing. Never put private signing keys in the repository or share them in chat. See the [BlueBuild signing guide](https://blue-build.org/how-to/cosign/).

See the [BlueBuild recipe reference](https://blue-build.org/reference/recipe/) and [Bazzite documentation](https://docs.bazzite.gg/) before adding system packages or changing the base image.
