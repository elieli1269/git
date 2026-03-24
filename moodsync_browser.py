#!/usr/bin/env python3
"""MoodSync Browser — Windows Desktop (PyQt6)"""

import sys, os, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar,
    QLineEdit, QPushButton, QLabel, QStatusBar,
    QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QAction

HOME_URL = "https://moodsync.alwaysdata.net"

STYLE = """
QMainWindow, QWidget#central {
    background: #161619;
}
QToolBar {
    background: #17171f;
    border-bottom: 1px solid #2a2a3a;
    padding: 4px 8px;
    spacing: 6px;
}
QPushButton {
    background: #2a2a3a;
    color: #c8c4e8;
    border: 1px solid #3a3a50;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
    min-width: 32px;
}
QPushButton:hover {
    background: #3a3a55;
    border-color: #7c5fe0;
    color: #fff;
}
QPushButton:pressed {
    background: #7c5fe0;
    color: #fff;
}
QPushButton:disabled {
    background: #1e1e28;
    color: #444;
    border-color: #2a2a3a;
}
QLineEdit {
    background: #1e1e28;
    color: #c8c4e8;
    border: 1px solid #3a3a50;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    selection-background-color: #7c5fe0;
}
QLineEdit:focus {
    border-color: #7c5fe0;
    background: #22222e;
}
QStatusBar {
    background: #17171f;
    color: #666;
    font-size: 11px;
    border-top: 1px solid #2a2a3a;
}
QLabel#title_label {
    color: #a090e8;
    font-size: 13px;
    font-weight: 700;
    padding: 0 8px;
}
"""

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoodSync")
        self.resize(420, 820)
        self.setStyleSheet(STYLE)

        # Profil persistant (cookies)
        self._profile = QWebEngineProfile("MoodSync", self)
        self._profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        cache = os.path.join(os.path.expanduser("~"), ".moodsync_browser")
        self._profile.setPersistentStoragePath(cache)
        self._profile.setCachePath(cache)

        # Central widget
        central = QWidget(); central.setObjectName("central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        tb = QToolBar(); tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        self.btn_back = QPushButton("‹")
        self.btn_back.setFixedSize(34, 34)
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._go_back)
        tb.addWidget(self.btn_back)

        self.btn_fwd = QPushButton("›")
        self.btn_fwd.setFixedSize(34, 34)
        self.btn_fwd.setEnabled(False)
        self.btn_fwd.clicked.connect(self._go_fwd)
        tb.addWidget(self.btn_fwd)

        self.btn_reload = QPushButton("↻")
        self.btn_reload.setFixedSize(34, 34)
        self.btn_reload.clicked.connect(self._reload)
        tb.addWidget(self.btn_reload)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Adresse...")
        self.url_bar.returnPressed.connect(self._nav_url)
        tb.addWidget(self.url_bar)

        self.btn_home = QPushButton("⌂")
        self.btn_home.setFixedSize(34, 34)
        self.btn_home.clicked.connect(self._go_home)
        tb.addWidget(self.btn_home)

        lbl = QLabel("MoodSync"); lbl.setObjectName("title_label")
        tb.addWidget(lbl)

        # WebView
        page = QWebEnginePage(self._profile, self)
        self.wv = QWebEngineView()
        self.wv.setPage(page)
        layout.addWidget(self.wv)

        # Status bar
        self.status = QStatusBar(); self.setStatusBar(self.status)

        # Connexions
        self.wv.urlChanged.connect(self._url_changed)
        self.wv.titleChanged.connect(self._title_changed)
        self.wv.loadStarted.connect(lambda: self.status.showMessage("Chargement..."))
        self.wv.loadFinished.connect(self._load_finished)
        self.wv.loadProgress.connect(
            lambda p: self.status.showMessage(f"Chargement {p}%") if p < 100 else None)

        self.wv.load(QUrl(HOME_URL))

    def _go_back(self):   self.wv.back()
    def _go_fwd(self):    self.wv.forward()
    def _reload(self):    self.wv.reload()
    def _go_home(self):   self.wv.load(QUrl(HOME_URL))

    def _nav_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.wv.load(QUrl(url))

    def _url_changed(self, url):
        self.url_bar.setText(url.toString())
        self.btn_back.setEnabled(self.wv.history().canGoBack())
        self.btn_fwd.setEnabled(self.wv.history().canGoForward())

    def _title_changed(self, title):
        self.setWindowTitle(f"{title} — MoodSync" if title else "MoodSync")

    def _load_finished(self, ok):
        self.status.showMessage("Prêt" if ok else "Erreur de chargement", 3000)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MoodSync")
    app.setFont(QFont("Segoe UI", 10))

    # Palette sombre
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,     QColor("#161619"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#c8c4e8"))
    pal.setColor(QPalette.ColorRole.Base,       QColor("#1e1e28"))
    pal.setColor(QPalette.ColorRole.Text,       QColor("#c8c4e8"))
    app.setPalette(pal)

    win = BrowserWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
