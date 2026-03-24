#!/usr/bin/env python3
"""
MoodSync Browser v2 — Desktop Windows
Connexion externe + UI premium
"""

import sys, os, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar,
    QLineEdit, QPushButton, QLabel, QStatusBar,
    QVBoxLayout, QHBoxLayout, QSizePolicy, QDialog,
    QFormLayout, QCheckBox, QMessageBox, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineScript
)
from PyQt6.QtCore import QUrl, Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QPixmap, QPainter

HOME_URL  = "https://moodsync.alwaysdata.net"
LOGIN_URL = "https://moodsync.alwaysdata.net/login.php"
CONF_FILE = os.path.join(os.path.expanduser("~"), ".moodsync_browser", "config.json")

# ── Config persistante ────────────────────────────────────────────────────────

def load_conf():
    try:
        if os.path.exists(CONF_FILE):
            return json.loads(open(CONF_FILE).read())
    except: pass
    return {}

def save_conf(d):
    os.makedirs(os.path.dirname(CONF_FILE), exist_ok=True)
    open(CONF_FILE, 'w').write(json.dumps(d))

# ── Style ─────────────────────────────────────────────────────────────────────

STYLE = """
* { font-family: 'Segoe UI', 'SF Pro Display', system-ui; }

QMainWindow {
    background: #0e0e16;
}

/* ── TOOLBAR ── */
QToolBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1a1a28, stop:1 #141420);
    border: none;
    border-bottom: 1px solid #2a2a42;
    padding: 6px 10px;
    spacing: 5px;
}
QToolBar::separator {
    background: #2a2a42;
    width: 1px;
    margin: 4px 2px;
}

/* ── BOUTONS NAV ── */
QPushButton.nav {
    background: transparent;
    color: #7070a0;
    border: none;
    border-radius: 8px;
    padding: 0;
    font-size: 18px;
    font-weight: 300;
}
QPushButton.nav:hover {
    background: rgba(120,90,240,.15);
    color: #c8b8f8;
}
QPushButton.nav:disabled { color: #333348; }
QPushButton.nav:pressed  { background: rgba(120,90,240,.28); }

/* ── URL BAR ── */
QLineEdit#url_bar {
    background: #1a1a2e;
    color: #d0cce8;
    border: 1px solid #2e2e4a;
    border-radius: 10px;
    padding: 6px 14px;
    font-size: 13px;
    selection-background-color: #7c5fe0;
}
QLineEdit#url_bar:focus {
    border-color: #7c5fe0;
    background: #1e1e36;
    color: #fff;
}

/* ── BOUTON CONNEXION ── */
QPushButton#btn_login {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7c5fe0, stop:1 #5b3fc8);
    color: #fff;
    border: none;
    border-radius: 9px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#btn_login:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #9070f0, stop:1 #7050e0);
}
QPushButton#btn_login:pressed {
    background: #5b3fc8;
}

/* ── BOUTON ACCUEIL ── */
QPushButton#btn_home {
    background: rgba(255,255,255,.05);
    color: #8080b0;
    border: 1px solid #2a2a42;
    border-radius: 9px;
    padding: 6px 12px;
    font-size: 13px;
}
QPushButton#btn_home:hover {
    background: rgba(120,90,240,.12);
    color: #c8b8f8;
    border-color: #5040a0;
}

/* ── AVATAR ── */
QPushButton#btn_avatar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #7c5fe0, stop:1 #4a2fb8);
    color: #fff;
    border: 2px solid rgba(150,120,255,.3);
    border-radius: 16px;
    font-size: 13px;
    font-weight: 800;
}
QPushButton#btn_avatar:hover {
    border-color: rgba(200,180,255,.6);
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #9070f8, stop:1 #6040d0);
}

/* ── STATUS BAR ── */
QStatusBar {
    background: #0e0e16;
    color: #404060;
    font-size: 11px;
    border-top: 1px solid #1e1e30;
    padding: 2px 10px;
}
QStatusBar::item { border: none; }

/* ── DIALOG LOGIN ── */
QDialog {
    background: #14141e;
}
QLabel { color: #a0a0c8; font-size: 13px; }
QLabel#dlg_title {
    color: #fff;
    font-size: 20px;
    font-weight: 800;
}
QLabel#dlg_sub {
    color: #6060a0;
    font-size: 12px;
}
QLineEdit.form {
    background: #1e1e30;
    color: #d0cce8;
    border: 1px solid #3030fifty;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
}
QLineEdit.form:focus {
    border-color: #7c5fe0;
    background: #22223a;
}
QPushButton#btn_dlg_ok {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7c5fe0, stop:1 #5b3fc8);
    color: #fff;
    border: none;
    border-radius: 11px;
    padding: 12px;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#btn_dlg_ok:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #9070f8, stop:1 #7050e0);
}
QPushButton#btn_dlg_cancel {
    background: #1e1e30;
    color: #7070a0;
    border: 1px solid #2a2a42;
    border-radius: 11px;
    padding: 12px;
    font-size: 13px;
}
QPushButton#btn_dlg_cancel:hover {
    background: #28283e;
    color: #a0a0c8;
}
QCheckBox { color: #6060a0; font-size: 12px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #3a3a5a;
    border-radius: 4px;
    background: #1e1e30;
}
QCheckBox::indicator:checked {
    background: #7c5fe0;
    border-color: #7c5fe0;
}
"""

# ── Dialog de connexion ───────────────────────────────────────────────────────

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion MoodSync")
        self.setFixedSize(360, 420)
        self.setStyleSheet(STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog |
                            Qt.WindowType.FramelessWindowHint)
        self._username = ""
        self._password = ""
        self._remember = False
        self._build()
        # Charger les identifiants sauvegardés
        conf = load_conf()
        if conf.get("remember"):
            self.inp_user.setText(conf.get("username", ""))
            self.inp_pass.setText(conf.get("password", ""))
            self.chk_rem.setChecked(True)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(14)

        # Logo + titre
        logo_row = QHBoxLayout()
        logo_lbl = QLabel("●")
        logo_lbl.setStyleSheet(
            "color:#7c5fe0;font-size:28px;font-weight:900;")
        title = QLabel("MoodSync")
        title.setObjectName("dlg_title")
        logo_row.addWidget(logo_lbl)
        logo_row.addWidget(title)
        logo_row.addStretch()
        lay.addLayout(logo_row)

        sub = QLabel("Connectez-vous pour continuer")
        sub.setObjectName("dlg_sub")
        lay.addWidget(sub)

        lay.addSpacing(8)

        # Champs
        lbl_u = QLabel("Nom d'utilisateur")
        lbl_u.setStyleSheet("color:#7070a0;font-size:11px;font-weight:700;")
        lay.addWidget(lbl_u)
        self.inp_user = QLineEdit()
        self.inp_user.setProperty("class", "form")
        self.inp_user.setStyleSheet("""
            QLineEdit {
                background:#1e1e30;color:#d0cce8;
                border:1px solid #3030508;border-radius:10px;
                padding:10px 14px;font-size:14px;
            }
            QLineEdit:focus {border-color:#7c5fe0;background:#22223a;}
        """)
        self.inp_user.setPlaceholderText("Votre pseudo...")
        lay.addWidget(self.inp_user)

        lbl_p = QLabel("Mot de passe")
        lbl_p.setStyleSheet("color:#7070a0;font-size:11px;font-weight:700;")
        lay.addWidget(lbl_p)
        self.inp_pass = QLineEdit()
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setStyleSheet("""
            QLineEdit {
                background:#1e1e30;color:#d0cce8;
                border:1px solid #303050;border-radius:10px;
                padding:10px 14px;font-size:14px;
            }
            QLineEdit:focus {border-color:#7c5fe0;background:#22223a;}
        """)
        self.inp_pass.setPlaceholderText("Mot de passe...")
        self.inp_pass.returnPressed.connect(self._ok)
        lay.addWidget(self.inp_pass)

        self.chk_rem = QCheckBox("Se souvenir de moi")
        lay.addWidget(self.chk_rem)

        lay.addSpacing(4)

        # Boutons
        btn_ok = QPushButton("Se connecter →")
        btn_ok.setObjectName("btn_dlg_ok")
        btn_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ok.clicked.connect(self._ok)
        lay.addWidget(btn_ok)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setObjectName("btn_dlg_cancel")
        btn_cancel.clicked.connect(self.reject)
        lay.addWidget(btn_cancel)

        # Drag pour fenêtre sans barre de titre
        self._drag_pos = None

    def _ok(self):
        u = self.inp_user.text().strip()
        p = self.inp_pass.text()
        if not u or not p:
            self.inp_user.setPlaceholderText("⚠ Champ requis")
            return
        self._username = u
        self._password = p
        self._remember = self.chk_rem.isChecked()
        if self._remember:
            save_conf({"username": u, "password": p, "remember": True})
        else:
            save_conf({"remember": False})
        self.accept()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    @property
    def username(self): return self._username
    @property
    def password(self): return self._password

# ── JS d'auto-connexion ───────────────────────────────────────────────────────

def autofill_js(username, password):
    u = username.replace("'", "\\'")
    p = password.replace("'", "\\'")
    return f"""
    (function() {{
        function tryFill() {{
            var u = document.querySelector(
                'input[name="username"],input[name="login"],input[type="text"]');
            var p = document.querySelector(
                'input[name="password"],input[type="password"]');
            if (u && p) {{
                u.value = '{u}';
                p.value = '{p}';
                u.dispatchEvent(new Event('input', {{bubbles:true}}));
                p.dispatchEvent(new Event('input', {{bubbles:true}}));
                var form = p.closest('form');
                if (form) form.submit();
                else {{
                    var btn = document.querySelector(
                        'button[type="submit"],input[type="submit"],.btn-login,.login-btn');
                    if (btn) btn.click();
                }}
            }} else {{
                setTimeout(tryFill, 300);
            }}
        }}
        tryFill();
    }})();
    """

# ── Fenêtre principale ────────────────────────────────────────────────────────

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoodSync")
        self.resize(440, 860)
        self.setMinimumSize(360, 600)
        self.setStyleSheet(STYLE)
        self._username = ""
        self._autofill_pending = None
        self._build()
        self._restore_size()

    def _build(self):
        # Profil WebEngine persistant
        cache_dir = os.path.join(os.path.expanduser("~"), ".moodsync_browser")
        os.makedirs(cache_dir, exist_ok=True)
        self._profile = QWebEngineProfile("MoodSyncProfile", self)
        self._profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self._profile.setPersistentStoragePath(cache_dir)
        self._profile.setCachePath(cache_dir)
        ua = self._profile.httpUserAgent()
        self._profile.setHttpUserAgent(ua + " MoodSyncDesktop/2.0")

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ──
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        def nav_btn(text, tip, fn, obj_name=None):
            b = QPushButton(text)
            b.setObjectName(obj_name or "")
            b.setProperty("class", "nav")
            b.setStyleSheet("""
                QPushButton {
                    background:transparent;color:#6060a0;
                    border:none;border-radius:8px;
                    font-size:20px;font-weight:300;
                }
                QPushButton:hover {
                    background:rgba(120,90,240,.14);color:#c0b0f0;
                }
                QPushButton:disabled { color:#2a2a3a; }
                QPushButton:pressed  { background:rgba(120,90,240,.26); }
            """)
            b.setFixedSize(36, 36)
            b.setToolTip(tip)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(fn)
            return b

        self.btn_back   = nav_btn("‹", "Retour",   self._go_back)
        self.btn_fwd    = nav_btn("›", "Avancer",  self._go_fwd)
        self.btn_reload = nav_btn("↻", "Recharger",self._reload)
        self.btn_back.setEnabled(False)
        self.btn_fwd.setEnabled(False)

        tb.addWidget(self.btn_back)
        tb.addWidget(self.btn_fwd)
        tb.addWidget(self.btn_reload)
        tb.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("url_bar")
        self.url_bar.setPlaceholderText("moodsync.alwaysdata.net")
        self.url_bar.returnPressed.connect(self._nav_url)
        self.url_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.setFixedHeight(34)
        tb.addWidget(self.url_bar)
        tb.addSeparator()

        self.btn_home = QPushButton("⌂  Accueil")
        self.btn_home.setObjectName("btn_home")
        self.btn_home.setFixedHeight(34)
        self.btn_home.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_home.clicked.connect(self._go_home)
        tb.addWidget(self.btn_home)

        self.btn_login = QPushButton("⚡  Connexion")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setFixedHeight(34)
        self.btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_login.clicked.connect(self._show_login)
        tb.addWidget(self.btn_login)

        self.btn_avatar = QPushButton("?")
        self.btn_avatar.setObjectName("btn_avatar")
        self.btn_avatar.setFixedSize(32, 32)
        self.btn_avatar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_avatar.clicked.connect(self._show_login)
        self.btn_avatar.hide()
        tb.addWidget(self.btn_avatar)

        # ── WebView ──
        page = QWebEnginePage(self._profile, self)
        self.wv = QWebEngineView()
        self.wv.setPage(page)
        root.addWidget(self.wv)

        # ── Status bar ──
        self.sb = QStatusBar()
        self.setStatusBar(self.sb)

        # ── Indicateur de chargement ──
        self._load_lbl = QLabel("")
        self._load_lbl.setStyleSheet("color:#5050a0;font-size:11px;")
        self.sb.addPermanentWidget(self._load_lbl)

        # ── Connexions ──
        self.wv.urlChanged.connect(self._url_changed)
        self.wv.titleChanged.connect(self._title_changed)
        self.wv.loadStarted.connect(self._load_start)
        self.wv.loadFinished.connect(self._load_done)
        self.wv.loadProgress.connect(self._load_progress)

        self.wv.load(QUrl(HOME_URL))

    # ── Navigation ────────────────────────────────────────────────────────────

    def _go_back(self):   self.wv.back()
    def _go_fwd(self):    self.wv.forward()
    def _reload(self):    self.wv.reload()
    def _go_home(self):   self.wv.load(QUrl(HOME_URL))

    def _nav_url(self):
        url = self.url_bar.text().strip()
        if "." not in url:
            url = f"https://moodsync.alwaysdata.net/search?q={url}"
        elif not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.wv.load(QUrl(url))

    # ── Callbacks WebEngine ───────────────────────────────────────────────────

    def _url_changed(self, url):
        u = url.toString()
        self.url_bar.setText(u)
        self.btn_back.setEnabled(self.wv.history().canGoBack())
        self.btn_fwd.setEnabled(self.wv.history().canGoForward())
        # Auto-fill si on arrive sur login.php
        if self._autofill_pending and "login" in u.lower():
            u2, p2 = self._autofill_pending
            self._autofill_pending = None
            QTimer.singleShot(600, lambda: self.wv.page().runJavaScript(
                autofill_js(u2, p2)))

    def _title_changed(self, title):
        t = title or "MoodSync"
        self.setWindowTitle(f"{t} — MoodSync")
        # Détecter si connecté via meta username
        self.wv.page().runJavaScript(
            "(function(){"
            "var m=document.querySelector('meta[name=\"username\"]');"
            "return m?m.content:'';"
            "})()",
            self._on_user_detected)

    def _on_user_detected(self, name):
        if name and name != self._username:
            self._username = name
            initials = "".join(p[0].upper() for p in name.split()[:2])
            self.btn_login.hide()
            self.btn_avatar.setText(initials or name[0].upper())
            self.btn_avatar.show()
            self.sb.showMessage(f"● Connecté en tant que {name}", 4000)

    def _load_start(self):
        self.btn_reload.setText("✕")
        self.btn_reload.clicked.disconnect()
        self.btn_reload.clicked.connect(lambda: self.wv.stop())
        self._load_lbl.setText("⟳ Chargement...")

    def _load_progress(self, p):
        if p < 100:
            self._load_lbl.setText(f"⟳ {p}%")

    def _load_done(self, ok):
        self.btn_reload.setText("↻")
        self.btn_reload.clicked.disconnect()
        self.btn_reload.clicked.connect(self._reload)
        self._load_lbl.setText("")
        if not ok:
            self.sb.showMessage("⚠ Erreur de chargement", 3000)

    # ── Connexion ─────────────────────────────────────────────────────────────

    def _show_login(self):
        dlg = LoginDialog(self)
        # Centrer sur la fenêtre principale
        dlg.move(
            self.x() + (self.width()  - dlg.width())  // 2,
            self.y() + (self.height() - dlg.height()) // 2)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._username = dlg.username
            # Naviguer vers login.php et autofill
            self._autofill_pending = (dlg.username, dlg.password)
            cur = self.wv.url().toString()
            if "login" in cur.lower():
                # Déjà sur la page login — injecter directement
                self._autofill_pending = None
                QTimer.singleShot(400, lambda: self.wv.page().runJavaScript(
                    autofill_js(dlg.username, dlg.password)))
            else:
                self.wv.load(QUrl(LOGIN_URL))

    # ── Persistance taille fenêtre ────────────────────────────────────────────

    def _restore_size(self):
        conf = load_conf()
        if "win_w" in conf and "win_h" in conf:
            self.resize(conf["win_w"], conf["win_h"])
        if "win_x" in conf and "win_y" in conf:
            self.move(conf["win_x"], conf["win_y"])

    def closeEvent(self, e):
        conf = load_conf()
        conf.update({
            "win_w": self.width(),
            "win_h": self.height(),
            "win_x": self.x(),
            "win_y": self.y(),
        })
        save_conf(conf)
        super().closeEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F5:
            self._reload()
        elif e.key() == Qt.Key.Key_Escape:
            self.wv.stop()
        elif (e.modifiers() == Qt.KeyboardModifier.ControlModifier
              and e.key() == Qt.Key.Key_L):
            self.url_bar.setFocus()
            self.url_bar.selectAll()
        elif (e.modifiers() == Qt.KeyboardModifier.ControlModifier
              and e.key() == Qt.Key.Key_R):
            self._reload()
        else:
            super().keyPressEvent(e)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Nécessaire pour Qt WebEngine
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS",
                          "--disable-gpu-sandbox")

    app = QApplication(sys.argv)
    app.setApplicationName("MoodSync")
    app.setApplicationDisplayName("MoodSync Browser")
    app.setFont(QFont("Segoe UI", 10))

    # Palette sombre globale
    pal = QPalette()
    dark = {
        QPalette.ColorRole.Window:          "#0e0e16",
        QPalette.ColorRole.WindowText:      "#c8c4e8",
        QPalette.ColorRole.Base:            "#14141e",
        QPalette.ColorRole.AlternateBase:   "#1a1a28",
        QPalette.ColorRole.Text:            "#c8c4e8",
        QPalette.ColorRole.BrightText:      "#ffffff",
        QPalette.ColorRole.Button:          "#1e1e2e",
        QPalette.ColorRole.ButtonText:      "#c8c4e8",
        QPalette.ColorRole.Highlight:       "#7c5fe0",
        QPalette.ColorRole.HighlightedText: "#ffffff",
        QPalette.ColorRole.Link:            "#a080f0",
        QPalette.ColorRole.Midlight:        "#2a2a42",
    }
    for role, color in dark.items():
        pal.setColor(role, QColor(color))
    app.setPalette(pal)

    win = BrowserWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
