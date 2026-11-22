# My Custom Distro

A personal, gaming-focused Linux distribution built with [BlueBuild](https://blue-build.org/) on top of [Bazzite](https://bazzite.gg/).

> **Project status: foundation stage.** This image is experimental and is not ready to replace a daily-use operating system. We will build and test it in stages before recommending installation.

## Current foundation

- **Base:** Bazzite stable desktop image
- **Graphics:** NVIDIA-open driver image for Turing and newer GPUs (including GTX 16-series)
- **Desktop:** KDE Plasma, inherited from Bazzite
- **System utilities:** btop, fastfetch, git and micro
- **Custom artwork:** Afterburn wallpaper and original distribution icon
- **Custom application:** My Custom Distro Center launcher
- **Image builder:** BlueBuild
- **Build automation:** GitHub Actions

Bazzite provides the gaming-focused base. The goal of this project is to develop its own visual identity, desktop experience, settings tools and gaming-focused applications on top of that foundation.

## Build status

[![BlueBuild](https://github.com/oskaras424-sudo/my-custom-distro/actions/workflows/build.yml/badge.svg)](https://github.com/oskaras424-sudo/my-custom-distro/actions/workflows/build.yml)

Open the **Actions** tab to see build results. A green check means the image build completed; it does not mean the image has been fully tested on hardware.

## Image

The intended image reference is:

```text
ghcr.io/oskaras424-sudo/my-custom-distro:latest
```

Do not install or rebase to this image until a build has succeeded and the resulting image has been tested. Keep a known-good recovery option and back up important data before any operating-system installation.

## Roadmap

- [x] Create the BlueBuild repository and initial image recipe
- [x] Select the Bazzite NVIDIA-open foundation for GTX 16-series hardware
- [x] Add original wallpaper and icon artwork
- [x] Add the first KDE desktop control-center launcher
- [ ] Verify the first automated build and container signing
- [ ] Choose the final distribution name and visual identity
- [ ] Set a default desktop theme and wallpaper
- [ ] Develop a richer gaming and performance control centre
- [ ] Test the image in a virtual machine or spare installation
- [ ] Prepare installation media and release documentation

## Development

Edit `recipes/recipe.yml` to change the image build. The workflow in `.github/workflows/build.yml` runs automatically when relevant files are pushed and can also be started manually from the Actions tab.

The build workflow uses a GitHub Actions secret named `SIGNING_SECRET` for cosign signing. Do not put private signing keys in this repository or share them in chat. See the [BlueBuild signing guide](https://blue-build.org/how-to/cosign/) if repository signing still needs to be configured.

See the [BlueBuild recipe reference](https://blue-build.org/reference/recipe/) and [Bazzite documentation](https://docs.bazzite.gg/) before adding system packages or changing the base image.
