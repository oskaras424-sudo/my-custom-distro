#!/usr/bin/python3
"""My Custom Distro Task Manager — Windows-style system control with deep personalisation."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import psutil
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QFrame, QComboBox, QSpinBox, QCheckBox, QColorDialog,
    QFileDialog, QMessageBox, QFormLayout, QScrollArea, QAbstractItemView,
)

APP = "My Custom Distro Task Manager"
CONFIG = Path.home() / ".config/my-custom-distro/task-manager.json"

THEMES = {
    "Afterburn": ("#0b0c11", "#12141c", "#1a1c27", "#f4f0f3", "#a3a1ad", "#e83a5e", "#ff8197", "#2c2e3b"),
    "Midnight": ("#090e18", "#101827", "#172338", "#edf4ff", "#9aabc3", "#548dff", "#8bb5ff", "#293951"),
    "Emerald": ("#09120f", "#101d18", "#182b22", "#e9f5ed", "#9bb7a6", "#22ae78", "#66d5a9", "#294638"),
    "Violet": ("#100d18", "#191426", "#241d35", "#f4efff", "#afa4c7", "#9b6cff", "#c1a3ff", "#3b3152"),
    "Arctic": ("#0b1117", "#121e27", "#1a2c38", "#effaff", "#a3bac4", "#25a8c7", "#71d4e8", "#2e4855"),
    "Light": ("#edf0f5", "#ffffff", "#f4f6fa", "#1c2430", "#687486", "#c52c51", "#e34b70", "#d6dce6"),
}

DEFAULTS = {
    "theme": "Afterburn", "accent": "", "density": "Comfortable",
    "refresh_ms": 1500, "history_points": 60, "always_on_top": False,
    "show_gpu": True, "show_grid": True, "track_history": False,
    "columns": {"Status": True, "CPU": True, "Memory": True, "PID": True, "User": True, "Command": False},
    "usage": {},
}

def load_config():
    data = dict(DEFAULTS)
    data["columns"] = dict(DEFAULTS["columns"])
    try:
        saved = json.loads(CONFIG.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            data.update(saved)
            cols = dict(DEFAULTS["columns"])
            if isinstance(saved.get("columns"), dict):
                cols.update(saved["columns"])
            data["columns"] = cols
    except (OSError, json.JSONDecodeError):
        pass
    if data.get("theme") not in THEMES:
        data["theme"] = "Afterburn"
    data["refresh_ms"] = max(500, min(5000, int(data.get("refresh_ms", 1500))))
    data["history_points"] = max(20, min(180, int(data.get("history_points", 60))))
    if not isinstance(data.get("usage"), dict):
        data["usage"] = {}
    return data

def save_config(config):
    try:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")
    except OSError:
        pass

def byte_text(number):
    if number is None:
        return "—"
    value = float(number)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{int(value)} B" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"

class Graph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = []
        self.maximum = 100
        self.color = "#e83a5e"
        self.background = "#12141c"
        self.grid_color = "#2c2e3b"
        self.grid = True
        self.setMinimumHeight(245)

    def set_data(self, values, maximum, color, background, grid_color, grid=True):
        self.values = list(values)
        self.maximum = max(float(maximum), 1.0)
        self.color, self.background, self.grid_color, self.grid = color, background, grid_color, grid
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = self.rect().adjusted(18, 14, -18, -24)
        painter.fillRect(self.rect(), QColor(self.background))
        if self.grid:
            pen = QPen(QColor(self.grid_color), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            for index in range(5):
                y = area.top() + index * area.height() / 4
                painter.drawLine(int(area.left()), int(y), int(area.right()), int(y))
        if len(self.values) < 2:
            painter.setPen(QColor("#a3a1ad"))
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, "Collecting performance data…")
            return
        pts = []
        for i, value in enumerate(self.values):
            x = area.left() + i * area.width() / max(1, len(self.values) - 1)
            y = area.bottom() - max(0.0, min(self.maximum, float(value))) / self.maximum * area.height()
            pts.append((x, y))
        line = QPainterPath()
        line.moveTo(*pts[0])
        for pt in pts[1:]:
            line.lineTo(*pt)
        fill = QPainterPath(line)
        fill.lineTo(pts[-1][0], area.bottom())
        fill.lineTo(pts[0][0], area.bottom())
        fill.closeSubpath()
        fill_color = QColor(self.color)
        fill_color.setAlpha(38)
        painter.fillPath(fill, QBrush(fill_color))
        painter.setPen(QPen(QColor(self.color), 2.5))
        painter.drawPath(line)
        painter.setPen(QColor("#a3a1ad"))
        painter.drawText(int(area.left()), int(area.bottom() + 18), "60 seconds ago")
        painter.drawText(int(area.right() - 30), int(area.bottom() + 18), "Now")

class Card(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        self.name = QLabel(title)
        self.name.setObjectName("muted")
        self.value = QLabel("—")
        self.value.setObjectName("cardValue")
        self.detail = QLabel("Waiting for data")
        self.detail.setObjectName("muted")
        layout.addWidget(self.name)
        layout.addWidget(self.value)
        layout.addWidget(self.detail)

    def set_values(self, value, detail):
        self.value.setText(value)
        self.detail.setText(detail)

class TaskManager(QMainWindow):
    NAV = [("Processes", "▦"), ("Performance", "◒"), ("App history", "◷"),
           ("Startup apps", "↗"), ("Users", "◎"), ("Details", "☷"),
           ("Services", "⚙"), ("Settings", "✳")]

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.rows = []
        self.cpu_hist, self.mem_hist, self.disk_hist, self.net_hist = [], [], [], []
        self.last_disk = psutil.disk_io_counters()
        self.last_net = psutil.net_io_counters()
        self.last_time = time.monotonic()
        self.gpu = {}
        self.gpu_ticks = 0
        self.usage = dict(self.cfg["usage"])
        self.save_tick = 0
        self.p = self.palette()
        self.setWindowTitle("Task Manager — My Custom Distro")
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/my-custom-distro.svg"))
        self.resize(1360, 850)
        self.setMinimumSize(980, 650)
        self.build()
        self.apply_theme()
        self.apply_window_options()
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search.setFocus)
        QShortcut(QKeySequence("F5"), self, activated=self.refresh)
        QShortcut(QKeySequence("Delete"), self, activated=self.end_task)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(self.cfg["refresh_ms"])
        self.refresh()
        self.go("Processes")

    def palette(self):
        bg, panel, raised, text, muted, accent, accent2, border = THEMES[self.cfg["theme"]]
        custom = self.cfg.get("accent")
        if custom and QColor(custom).isValid():
            accent = QColor(custom).name()
        return dict(bg=bg, panel=panel, raised=raised, text=text, muted=muted,
                    accent=accent, accent2=accent2, border=border)

    def build(self):
        root = QWidget()
        root_l = QVBoxLayout(root)
        root_l.setContentsMargins(0, 0, 0, 0)
        root_l.setSpacing(0)
        self.setCentralWidget(root)

        top = QFrame()
        top.setObjectName("top")
        top.setFixedHeight(74)
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(22, 10, 22, 10)
        mark = QLabel("M")
        mark.setObjectName("mark")
        mark.setFixedSize(42, 42)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_l.addWidget(mark)
        titles = QVBoxLayout()
        titles.setSpacing(1)
        title = QLabel("TASK MANAGER")
        title.setObjectName("brand")
        subtitle = QLabel("SYSTEM CONTROL  /  GAMING EDITION")
        subtitle.setObjectName("muted")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        holder = QWidget()
        holder.setLayout(titles)
        top_l.addWidget(holder)
        top_l.addStretch(1)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search processes…   Ctrl + F")
        self.search.setClearButtonEnabled(True)
        self.search.setMaximumWidth(330)
        self.search.textChanged.connect(self.update_processes)
        top_l.addWidget(self.search)
        refresh = QPushButton("↻  Refresh")
        refresh.clicked.connect(self.refresh)
        top_l.addWidget(refresh)
        root_l.addWidget(top)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root_l.addLayout(body, 1)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(215)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(12, 18, 12, 12)
        side.setSpacing(5)
        eyebrow = QLabel("OVERVIEW")
        eyebrow.setObjectName("eyebrow")
        side.addWidget(eyebrow)
        self.nav = {}
        for name, symbol in self.NAV:
            button = QPushButton(f"{symbol}    {name}")
            button.setObjectName("nav")
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.clicked.connect(lambda checked=False, n=name: self.go(n))
            side.addWidget(button)
            self.nav[name] = button
        side.addStretch(1)
        foot = QLabel("MY CUSTOM DISTRO\nBUILD 001  ·  EXPERIMENTAL")
        foot.setObjectName("muted")
        side.addWidget(foot)
        body.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.pages = {}
        self.make_processes()
        self.make_performance()
        self.make_history()
        self.make_startup()
        self.make_users()
        self.make_details()
        self.make_services()
        self.make_settings()
        for name, _ in self.NAV:
            self.stack.addWidget(self.pages[name])
        body.addWidget(self.stack, 1)
        self.statusBar().showMessage("Ready · Local system statistics")

    def page(self, name, description):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(25, 22, 25, 20)
        v.setSpacing(14)
        h = QLabel(name)
        h.setObjectName("pageTitle")
        d = QLabel(description)
        d.setObjectName("muted")
        v.addWidget(h)
        v.addWidget(d)
        self.pages[name] = w
        return v

    def table(self, headers):
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setAlternatingRowColors(True)
        t.setShowGrid(False)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        t.horizontalHeader().setStretchLastSection(True)
        t.setSortingEnabled(True)
        return t

    def make_processes(self):
        v = self.page("Processes", "See what's running, what it's using, and manage individual tasks.")
        bar = QHBoxLayout()
        self.proc_count = QLabel("— processes")
        self.proc_count.setObjectName("muted")
        bar.addWidget(self.proc_count)
        bar.addStretch(1)
        self.end_button = QPushButton("End task")
        self.end_button.setObjectName("danger")
        self.end_button.clicked.connect(self.end_task)
        bar.addWidget(self.end_button)
        v.addLayout(bar)
        self.process_table = self.table(["Name", "Status", "CPU", "Memory", "PID", "User", "Command"])
        for i, width in enumerate((225, 100, 80, 110, 80, 130, 260)):
            self.process_table.setColumnWidth(i, width)
        self.process_table.itemSelectionChanged.connect(self.selection_changed)
        v.addWidget(self.process_table, 1)

    def make_performance(self):
        v = self.page("Performance", "Live CPU, memory, storage, network and NVIDIA GPU activity.")
        grid = QGridLayout()
        self.cards = {}
        for i, key in enumerate(("CPU", "Memory", "Disk", "Network")):
            self.cards[key] = Card(key)
            grid.addWidget(self.cards[key], 0, i)
        v.addLayout(grid)
        row = QHBoxLayout()
        lab = QLabel("PERFORMANCE HISTORY")
        lab.setObjectName("eyebrow")
        row.addWidget(lab)
        row.addStretch(1)
        self.graph_select = QComboBox()
        self.graph_select.addItems(["CPU", "Memory", "Disk", "Network", "GPU"])
        self.graph_select.currentTextChanged.connect(self.update_graph)
        row.addWidget(self.graph_select)
        v.addLayout(row)
        box = QFrame()
        box.setObjectName("card")
        box_l = QVBoxLayout(box)
        self.graph = Graph()
        box_l.addWidget(self.graph)
        v.addWidget(box, 1)
        self.gpu_label = QLabel("NVIDIA telemetry will appear here when available.")
        self.gpu_label.setObjectName("muted")
        v.addWidget(self.gpu_label)

    def make_history(self):
        v = self.page("App history", "Optional local-only process usage history. Nothing is uploaded.")
        box = QFrame()
        box.setObjectName("card")
        b = QVBoxLayout(box)
        h = QLabel("Your activity stays on this device")
        h.setObjectName("cardTitle")
        note = QLabel("Tracking is off by default. When enabled, this page records the time that process names are present, saved locally in your user configuration folder.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        self.track = QCheckBox("Enable local process usage tracking")
        self.track.setChecked(bool(self.cfg["track_history"]))
        self.track.toggled.connect(self.toggle_tracking)
        b.addWidget(h)
        b.addWidget(note)
        b.addWidget(self.track)
        v.addWidget(box)
        self.history_table = self.table(["Process", "Observed time"])
        v.addWidget(self.history_table, 1)
        clear = QPushButton("Clear usage history")
        clear.clicked.connect(self.clear_history)
        v.addWidget(clear, 0, Qt.AlignmentFlag.AlignRight)

    def make_startup(self):
        v = self.page("Startup apps", "Review desktop applications configured to start when you sign in.")
        self.startup_table = self.table(["Application", "Command", "Source"])
        self.startup_table.setColumnWidth(0, 240)
        self.startup_table.setColumnWidth(1, 430)
        v.addWidget(self.startup_table, 1)
        row = QHBoxLayout()
        row.addWidget(QLabel("Read-only review in this first release."), 1)
        b = QPushButton("Rescan")
        b.clicked.connect(self.populate_startup)
        row.addWidget(b)
        v.addLayout(row)

    def make_users(self):
        v = self.page("Users", "Logged-in sessions visible to your current account.")
        self.users_table = self.table(["User", "Terminal", "Host", "Started"])
        v.addWidget(self.users_table, 1)

    def make_details(self):
        v = self.page("Details", "Process-by-process view with executable paths and thread counts.")
        self.details_table = self.table(["Name", "PID", "Status", "CPU", "Memory", "Threads", "Executable"])
        self.details_table.setColumnWidth(0, 220)
        self.details_table.setColumnWidth(6, 390)
        v.addWidget(self.details_table, 1)

    def make_services(self):
        v = self.page("Services", "System service status. This first release is read-only.")
        self.services_table = self.table(["Service", "Load", "Active", "Sub-state", "Description"])
        self.services_table.setColumnWidth(0, 300)
        v.addWidget(self.services_table, 1)
        b = QPushButton("Refresh services")
        b.clicked.connect(self.populate_services)
        v.addWidget(b, 0, Qt.AlignmentFlag.AlignRight)

    def make_settings(self):
        v = self.page("Settings", "Personalise the Task Manager's appearance, layout and behaviour.")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setSpacing(12)

        look = QFrame()
        look.setObjectName("card")
        ll = QVBoxLayout(look)
        title = QLabel("Appearance & layout")
        title.setObjectName("cardTitle")
        ll.addWidget(title)
        form = QFormLayout()
        self.theme = QComboBox()
        self.theme.addItems(THEMES.keys())
        self.theme.setCurrentText(self.cfg["theme"])
        self.theme.currentTextChanged.connect(self.set_theme)
        form.addRow("Colour preset", self.theme)
        self.density = QComboBox()
        self.density.addItems(["Compact", "Comfortable", "Spacious"])
        self.density.setCurrentText(self.cfg["density"])
        self.density.currentTextChanged.connect(self.set_density)
        form.addRow("Interface density", self.density)
        self.accent_button = QPushButton("Choose custom accent colour…")
        self.accent_button.clicked.connect(self.choose_accent)
        form.addRow("Accent colour", self.accent_button)
        self.topmost = QCheckBox("Keep above other windows")
        self.topmost.setChecked(bool(self.cfg["always_on_top"]))
        self.topmost.toggled.connect(self.set_topmost)
        form.addRow("Window", self.topmost)
        ll.addLayout(form)
        lay.addWidget(look)

        behaviour = QFrame()
        behaviour.setObjectName("card")
        bl = QVBoxLayout(behaviour)
        btitle = QLabel("Monitoring & behaviour")
        btitle.setObjectName("cardTitle")
        bl.addWidget(btitle)
        bf = QFormLayout()
        self.refresh_rate = QSpinBox()
        self.refresh_rate.setRange(500, 5000)
        self.refresh_rate.setSingleStep(250)
        self.refresh_rate.setSuffix(" ms")
        self.refresh_rate.setValue(self.cfg["refresh_ms"])
        self.refresh_rate.valueChanged.connect(self.set_refresh)
        bf.addRow("Refresh interval", self.refresh_rate)
        self.points = QSpinBox()
        self.points.setRange(20, 180)
        self.points.setSingleStep(10)
        self.points.setSuffix(" points")
        self.points.setValue(self.cfg["history_points"])
        self.points.valueChanged.connect(self.set_points)
        bf.addRow("Chart history length", self.points)
        self.gpu_toggle = QCheckBox("Show NVIDIA GPU metrics when available")
        self.gpu_toggle.setChecked(bool(self.cfg["show_gpu"]))
        self.gpu_toggle.toggled.connect(self.set_gpu)
        bf.addRow("GPU", self.gpu_toggle)
        self.grid_toggle = QCheckBox("Show chart grid lines")
        self.grid_toggle.setChecked(bool(self.cfg["show_grid"]))
        self.grid_toggle.toggled.connect(self.set_grid)
        bf.addRow("Charts", self.grid_toggle)
        bl.addLayout(bf)
        lay.addWidget(behaviour)

        columns = QFrame()
        columns.setObjectName("card")
        cl = QVBoxLayout(columns)
        ctitle = QLabel("Process table columns")
        ctitle.setObjectName("cardTitle")
        cl.addWidget(ctitle)
        self.column_checks = {}
        cg = QGridLayout()
        for index, name in enumerate(self.cfg["columns"]):
            check = QCheckBox(name)
            check.setChecked(bool(self.cfg["columns"][name]))
            check.toggled.connect(lambda enabled, n=name: self.set_column(n, enabled))
            self.column_checks[name] = check
            cg.addWidget(check, index // 3, index % 3)
        cl.addLayout(cg)
        lay.addWidget(columns)

        tools = QFrame()
        tools.setObjectName("card")
        tl = QVBoxLayout(tools)
        ttitle = QLabel("Your configuration")
        ttitle.setObjectName("cardTitle")
        tl.addWidget(ttitle)
        buttons = QHBoxLayout()
        for text, fn in (("Export settings", self.export_settings), ("Import settings", self.import_settings), ("Reset settings", self.reset_settings)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            buttons.addWidget(b)
        tl.addLayout(buttons)
        help_text = QLabel("Preferences are saved locally in ~/.config/my-custom-distro/task-manager.json. Export and import to move your setup between computers.")
        help_text.setWordWrap(True)
        help_text.setObjectName("muted")
        tl.addWidget(help_text)
        lay.addWidget(tools)
        lay.addStretch(1)
        scroll.setWidget(inner)
        v.addWidget(scroll, 1)

    def apply_theme(self):
        p = self.p
        row_h = {"Compact": 27, "Comfortable": 35, "Spacious": 44}.get(self.cfg["density"], 35)
        self.process_table.verticalHeader().setDefaultSectionSize(row_h)
        self.details_table.verticalHeader().setDefaultSectionSize(row_h)
        self.sidebar.setFixedWidth(185 if self.cfg["density"] == "Compact" else 215)
        self.setStyleSheet(f"""
        QWidget {{ color:{p['text']}; font-family:'Inter','Segoe UI',sans-serif; font-size:13px; }}
        QMainWindow {{ background:{p['bg']}; }}
        QFrame#top {{ background:{p['panel']}; border-bottom:1px solid {p['border']}; }}
        QFrame#sidebar {{ background:{p['panel']}; border-right:1px solid {p['border']}; }}
        QLabel#mark {{ background:{p['accent']}; color:white; border-radius:11px; font-size:23px; font-weight:900; }}
        QLabel#brand {{ color:{p['text']}; font-size:15px; font-weight:850; letter-spacing:1px; }}
        QLabel#pageTitle {{ font-size:26px; font-weight:800; color:{p['text']}; }}
        QLabel#eyebrow {{ color:{p['muted']}; font-size:10px; font-weight:800; letter-spacing:1.5px; }}
        QLabel#muted {{ color:{p['muted']}; font-size:11px; }}
        QLabel#cardTitle {{ font-size:15px; font-weight:750; }}
        QLabel#cardValue {{ font-size:25px; font-weight:850; }}
        QFrame#card {{ background:{p['panel']}; border:1px solid {p['border']}; border-radius:11px; }}
        QPushButton {{ background:{p['raised']}; border:1px solid {p['border']}; border-radius:7px; padding:8px 13px; font-weight:600; }}
        QPushButton:hover {{ border-color:{p['accent']}; background:{p['surface'] if 'surface' in p else p['raised']}; }}
        QPushButton#danger {{ background:{p['accent']}; color:white; border-color:{p['accent']}; padding:9px 17px; }}
        QPushButton#nav {{ text-align:left; background:transparent; border:0; padding:10px 12px; color:{p['muted']}; }}
        QPushButton#nav:hover {{ background:{p['raised']}; color:{p['text']}; }}
        QPushButton#nav:checked {{ background:{p['raised']}; color:{p['accent2']}; border-left:3px solid {p['accent']}; font-weight:800; }}
        QLineEdit,QComboBox,QSpinBox {{ background:{p['raised']}; border:1px solid {p['border']}; border-radius:7px; padding:8px 10px; min-height:20px; selection-background-color:{p['accent']}; }}
        QComboBox QAbstractItemView {{ background:{p['panel']}; selection-background-color:{p['accent']}; }}
        QTableWidget {{ background:{p['panel']}; alternate-background-color:{p['raised']}; border:1px solid {p['border']}; border-radius:9px; gridline-color:transparent; selection-background-color:{p['raised']}; outline:0; }}
        QTableWidget::item {{ padding:5px 7px; border:0; }}
        QHeaderView::section {{ background:{p['raised']}; color:{p['muted']}; border:0; border-bottom:1px solid {p['border']}; padding:9px 7px; font-size:11px; font-weight:750; }}
        QCheckBox {{ spacing:8px; }}
        QCheckBox::indicator {{ width:16px; height:16px; border:1px solid {p['muted']}; border-radius:4px; background:{p['raised']}; }}
        QCheckBox::indicator:checked {{ background:{p['accent']}; border-color:{p['accent']}; }}
        QStatusBar {{ background:{p['panel']}; color:{p['muted']}; border-top:1px solid {p['border']}; }}
        QScrollArea {{ border:0; background:transparent; }}
        """)
        self.graph.set_data(self.cpu_hist, 100, p["accent"], p["panel"], p["border"], self.cfg["show_grid"])

    def apply_window_options(self):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, bool(self.cfg["always_on_top"]))
        self.show()

    def go(self, name):
        self.stack.setCurrentWidget(self.pages[name])
        for key, button in self.nav.items():
            button.setChecked(key == name)
        if name == "Startup apps": self.populate_startup()
        if name == "Users": self.populate_users()
        if name == "Services": self.populate_services()
        if name == "Details": self.populate_details()
        if name == "App history": self.populate_history()

    def refresh(self):
        self.collect_processes()
        self.collect_metrics()
        self.update_processes()
        self.populate_details()
        self.update_cards()
        self.update_graph()
        if self.cfg["track_history"]:
            self.record_usage()
        if self.stack.currentWidget() is self.pages["App history"]:
            self.populate_history()

    def collect_processes(self):
        result = []
        for proc in psutil.process_iter(attrs=["pid", "name", "username", "status", "memory_info", "cmdline", "exe"]):
            try:
                info = proc.info
                memory = info.get("memory_info")
                cmd = info.get("cmdline") or []
                result.append({
                    "pid": int(info["pid"]), "name": str(info.get("name") or "Unknown"),
                    "status": str(info.get("status") or "Unknown"),
                    "cpu": max(0.0, float(proc.cpu_percent(interval=None))),
                    "memory": int(memory.rss) if memory else 0,
                    "user": str(info.get("username") or "—"),
                    "command": str(info.get("exe") or " ".join(cmd)),
                    "threads": proc.num_threads(), "proc": proc,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError, KeyError):
                continue
        self.rows = result
        self.proc_count.setText(f"{len(result)} processes")

    def collect_metrics(self):
        now = time.monotonic()
        dt = max(0.1, now - self.last_time)
        self.last_time = now
        self.cpu_hist.append(psutil.cpu_percent(interval=None))
        self.mem_hist.append(psutil.virtual_memory().percent)
        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()
        disk_rate = 0
        net_rate = 0
        if disk and self.last_disk:
            disk_rate = max(0, disk.read_bytes + disk.write_bytes - self.last_disk.read_bytes - self.last_disk.write_bytes) / dt / 1048576
        if net and self.last_net:
            net_rate = max(0, net.bytes_recv + net.bytes_sent - self.last_net.bytes_recv - self.last_net.bytes_sent) / dt / 1048576
        self.disk_hist.append(disk_rate)
        self.net_hist.append(net_rate)
        self.last_disk, self.last_net = disk, net
        limit = self.cfg["history_points"]
        for seq in (self.cpu_hist, self.mem_hist, self.disk_hist, self.net_hist):
            del seq[:-limit]
        self.gpu_ticks += 1
        if self.cfg["show_gpu"] and self.gpu_ticks % 4 == 0:
            self.gpu = self.read_gpu()

    def read_gpu(self):
        if not shutil.which("nvidia-smi"):
            return {}
        try:
            res = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=1.5, check=False)
            parts = [x.strip() for x in res.stdout.strip().splitlines()[0].split(",")]
            if len(parts) >= 4:
                return {"util": float(parts[0]), "used": float(parts[1]), "total": float(parts[2]), "temp": float(parts[3])}
        except (OSError, subprocess.SubprocessError, ValueError, IndexError):
            pass
        return {}

    def update_processes(self, _query=""):
        selected = None
        selection = self.process_table.selectionModel().selectedRows()
        if selection:
            item = self.process_table.item(selection[0].row(), 0)
            if item:
                selected = item.data(Qt.ItemDataRole.UserRole)
        query = self.search.text().lower().strip()
        rows = [r for r in self.rows if not query or query in r["name"].lower() or query in str(r["pid"]) or query in r["command"].lower()]
        rows.sort(key=lambda row: row["cpu"], reverse=True)
        t = self.process_table
        t.setSortingEnabled(False)
        t.setRowCount(0)
        for data in rows:
            r = t.rowCount()
            t.insertRow(r)
            values = [data["name"], data["status"], f"{data['cpu']:.1f}%", byte_text(data["memory"]), str(data["pid"]), data["user"], data["command"]]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, data["pid"])
                if col in (2, 3, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                t.setItem(r, col, item)
        t.setSortingEnabled(True)
        cols = self.cfg["columns"]
        for col, key in ((1, "Status"), (2, "CPU"), (3, "Memory"), (4, "PID"), (5, "User"), (6, "Command")):
            t.setColumnHidden(col, not cols.get(key, True))
        if selected:
            for r in range(t.rowCount()):
                if t.item(r, 0).data(Qt.ItemDataRole.UserRole) == selected:
                    t.selectRow(r)
                    break
        self.selection_changed()

    def selection_changed(self):
        self.end_button.setEnabled(bool(self.process_table.selectionModel().selectedRows()))

    def end_task(self):
        selected = self.process_table.selectionModel().selectedRows()
        if not selected:
            return
        item = self.process_table.item(selected[0].row(), 0)
        pid = int(item.data(Qt.ItemDataRole.UserRole))
        proc = next((r["proc"] for r in self.rows if r["pid"] == pid), None)
        if not proc:
            return
        name = next((r["name"] for r in self.rows if r["pid"] == pid), str(pid))
        answer = QMessageBox.question(self, "End task", f"End {name} (PID {pid})?\\n\\nUnsaved work may be lost.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                force = QMessageBox.question(self, "Still running", f"{name} did not close normally. Force stop it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
                if force == QMessageBox.StandardButton.Yes:
                    proc.kill()
        except psutil.AccessDenied:
            QMessageBox.warning(self, "Permission denied", "Your account cannot end this process.")
        except psutil.NoSuchProcess:
            pass
        except OSError as error:
            QMessageBox.warning(self, "Could not end task", str(error))
        self.refresh()

    def update_cards(self):
        cpu = self.cpu_hist[-1] if self.cpu_hist else 0
        mem = psutil.virtual_memory()
        disk = self.disk_hist[-1] if self.disk_hist else 0
        net = self.net_hist[-1] if self.net_hist else 0
        self.cards["CPU"].set_values(f"{cpu:.0f}%", f"{psutil.cpu_count() or '—'} logical processors")
        self.cards["Memory"].set_values(f"{mem.percent:.0f}%", f"{byte_text(mem.used)} / {byte_text(mem.total)}")
        self.cards["Disk"].set_values(f"{disk:.1f} MB/s", "Combined read + write")
        self.cards["Network"].set_values(f"{net:.1f} MB/s", "Combined send + receive")
        if not self.cfg["show_gpu"]:
            self.gpu_label.setText("GPU telemetry is hidden in Settings.")
        elif self.gpu:
            g = self.gpu
            self.gpu_label.setText(f"NVIDIA GPU  ·  {g['util']:.0f}% load  ·  {g['temp']:.0f}°C  ·  VRAM {byte_text(g['used'] * 1048576)} / {byte_text(g['total'] * 1048576)}")
        else:
            self.gpu_label.setText("NVIDIA telemetry unavailable — it will appear when nvidia-smi is available.")

    def update_graph(self, _name=None):
        if not hasattr(self, "graph"):
            return
        name = self.graph_select.currentText()
        if name == "CPU": data, maximum = self.cpu_hist, 100
        elif name == "Memory": data, maximum = self.mem_hist, 100
        elif name == "Disk": data, maximum = self.disk_hist, max(5, max(self.disk_hist, default=0) * 1.2)
        elif name == "Network": data, maximum = self.net_hist, max(5, max(self.net_hist, default=0) * 1.2)
        else: data, maximum = ([self.gpu.get("util", 0)] if self.gpu else []), 100
        self.graph.set_data(data, maximum, self.p["accent"], self.p["panel"], self.p["border"], self.cfg["show_grid"])

    def populate_details(self):
        if not hasattr(self, "details_table"):
            return
        query = self.search.text().lower().strip()
        t = self.details_table
        t.setSortingEnabled(False)
        t.setRowCount(0)
        for d in self.rows:
            if query and query not in d["name"].lower() and query not in str(d["pid"]) and query not in d["command"].lower():
                continue
            r = t.rowCount()
            t.insertRow(r)
            for col, value in enumerate([d["name"], str(d["pid"]), d["status"], f"{d['cpu']:.1f}%", byte_text(d["memory"]), str(d["threads"]), d["command"]]):
                t.setItem(r, col, QTableWidgetItem(value))
        t.setSortingEnabled(True)

    def populate_startup(self):
        t = self.startup_table
        t.setRowCount(0)
        for folder in (Path.home() / ".config/autostart", Path("/etc/xdg/autostart")):
            try:
                entries = folder.glob("*.desktop")
                for file in sorted(entries):
                    try:
                        lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
                        if any(x.lower() in ("hidden=true", "nodisplay=true") for x in lines):
                            continue
                        name = next((x.split("=", 1)[1] for x in lines if x.startswith("Name=")), file.stem)
                        command = next((x.split("=", 1)[1] for x in lines if x.startswith("Exec=")), "")
                        r = t.rowCount()
                        t.insertRow(r)
                        for col, value in enumerate([name, command, "User" if folder.name == "autostart" and folder.parent.name == ".config" else "System"]):
                            t.setItem(r, col, QTableWidgetItem(value))
                    except OSError:
                        pass
            except OSError:
                pass

    def populate_users(self):
        t = self.users_table
        t.setRowCount(0)
        try:
            users = psutil.users()
        except psutil.Error:
            users = []
        for u in users:
            started = time.strftime("%Y-%m-%d %H:%M", time.localtime(u.started)) if u.started else "—"
            r = t.rowCount()
            t.insertRow(r)
            for col, value in enumerate([u.name, u.terminal or "—", u.host or "Local", started]):
                t.setItem(r, col, QTableWidgetItem(value))

    def populate_services(self):
        t = self.services_table
        t.setRowCount(0)
        try:
            res = subprocess.run(["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--no-legend"], capture_output=True, text=True, timeout=4, check=False)
            lines = res.stdout.splitlines()
        except (OSError, subprocess.SubprocessError):
            lines = []
        for line in lines:
            parts = line.split(None, 4)
            if len(parts) < 4:
                continue
            values = parts[:4] + [parts[4] if len(parts) > 4 else ""]
            r = t.rowCount()
            t.insertRow(r)
            for col, value in enumerate(values):
                t.setItem(r, col, QTableWidgetItem(value))

    def record_usage(self):
        step = self.cfg["refresh_ms"] / 1000
        for proc in self.rows:
            name = proc["name"]
            self.usage[name] = self.usage.get(name, 0) + step
        self.save_tick += 1
        if self.save_tick >= 20:
            self.cfg["usage"] = self.usage
            save_config(self.cfg)
            self.save_tick = 0

    def populate_history(self):
        t = self.history_table
        t.setRowCount(0)
        for name, seconds in sorted(self.usage.items(), key=lambda x: x[1], reverse=True):
            r = t.rowCount()
            t.insertRow(r)
            t.setItem(r, 0, QTableWidgetItem(name))
            t.setItem(r, 1, QTableWidgetItem(f"{seconds / 60:.1f} min"))

    def toggle_tracking(self, enabled):
        self.cfg["track_history"] = enabled
        save_config(self.cfg)

    def clear_history(self):
        answer = QMessageBox.question(self, "Clear history", "Delete all locally saved process usage history?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Yes:
            self.usage.clear()
            self.cfg["usage"] = {}
            save_config(self.cfg)
            self.populate_history()

    def persist(self):
        save_config(self.cfg)

    def set_theme(self, name):
        if name not in THEMES:
            return
        previous = self.p["accent"]
        self.cfg["theme"] = name
        self.cfg["accent"] = ""
        self.p = self.palette()
        self.apply_theme()
        self.persist()

    def set_density(self, value):
        self.cfg["density"] = value
        self.apply_theme()
        self.persist()

    def choose_accent(self):
        color = QColorDialog.getColor(QColor(self.p["accent"]), self, "Choose accent colour")
        if color.isValid():
            self.cfg["accent"] = color.name()
            self.p = self.palette()
            self.apply_theme()
            self.persist()

    def set_topmost(self, enabled):
        self.cfg["always_on_top"] = enabled
        self.persist()
        self.apply_window_options()

    def set_refresh(self, value):
        self.cfg["refresh_ms"] = value
        if hasattr(self, "timer"):
            self.timer.setInterval(value)
        self.persist()

    def set_points(self, value):
        self.cfg["history_points"] = value
        self.persist()

    def set_gpu(self, enabled):
        self.cfg["show_gpu"] = enabled
        self.persist()
        self.update_cards()

    def set_grid(self, enabled):
        self.cfg["show_grid"] = enabled
        self.persist()
        self.update_graph()

    def set_column(self, name, enabled):
        self.cfg["columns"][name] = enabled
        self.persist()
        self.update_processes()

    def export_settings(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export settings", "my-custom-distro-task-manager.json", "JSON files (*.json)")
        if path:
            try:
                Path(path).write_text(json.dumps(self.cfg, indent=2), encoding="utf-8")
                QMessageBox.information(self, "Exported", "Your Task Manager settings have been exported.")
            except OSError as e:
                QMessageBox.warning(self, "Export failed", str(e))

    def import_settings(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import settings", str(Path.home()), "JSON files (*.json)")
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("theme", "Afterburn") not in THEMES:
                raise ValueError("This settings file is not valid.")
            new = dict(DEFAULTS)
            new["columns"] = dict(DEFAULTS["columns"])
            new.update(data)
            if isinstance(data.get("columns"), dict):
                new["columns"].update(data["columns"])
            self.cfg = new
            self.usage = dict(new["usage"])
            self.p = self.palette()
            self.sync_settings()
            self.apply_theme()
            self.timer.setInterval(self.cfg["refresh_ms"])
            self.persist()
            QMessageBox.information(self, "Imported", "Settings have been imported and applied.")
        except (OSError, json.JSONDecodeError, ValueError) as e:
            QMessageBox.warning(self, "Import failed", str(e))

    def sync_settings(self):
        for widget, key in ((self.theme, "theme"), (self.density, "density")):
            widget.blockSignals(True)
            widget.setCurrentText(self.cfg[key])
            widget.blockSignals(False)
        for widget, key in ((self.refresh_rate, "refresh_ms"), (self.points, "history_points")):
            widget.blockSignals(True)
            widget.setValue(self.cfg[key])
            widget.blockSignals(False)
        for widget, key in ((self.topmost, "always_on_top"), (self.gpu_toggle, "show_gpu"), (self.grid_toggle, "show_grid"), (self.track, "track_history")):
            widget.blockSignals(True)
            widget.setChecked(bool(self.cfg[key]))
            widget.blockSignals(False)
        for name, widget in self.column_checks.items():
            widget.blockSignals(True)
            widget.setChecked(bool(self.cfg["columns"].get(name, True)))
            widget.blockSignals(False)

    def reset_settings(self):
        answer = QMessageBox.question(self, "Reset settings", "Restore Task Manager defaults?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Yes:
            self.cfg = dict(DEFAULTS)
            self.cfg["columns"] = dict(DEFAULTS["columns"])
            self.usage = {}
            self.p = self.palette()
            self.sync_settings()
            self.apply_theme()
            self.timer.setInterval(self.cfg["refresh_ms"])
            self.persist()

    def closeEvent(self, event):
        if self.cfg.get("track_history"):
            self.cfg["usage"] = self.usage
            save_config(self.cfg)
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP)
    app.setOrganizationName("My Custom Distro")
    window = TaskManager()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
