#!/usr/bin/python3
"""First-run optional application picker for My Custom Distro.

Applications are installed into the signed-in user's Flatpak installation only.
No optional app is installed unless the user checks it and presses Install.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton,
    QScrollArea, QVBoxLayout, QWidget, QTextEdit,
)

APP_TITLE = "My Custom Distro — App Setup"
MARKER = Path.home() / ".config/my-custom-distro/first-run-app-selection.done"
FLATHUB_URL = "https://flathub.org/repo/flathub.flatpakrepo"

# name, Flatpak ID, category, description
APPS = [
    ("Firefox", "org.mozilla.firefox", "Everyday", "Web browser"),
    ("Thunderbird", "org.mozilla.thunderbird", "Everyday", "Email, calendars and contacts"),
    ("LibreOffice", "org.libreoffice.LibreOffice", "Everyday", "Documents, spreadsheets and presentations"),
    ("VLC", "org.videolan.VLC", "Everyday", "Video and music player"),
    ("OBS Studio", "com.obsproject.Studio", "Creative", "Recording and live streaming"),
    ("GIMP", "org.gimp.GIMP", "Creative", "Image editing"),
    ("Krita", "org.kde.krita", "Creative", "Digital painting and illustration"),
    ("Kdenlive", "org.kde.kdenlive", "Creative", "Video editing"),
    ("Blender", "org.blender.Blender", "Creative", "3D modelling, animation and rendering"),
    ("Lutris", "net.lutris.Lutris", "Gaming", "Manage games from different stores"),
    ("ProtonUp-Qt", "net.davidotek.pupgui2", "Gaming", "Install and manage Proton-GE and Wine-GE"),
    ("Mission Center", "io.missioncenter.MissionCenter", "Gaming", "Visual system resource monitor"),
    ("Flatseal", "com.github.tchx84.Flatseal", "Customisation", "Manage Flatpak application permissions"),
    ("Warehouse", "io.github.flattool.Warehouse", "Customisation", "Manage installed Flatpak applications"),
]

PRESETS = {
    "Everyday": {"org.mozilla.firefox", "org.mozilla.thunderbird",
                 "org.libreoffice.LibreOffice", "org.videolan.VLC"},
    "Gaming": {"net.lutris.Lutris", "net.davidotek.pupgui2",
               "io.missioncenter.MissionCenter"},
    "Creative": {"com.obsproject.Studio", "org.gimp.GIMP", "org.kde.krita",
                 "org.kde.kdenlive", "org.blender.Blender"},
    "Customisation": {"com.github.tchx84.Flatseal", "io.github.flattool.Warehouse"},
}

PALETTE = {
    "bg": "#090a0f",
    "panel": "#11131b",
    "card": "#171a24",
    "raised": "#202330",
    "text": "#f4f0f3",
    "muted": "#9b9ba8",
    "accent": "#e83a5e",
    "accent_hover": "#ff8197",
    "border": "#303342",
}

class AppCard(QFrame):
    def __init__(self, name: str, app_id: str, category: str, description: str):
        super().__init__()
        self.setObjectName("appCard")
        self.app_id = app_id
        self.category = category
        layout = QVBoxLayout(self)
        layout.setContentsMargins(13, 12, 13, 12)
        layout.setSpacing(5)
        self.check = QCheckBox(name)
        self.check.setObjectName("appCheck")
        self.description = QLabel(description)
        self.description.setObjectName("muted")
        self.description.setWordWrap(True)
        self.identifier = QLabel(app_id)
        self.identifier.setObjectName("appId")
        layout.addWidget(self.check)
        layout.addWidget(self.description)
        layout.addWidget(self.identifier)

    def matches(self, query: str) -> bool:
        return query in (
            self.check.text().lower() + " " +
            self.description.text().lower() + " " +
            self.app_id.lower() + " " + self.category.lower()
        )

class AppSetup(QMainWindow):
    def __init__(self, manage: bool = False):
        super().__init__()
        self.manage = manage
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/my-custom-distro.svg"))
        self.resize(1020, 790)
        self.setMinimumSize(820, 640)
        self.cards: dict[str, AppCard] = {}
        self.queue: list[str] = []
        self.failed: list[tuple[str, str]] = []
        self.completed = 0
        self.current_id = ""
        self.current_kind = ""
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(24, 22, 24, 20)
        outer.setSpacing(13)

        header = QHBoxLayout()
        brand = QLabel("M")
        brand.setObjectName("brandMark")
        brand.setFixedSize(48, 48)
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(brand)
        titles = QVBoxLayout()
        titles.setSpacing(1)
        title = QLabel("MAKE IT YOURS")
        title.setObjectName("title")
        subtitle = QLabel("Choose the apps you want. Leave everything else out.")
        subtitle.setObjectName("muted")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch(1)
        outer.addLayout(header)

        info = QFrame()
        info.setObjectName("notice")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(13, 10, 13, 10)
        note = QLabel(
            "Only the apps you select below will be installed. They are installed for your user account, "
            "not for every account on the PC. Steam and the core KDE desktop tools are already supplied "
            "by the Bazzite base."
        )
        note.setWordWrap(True)
        note.setObjectName("noticeText")
        info_layout.addWidget(note)
        outer.addWidget(info)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search apps or categories…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.filter_cards)
        toolbar.addWidget(self.search, 1)
        for label, preset in (
            ("Everyday", "Everyday"),
            ("Gaming", "Gaming"),
            ("Creative", "Creative"),
            ("All apps", "All"),
            ("Custom", "Customisation"),
            ("Clear", "None"),
        ):
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, p=preset: self.apply_preset(p))
            toolbar.addWidget(button)
        outer.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        holder = QWidget()
        content = QVBoxLayout(holder)
        content.setContentsMargins(2, 2, 2, 2)
        content.setSpacing(12)

        categories = [
            ("EVERYDAY", "Browser, email, office and media"),
            ("GAMING", "Additional game management and performance tools"),
            ("CREATIVE", "Streaming, image, video and 3D tools"),
            ("CUSTOMISATION", "Optional app and permission managers"),
        ]
        by_category = {name.title(): [] for name, _ in categories}
        for item in APPS:
            by_category[item[2]].append(item)

        for heading, desc in categories:
            section = QFrame()
            section.setObjectName("section")
            section_layout = QVBoxLayout(section)
            section_layout.setContentsMargins(13, 11, 13, 13)
            section_layout.setSpacing(8)
            head = QHBoxLayout()
            label = QLabel(heading)
            label.setObjectName("sectionTitle")
            detail = QLabel(desc)
            detail.setObjectName("muted")
            head.addWidget(label)
            head.addStretch(1)
            section_layout.addLayout(head)
            section_layout.addWidget(detail)
            grid = QGridLayout()
            grid.setHorizontalSpacing(9)
            grid.setVerticalSpacing(9)
            for i, (name, app_id, category, description) in enumerate(by_category[heading.title()]):
                card = AppCard(name, app_id, category, description)
                self.cards[app_id] = card
                card.check.toggled.connect(self.update_status)
                grid.addWidget(card, i // 2, i % 2)
            section_layout.addLayout(grid)
            content.addWidget(section)
        content.addStretch(1)
        scroll.setWidget(holder)
        outer.addWidget(scroll, 1)

        self.status = QLabel("No optional apps selected.")
        self.status.setObjectName("muted")
        outer.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.hide()
        outer.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(105)
        self.log.hide()
        outer.addWidget(self.log)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.skip_button = QPushButton("Skip for now")
        self.skip_button.clicked.connect(self.skip)
        buttons.addWidget(self.skip_button)
        self.install_button = QPushButton("Install selected apps")
        self.install_button.setObjectName("primary")
        self.install_button.clicked.connect(self.install_selected)
        buttons.addWidget(self.install_button)
        outer.addLayout(buttons)

        self.update_status()

    def apply_theme(self):
        p = PALETTE
        self.setStyleSheet(f"""
          QWidget {{ background:{p['bg']}; color:{p['text']}; font-family:'Inter','Segoe UI',sans-serif; font-size:13px; }}
          QLabel#title {{ font-size:22px; font-weight:850; letter-spacing:1.4px; }}
          QLabel#muted {{ color:{p['muted']}; font-size:11px; }}
          QLabel#brandMark {{ background:{p['accent']}; color:white; border-radius:12px; font-size:24px; font-weight:900; }}
          QFrame#notice {{ background:#211720; border:1px solid #633044; border-radius:10px; }}
          QLabel#noticeText {{ color:#f4dce3; }}
          QFrame#section {{ background:{p['panel']}; border:1px solid {p['border']}; border-radius:11px; }}
          QLabel#sectionTitle {{ font-size:12px; font-weight:850; letter-spacing:1.1px; color:{p['accent_hover']}; }}
          QFrame#appCard {{ background:{p['card']}; border:1px solid {p['border']}; border-radius:9px; }}
          QFrame#appCard:hover {{ border-color:{p['accent']}; }}
          QLabel#appId {{ color:#767989; font-size:10px; }}
          QCheckBox#appCheck {{ font-size:14px; font-weight:750; spacing:8px; }}
          QCheckBox::indicator {{ width:17px; height:17px; border:1px solid #777989; border-radius:4px; background:{p['raised']}; }}
          QCheckBox::indicator:checked {{ background:{p['accent']}; border-color:{p['accent']}; }}
          QLineEdit {{ background:{p['panel']}; border:1px solid {p['border']}; border-radius:8px; padding:9px; }}
          QPushButton {{ background:{p['raised']}; border:1px solid {p['border']}; border-radius:8px; padding:9px 13px; font-weight:650; }}
          QPushButton:hover {{ border-color:{p['accent']}; }}
          QPushButton#primary {{ background:{p['accent']}; border-color:{p['accent']}; color:white; padding:10px 18px; font-weight:800; }}
          QPushButton#primary:hover {{ background:{p['accent_hover']}; }}
          QPushButton:disabled {{ color:#777989; background:{p['panel']}; }}
          QProgressBar {{ background:{p['panel']}; border:1px solid {p['border']}; border-radius:6px; text-align:center; height:17px; }}
          QProgressBar::chunk {{ background:{p['accent']}; border-radius:5px; }}
          QTextEdit {{ background:{p['panel']}; border:1px solid {p['border']}; border-radius:8px; color:{p['muted']}; }}
          QScrollArea {{ border:0; }}
        """)
        self.setStyleSheet(self.styleSheet() + f"QWidget#qt_scrollarea_viewport {{ background:{p['bg']}; }}")

    def selected_ids(self) -> list[str]:
        return [app_id for app_id, card in self.cards.items() if card.check.isChecked()]

    def update_status(self):
        count = len(self.selected_ids())
        self.status.setText(f"{count} app{'s' if count != 1 else ''} selected. Nothing installs until you press Install selected apps.")
        self.install_button.setEnabled(count > 0 and not self.process_is_running())

    def process_is_running(self):
        return self.process.state() != QProcess.ProcessState.NotRunning

    def filter_cards(self, value: str):
        query = value.lower().strip()
        for card in self.cards.values():
            card.setVisible(not query or card.matches(query))

    def apply_preset(self, name: str):
        if name == "All":
            chosen = set(self.cards)
        elif name == "None":
            chosen = set()
        else:
            chosen = PRESETS[name]
        for app_id, card in self.cards.items():
            card.check.setChecked(app_id in chosen)
        self.update_status()

    def skip(self):
        if self.process_is_running():
            return
        try:
            MARKER.parent.mkdir(parents=True, exist_ok=True)
            MARKER.write_text("skipped\n", encoding="utf-8")
        except OSError:
            pass
        self.close()

    def install_selected(self):
        selected = self.selected_ids()
        if not selected:
            QMessageBox.information(self, APP_TITLE, "Choose at least one app, or press Skip for now.")
            return
        if not shutil_which("flatpak"):
            QMessageBox.critical(self, APP_TITLE, "Flatpak is not available. You can install optional apps later through KDE Discover.")
            return

        self.queue = selected
        self.failed = []
        self.completed = 0
        self.install_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.search.setEnabled(False)
        for card in self.cards.values():
            card.check.setEnabled(False)
        self.progress.show()
        self.log.show()
        self.log.clear()
        self.progress.setRange(0, len(self.queue) + 1)
        self.progress.setValue(0)
        self.status.setText("Preparing the per-user Flathub remote…")
        self.current_kind = "remote"
        self.process.start("flatpak", ["remote-add", "--user", "--if-not-exists", "flathub", FLATHUB_URL])

    def read_output(self):
        data = bytes(self.process.readAllStandardOutput()).decode(errors="replace").strip()
        if data:
            self.log.append(data)

    def read_error(self):
        data = bytes(self.process.readAllStandardError()).decode(errors="replace").strip()
        if data:
            self.log.append(data)

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.failed.append((self.current_id or "Flathub", "Flatpak could not be started."))
            self.log.append("Could not start the Flatpak command.")
            self.process_finished(-1, QProcess.ExitStatus.CrashExit)

    def process_finished(self, exit_code: int, _exit_status):
        if self.current_kind == "remote":
            if exit_code != 0:
                self.failed.append(("Flathub setup", "Could not configure the user Flathub remote. Check the internet connection and try again."))
                self.finish_installation()
                return
            self.log.append("Flathub is ready for your user account.")
            self.install_next()
            return

        if self.current_kind == "app":
            name = next((x[0] for x in APPS if x[1] == self.current_id), self.current_id)
            if exit_code == 0:
                self.log.append(f"Installed: {name}")
            else:
                self.failed.append((name, f"Flatpak exited with code {exit_code}."))
                self.log.append(f"Could not install {name}; moving to the next selection.")
            self.completed += 1
            self.progress.setValue(self.completed)
            self.install_next()

    def install_next(self):
        if not self.queue:
            self.finish_installation()
            return
        self.current_id = self.queue.pop(0)
        name = next((x[0] for x in APPS if x[1] == self.current_id), self.current_id)
        self.current_kind = "app"
        self.status.setText(f"Installing {name}…  {self.completed + 1} of {len(self.queue) + self.completed}")
        self.process.start("flatpak", [
            "install", "--user", "--noninteractive", "--assumeyes",
            "flathub", self.current_id
        ])

    def finish_installation(self):
        self.progress.setValue(self.progress.maximum())
        try:
            MARKER.parent.mkdir(parents=True, exist_ok=True)
            MARKER.write_text("completed\n", encoding="utf-8")
        except OSError:
            pass
        self.current_kind = ""
        self.status.setText("App selection finished.")
        self.skip_button.setText("Close")
        self.skip_button.setEnabled(True)
        self.skip_button.clicked.disconnect()
        self.skip_button.clicked.connect(self.close)
        self.search.setEnabled(True)
        for card in self.cards.values():
            card.check.setEnabled(True)
        if self.failed:
            details = "\n".join(f"• {name}: {reason}" for name, reason in self.failed)
            QMessageBox.warning(
                self, "Some apps could not be installed",
                "The rest of your selections were processed.\n\n" + details +
                "\n\nYou can reopen this picker from My Custom Distro Center to retry."
            )
        else:
            QMessageBox.information(
                self, "Setup complete",
                "Your selected apps have been installed for your user account.\n\n"
                "You can reopen this picker from My Custom Distro Center whenever you need it."
            )

    def closeEvent(self, event):
        if self.process_is_running():
            QMessageBox.information(self, APP_TITLE, "Please let the current Flatpak installation finish before closing this window.")
            event.ignore()
            return
        event.accept()

def shutil_which(name: str) -> str | None:
    import shutil
    return shutil.which(name)

def main():
    manage = "--manage" in sys.argv[1:]
    if MARKER.exists() and not manage:
        return 0
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setOrganizationName("My Custom Distro")
    window = AppSetup(manage=manage)
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
