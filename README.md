# My Custom Distro

A personal gaming-focused Linux distribution built with [BlueBuild](https://blue-build.org/) on top of the Bazzite KDE desktop image.

> **Project status: foundation stage.** This image is experimental and is not ready to replace a daily-use operating system. Test it before relying on it.

## What's included by default

- **Base:** Bazzite stable KDE Plasma desktop
- **Graphics:** Bazzite NVIDIA-open image for supported NVIDIA GPUs, including GTX 16-series
- **Gaming:** Steam from the Bazzite base
- **File manager:** Dolphin
- **Terminal:** Konsole
- **Desktop configuration:** KDE System Settings
- **Software centre:** Discover
- **System monitor:** KDE System Monitor
- **Screenshot tool:** Spectacle
- **Task Manager:** Custom Windows-inspired Qt/PySide6 application
- **Optional apps:** First-login app selection window

## Choose your own apps

The OS does not automatically install the optional application catalogue. At the first KDE login after installation, the **My Custom Distro App Setup** window lets each user choose what to install into their own account.

Available choices:

| Category | Optional applications |
|---|---|
| Everyday | Firefox, Thunderbird, LibreOffice, VLC |
| Gaming | Lutris, ProtonUp-Qt, Mission Center |
| Creative | OBS Studio, GIMP, Krita, Kdenlive, Blender |
| Customisation | Flatseal, Warehouse |

The chooser includes category presets, an All apps option, individual checkboxes and search. No listed app is installed unless selected. Press **Skip for now** to leave the optional apps out. Open **My Custom Distro Center → Choose optional applications** later to install or add more.

Optional apps are installed per-user from Flathub; this does not require administrator access and does not install them for other user accounts. Steam and the core KDE desktop tools are provided by the Bazzite base image and are not part of the optional list.

**Important:** this selection window appears after the OS has been installed and the user logs in for the first time. It is not currently embedded inside the OS installer's own screens.

## My Custom Distro Center

The control centre provides shortcuts to Task Manager, optional app setup, Firefox (if selected), Steam, KDE System Settings, Discover, Konsole, Dolphin, KDE System Monitor, screenshots and the Afterburn colour scheme.

## Custom Task Manager

A Windows-inspired Qt/PySide6 application with process, performance, app history, startup, users, details and services pages.

Its settings include colour presets, a custom accent colour, compact/comfortable/spacious density, refresh speed, graph history, optional NVIDIA telemetry, visible process columns, always-on-top mode, optional local usage tracking, and settings import/export.

## Custom artwork

- Afterburn 2560×1440 wallpaper
- Original distribution icon
- Afterburn KDE Plasma colour scheme

## Testing without dual boot

A safe route is to build the custom image, generate an ISO from the published image using BlueBuild's `generate-iso` command, and attach that ISO to a new VirtualBox virtual machine as a virtual optical disc. Install it onto the VM's virtual disk; this leaves the real Windows partitions untouched.

The official ISO instructions are at [BlueBuild — Generate an ISO](https://blue-build.org/how-to/generate-iso/). The command format is:

```bash
sudo bluebuild generate-iso --iso-name my-custom-distro.iso image ghcr.io/oskaras424-sudo/my-custom-distro:latest
```

The ISO can be attached directly to VirtualBox; no physical USB stick is needed. Give the VM a separate virtual disk (for example, 80 GB dynamically allocated), enable EFI, and keep its disk separate from the host's Windows drives. VirtualBox's virtual graphics adapter is not a substitute for testing native GTX 1660 Super performance; the VM is for checking installation, desktop behaviour and the app chooser.

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
- [x] Add a first-login per-user optional app chooser
- [ ] Verify the automated image build and container signing
- [ ] Make the Afterburn desktop theme and wallpaper first-login defaults
- [ ] Expand desktop, panel, launcher and window-effect customisation
- [ ] Test the image in VirtualBox
- [ ] Prepare installation media and release documentation

## Development

Edit `recipes/recipe.yml` to change the image build. The workflow in `.github/workflows/build.yml` runs automatically when relevant files are pushed and can also be started manually from GitHub Actions.

The workflow expects a GitHub Actions secret named `SIGNING_SECRET` for cosign signing. Never put private signing keys in the repository or share them in chat. See the [BlueBuild signing guide](https://blue-build.org/how-to/cosign/).

See the [BlueBuild recipe reference](https://blue-build.org/reference/recipe/), [Bazzite documentation](https://docs.bazzite.gg/) and [KDE documentation](https://apps.kde.org/) before changing the base image or adding packages.
