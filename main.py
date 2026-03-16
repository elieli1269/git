"""
MoodSync Browser — Android App
Navigateur dédié MoodSync avec WebView native Android
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty

# Couleurs MoodSync
MS_BG        = (0.086, 0.086, 0.102, 1)    # #161619
MS_SURFACE   = (0.122, 0.122, 0.149, 1)    # #1f1f26
MS_TOOLBAR   = (0.102, 0.102, 0.122, 1)    # #1a1a1f
MS_ACCENT    = (0.655, 0.545, 0.988, 1)    # #a78bfa
MS_ACCENT2   = (0.541, 0.361, 0.988, 1)    # #8a5cfc
MS_TEXT      = (0.910, 0.902, 0.941, 1)    # #e8e6f0
MS_TEXT_DIM  = (0.533, 0.502, 0.627, 1)    # #888080
MS_GREEN     = (0.506, 0.788, 0.584, 1)    # #81c995
MS_RED       = (0.949, 0.545, 0.510, 1)    # #f28b82
MS_BAR       = (0.118, 0.118, 0.141, 1)    # #1e1e24

HOME_URL     = "https://moodsync.alwaysdata.net"
LOGIN_URL    = "https://moodsync.alwaysdata.net/login.php"
PROFILE_URL  = "https://moodsync.alwaysdata.net/profile.php"


# ─── WebView Android ─────────────────────────────────────────────────────────

if platform == "android":
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast

    # Classes Java
    PythonActivity   = autoclass("org.kivy.android.PythonActivity")
    WebView          = autoclass("android.webkit.WebView")
    WebViewClient    = autoclass("android.webkit.WebViewClient")
    WebSettings      = autoclass("android.webkit.WebSettings")
    CookieManager    = autoclass("android.webkit.CookieManager")
    FrameLayout      = autoclass("android.widget.FrameLayout")
    ViewGroup        = autoclass("android.view.ViewGroup")
    LayoutParams     = autoclass("android.view.ViewGroup$LayoutParams")
    LinearLayout     = autoclass("android.widget.LinearLayout")
    View             = autoclass("android.view.View")
    Color_java       = autoclass("android.graphics.Color")
    String           = autoclass("java.lang.String")

    class AndroidWebView(Widget):
        url = StringProperty(HOME_URL)
        can_go_back_val    = BooleanProperty(False)
        can_go_forward_val = BooleanProperty(False)
        page_title         = StringProperty("MoodSync")
        current_url        = StringProperty(HOME_URL)
        on_title_change    = None
        on_url_change      = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self._webview = None
            self._container = None
            Clock.schedule_once(self._create_webview, 0)
            self.bind(pos=self._update_layout, size=self._update_layout)

        @run_on_ui_thread
        def _create_webview(self, *args):
            activity = PythonActivity.mActivity

            # Activer les cookies
            cm = CookieManager.getInstance()
            cm.setAcceptCookie(True)
            cm.setAcceptThirdPartyCookies  # Android 5+

            self._webview = WebView(activity)
            settings = self._webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setLoadWithOverviewMode(True)
            settings.setUseWideViewPort(True)
            settings.setBuiltInZoomControls(True)
            settings.setDisplayZoomControls(False)
            settings.setSupportMultipleWindows(False)
            settings.setMixedContentMode(0)  # MIXED_CONTENT_ALWAYS_ALLOW
            settings.setMediaPlaybackRequiresUserGesture(False)

            # User agent MoodSync
            ua = settings.getUserAgentString()
            settings.setUserAgentString(ua + " MoodSyncApp/2.0")

            # WebViewClient personnalisé
            class MSWebViewClient(WebViewClient):
                def __init__(this):
                    super().__init__()

                def onPageStarted(this, wv, url, favicon):
                    self.current_url = url or ""
                    if self.on_url_change:
                        Clock.schedule_once(lambda dt: self.on_url_change(url), 0)

                def onPageFinished(this, wv, url):
                    self.current_url = url or ""
                    self.can_go_back_val    = wv.canGoBack()
                    self.can_go_forward_val = wv.canGoForward()
                    # Récupérer le titre
                    t = wv.getTitle()
                    if t:
                        self.page_title = t
                        if self.on_title_change:
                            Clock.schedule_once(lambda dt: self.on_title_change(t), 0)
                    # Détecter connexion via JS
                    js = """
                    (function(){
                        var m = document.querySelector('meta[name="username"],meta[name="user-name"]');
                        if(m && m.content) return m.content;
                        var u = document.querySelector('.navbar-username,[data-username],[class*="username"]');
                        if(u && u.textContent.trim()) return u.textContent.trim();
                        return '';
                    })()
                    """
                    wv.evaluateJavascript(js, None)

                def shouldOverrideUrlLoading(this, wv, url):
                    return False  # Tout charger dans le WebView

            self._webview.setWebViewClient(MSWebViewClient())
            self._webview.setBackgroundColor(Color_java.parseColor("#161619"))

            # Ajouter à l'activité
            layout_params = LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT
            )
            activity.addContentView(self._webview, layout_params)
            self._webview.loadUrl(HOME_URL)
            Clock.schedule_once(self._update_layout, 0.1)

        @run_on_ui_thread
        def _update_layout(self, *args):
            if not self._webview:
                return
            from kivy.core.window import Window
            # Convertir coordonnées Kivy → Android
            x  = int(self.x)
            y  = int(Window.height - self.y - self.height)
            w  = int(self.width)
            h  = int(self.height)
            self._webview.setX(x)
            self._webview.setY(y)
            lp = self._webview.getLayoutParams()
            lp.width  = w
            lp.height = h
            self._webview.setLayoutParams(lp)
            self._webview.requestLayout()

        @run_on_ui_thread
        def load_url(self, url: str):
            if self._webview:
                if not url.startswith("http"):
                    url = "https://www.google.com/search?q=" + url
                self._webview.loadUrl(url)

        @run_on_ui_thread
        def go_back(self):
            if self._webview and self._webview.canGoBack():
                self._webview.goBack()
                self.can_go_back_val    = self._webview.canGoBack()
                self.can_go_forward_val = self._webview.canGoForward()

        @run_on_ui_thread
        def go_forward(self):
            if self._webview and self._webview.canGoForward():
                self._webview.goForward()
                self.can_go_back_val    = self._webview.canGoBack()
                self.can_go_forward_val = self._webview.canGoForward()

        @run_on_ui_thread
        def reload(self):
            if self._webview:
                self._webview.reload()

        @run_on_ui_thread
        def clear_cookies(self):
            cm = CookieManager.getInstance()
            cm.removeAllCookies(None)
            cm.flush()

else:
    # ── Fallback desktop (test) ───────────────────────────────────────────────
    try:
        from kivy.garden.webview import WebView as GardenWebView
        class AndroidWebView(GardenWebView):
            pass
    except Exception:
        class AndroidWebView(Widget):
            url = StringProperty(HOME_URL)
            can_go_back_val    = BooleanProperty(False)
            can_go_forward_val = BooleanProperty(False)
            page_title         = StringProperty("MoodSync")
            current_url        = StringProperty(HOME_URL)
            on_title_change    = None
            on_url_change      = None
            def load_url(self, url): self.current_url = url
            def go_back(self): pass
            def go_forward(self): pass
            def reload(self): pass
            def clear_cookies(self): pass
            def on_size(self, *a):
                self.canvas.before.clear()
                with self.canvas.before:
                    Color(*MS_BG)
                    Rectangle(pos=self.pos, size=self.size)
                    Color(*MS_SURFACE)
                    w, h = self.size
                    lbl_w = min(w - dp(40), dp(400))
                    Rectangle(
                        pos=(self.x + (w - lbl_w) / 2, self.y + h / 2 - dp(20)),
                        size=(lbl_w, dp(40))
                    )


# ─── Widgets UI ──────────────────────────────────────────────────────────────

class RoundButton(Button):
    def __init__(self, **kwargs):
        self.bg_color     = kwargs.pop("bg_color",     MS_SURFACE)
        self.hover_color  = kwargs.pop("hover_color",  MS_ACCENT)
        self.radius       = kwargs.pop("radius",        dp(20))
        super().__init__(**kwargs)
        self.background_normal   = ""
        self.background_color    = (0, 0, 0, 0)
        self.color               = MS_TEXT
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

    def on_press(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.hover_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

    def on_release(self):
        self._redraw()


class AvatarWidget(Button):
    """Bouton avatar rond avec initiales"""
    def __init__(self, initials="?", color=MS_ACCENT, **kwargs):
        super().__init__(text=initials, **kwargs)
        self._av_color = color
        self.background_normal = ""
        self.background_color  = (0, 0, 0, 0)
        self.color             = (1, 1, 1, 1)
        self.font_size         = sp(13)
        self.bold              = True
        self.bind(pos=self._draw, size=self._draw)

    def set_user(self, name: str):
        parts = name.strip().split()
        initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
        self.text = initials
        self._av_color = MS_ACCENT
        self._draw()

    def set_logged_out(self):
        self.text = "?"
        self._av_color = MS_TEXT_DIM
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._av_color)
            Ellipse(pos=self.pos, size=self.size)


# ─── Toolbar ─────────────────────────────────────────────────────────────────

class BrowserToolbar(BoxLayout):
    def __init__(self, browser_app, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.size_hint_y = None
        self.height      = dp(112)
        self.app         = browser_app
        self._build()

    def _build(self):
        with self.canvas.before:
            Color(*MS_TOOLBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        # ── Ligne 1 : nav + urlbar + avatar ──────────────────────────────────
        row1 = BoxLayout(orientation="horizontal", size_hint_y=None,
                         height=dp(52), padding=[dp(6), dp(6)])

        # Bouton retour
        self.btn_back = self._icon_btn("‹", self.app.go_back)
        self.btn_back.font_size = sp(22)
        row1.add_widget(self.btn_back)

        # Bouton suivant
        self.btn_fwd = self._icon_btn("›", self.app.go_forward)
        self.btn_fwd.font_size = sp(22)
        row1.add_widget(self.btn_fwd)

        # Bouton reload
        self.btn_reload = self._icon_btn("↻", self.app.reload_page)
        row1.add_widget(self.btn_reload)

        # URL bar
        url_wrap = FloatLayout(size_hint_x=1)
        with url_wrap.canvas.before:
            Color(*MS_SURFACE)
            self._urlbar_bg = RoundedRectangle(
                pos=url_wrap.pos, size=url_wrap.size,
                radius=[dp(18)]
            )
        url_wrap.bind(pos=self._upd_urlbar_bg, size=self._upd_urlbar_bg)
        self._url_wrap = url_wrap

        self.urlbar = TextInput(
            text=HOME_URL,
            multiline=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
            background_color=(0, 0, 0, 0),
            foreground_color=MS_TEXT,
            cursor_color=MS_ACCENT,
            font_size=sp(13),
            padding=[dp(12), dp(10)],
            hint_text="Chercher ou saisir une URL",
            hint_text_color=MS_TEXT_DIM,
        )
        self.urlbar.bind(on_text_validate=self.app.navigate)
        url_wrap.add_widget(self.urlbar)
        row1.add_widget(url_wrap)

        # Avatar
        self.avatar = AvatarWidget(size_hint=(None, None),
                                   size=(dp(34), dp(34)))
        self.avatar.bind(on_press=self.app.toggle_account_panel)
        row1.add_widget(self.avatar)

        self.add_widget(row1)

        # ── Ligne 2 : titre page ─────────────────────────────────────────────
        row2 = BoxLayout(orientation="horizontal", size_hint_y=None,
                         height=dp(24), padding=[dp(12), 0])
        self.title_lbl = Label(
            text="MoodSync",
            color=MS_TEXT_DIM,
            font_size=sp(11),
            halign="left",
            valign="middle",
            size_hint_x=1,
        )
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        row2.add_widget(self.title_lbl)

        # Status connexion
        self.conn_lbl = Label(
            text="Non connecté",
            color=MS_TEXT_DIM,
            font_size=sp(11),
            size_hint_x=None,
            width=dp(120),
            halign="right",
        )
        row2.add_widget(self.conn_lbl)
        self.add_widget(row2)

        # ── Ligne 3 : barre de progression ───────────────────────────────────
        self.progress_bar = Widget(size_hint_y=None, height=dp(3))
        self._progress_val = 0
        self.progress_bar.bind(pos=self._draw_progress, size=self._draw_progress)
        self.add_widget(self.progress_bar)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def _upd_urlbar_bg(self, *a):
        self._urlbar_bg.pos  = self._url_wrap.pos
        self._urlbar_bg.size = self._url_wrap.size

    def _draw_progress(self, *a):
        self.progress_bar.canvas.clear()
        if self._progress_val > 0:
            with self.progress_bar.canvas:
                Color(*MS_ACCENT)
                w = self.progress_bar.width * self._progress_val / 100
                Rectangle(pos=self.progress_bar.pos, size=(w, dp(3)))

    def set_progress(self, val: int):
        self._progress_val = val
        self._draw_progress()

    def set_title(self, title: str):
        self.title_lbl.text = title

    def set_url(self, url: str):
        if not self.urlbar.focus:
            self.urlbar.text = url

    def set_logged_in(self, name: str):
        self.avatar.set_user(name)
        self.conn_lbl.text  = f"● {name}"
        self.conn_lbl.color = MS_GREEN

    def set_logged_out(self):
        self.avatar.set_logged_out()
        self.conn_lbl.text  = "Non connecté"
        self.conn_lbl.color = MS_TEXT_DIM

    def set_back_enabled(self, v: bool):
        self.btn_back.opacity = 1.0 if v else 0.35

    def set_fwd_enabled(self, v: bool):
        self.btn_fwd.opacity = 1.0 if v else 0.35

    def _icon_btn(self, text: str, fn) -> Button:
        btn = Button(
            text=text,
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            font_size=sp(18),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=MS_TEXT_DIM,
        )
        btn.bind(on_press=lambda *a: fn())
        return btn


# ─── Panneau compte ───────────────────────────────────────────────────────────

class AccountPanel(FloatLayout):
    def __init__(self, browser_app, **kwargs):
        super().__init__(**kwargs)
        self.app = browser_app
        self.size_hint = (None, None)
        self.width  = dp(280)
        self.opacity = 0
        self._visible = False
        self._build()

    def _build(self):
        # Fond
        with self.canvas.before:
            Color(0.176, 0.180, 0.192, 0.97)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(14)]
            )
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(10),
            size_hint=(1, 1),
        )

        # Header
        self.header_lbl = Label(
            text="🎵  MoodSync",
            font_size=sp(18),
            bold=True,
            color=MS_ACCENT,
            size_hint_y=None,
            height=dp(36),
        )
        layout.add_widget(self.header_lbl)

        self.user_lbl = Label(
            text="Non connecté",
            font_size=sp(13),
            color=MS_TEXT_DIM,
            size_hint_y=None,
            height=dp(24),
        )
        layout.add_widget(self.user_lbl)

        # Bouton login
        self.btn_login = RoundButton(
            text="Se connecter",
            size_hint_y=None,
            height=dp(44),
            bg_color=MS_ACCENT,
            hover_color=MS_ACCENT2,
            font_size=sp(14),
        )
        self.btn_login.color = (1, 1, 1, 1)
        self.btn_login.bind(on_press=lambda *a: self.app.do_login())
        layout.add_widget(self.btn_login)

        # Bouton profil (caché par défaut)
        self.btn_profile = RoundButton(
            text="👤  Mon profil",
            size_hint_y=None,
            height=dp(40),
            bg_color=MS_SURFACE,
            hover_color=MS_ACCENT,
            font_size=sp(13),
        )
        self.btn_profile.bind(on_press=lambda *a: self.app.open_profile())
        self.btn_profile.opacity = 0
        self.btn_profile.disabled = True
        layout.add_widget(self.btn_profile)

        # Bouton déconnexion (caché par défaut)
        self.btn_logout = RoundButton(
            text="🚪  Se déconnecter",
            size_hint_y=None,
            height=dp(40),
            bg_color=(0.3, 0.1, 0.1, 1),
            hover_color=MS_RED,
            font_size=sp(13),
        )
        self.btn_logout.bind(on_press=lambda *a: self.app.do_logout())
        self.btn_logout.opacity = 0
        self.btn_logout.disabled = True
        layout.add_widget(self.btn_logout)

        # Bouton fermer
        btn_close = Button(
            text="✕  Fermer",
            size_hint_y=None,
            height=dp(36),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=MS_TEXT_DIM,
            font_size=sp(12),
        )
        btn_close.bind(on_press=lambda *a: self.hide())
        layout.add_widget(btn_close)
        layout.add_widget(Widget())  # spacer

        self.add_widget(layout)

    def _upd_bg(self, *a):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def show_logged_in(self, name: str):
        self.user_lbl.text       = f"👤  {name}"
        self.user_lbl.color      = MS_TEXT
        self.btn_login.opacity   = 0
        self.btn_login.disabled  = True
        self.btn_profile.opacity = 1
        self.btn_profile.disabled= False
        self.btn_logout.opacity  = 1
        self.btn_logout.disabled = False
        self.show()

    def show_logged_out(self):
        self.user_lbl.text       = "Non connecté"
        self.user_lbl.color      = MS_TEXT_DIM
        self.btn_login.opacity   = 1
        self.btn_login.disabled  = False
        self.btn_profile.opacity = 0
        self.btn_profile.disabled= True
        self.btn_logout.opacity  = 0
        self.btn_logout.disabled = True
        self.show()

    def show(self):
        self._visible = True
        self.opacity  = 1

    def hide(self):
        self._visible = False
        self.opacity  = 0

    def toggle(self, logged_in: bool, name: str = ""):
        if self._visible:
            self.hide()
        elif logged_in:
            self.show_logged_in(name)
        else:
            self.show_logged_out()


# ─── Layout principal ─────────────────────────────────────────────────────────

class BrowserLayout(FloatLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self._app = app_ref

        # WebView (zone principale)
        self.webview = AndroidWebView(
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        self.webview.on_title_change = self._on_title
        self.webview.on_url_change   = self._on_url
        self.add_widget(self.webview)

        # Toolbar (en haut)
        self.toolbar = BrowserToolbar(
            self._app,
            size_hint=(1, None),
            pos_hint={"x": 0, "top": 1},
        )
        self.add_widget(self.toolbar)

        # Réajuster la webview sous la toolbar
        self.toolbar.bind(height=self._adjust_webview)
        Clock.schedule_once(self._adjust_webview, 0.2)

        # Panneau compte (flottant)
        self.account_panel = AccountPanel(self._app)
        self.account_panel.height = dp(280)
        self.add_widget(self.account_panel)
        Clock.schedule_once(self._position_panel, 0.3)

        # Timer check login
        Clock.schedule_interval(self._tick_login, 5)

    def _adjust_webview(self, *a):
        th = self.toolbar.height
        h  = self.height - th
        if h > 0:
            self.webview.size_hint   = (1, None)
            self.webview.height      = h
            self.webview.pos_hint    = {"x": 0, "y": 0}
            self.webview.y           = 0

    def _position_panel(self, *a):
        self.account_panel.pos = (
            self.width - self.account_panel.width - dp(8),
            self.height - self.toolbar.height - self.account_panel.height - dp(4),
        )

    def on_size(self, *a):
        self._adjust_webview()
        self._position_panel()

    def _on_title(self, title: str):
        self.toolbar.set_title(title)

    def _on_url(self, url: str):
        self.toolbar.set_url(url)

    def _tick_login(self, dt):
        # Sur Android, on tenterait d'évaluer JS ; sur desktop, on skip
        pass


# ─── Application ─────────────────────────────────────────────────────────────

class MoodSyncApp(App):
    def build(self):
        Window.clearcolor = MS_BG

        # Plein écran sur Android
        if platform == "android":
            Window.fullscreen = True

        self._user_info = {"logged_in": False, "name": ""}
        self.layout     = BrowserLayout(self)
        return self.layout

    # ── Actions toolbar ───────────────────────────────────────────────────────

    def navigate(self, instance=None):
        url = self.layout.toolbar.urlbar.text.strip()
        if not url:
            return
        if not url.startswith("http"):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = "https://www.google.com/search?q=" + url
        self.layout.webview.load_url(url)
        self.layout.toolbar.urlbar.focus = False

    def go_back(self):
        self.layout.webview.go_back()

    def go_forward(self):
        self.layout.webview.go_forward()

    def reload_page(self):
        self.layout.webview.reload()

    def toggle_account_panel(self, *a):
        self.layout.account_panel.toggle(
            self._user_info["logged_in"],
            self._user_info.get("name", "")
        )

    def do_login(self):
        self.layout.account_panel.hide()
        self.layout.webview.load_url(LOGIN_URL)

    def do_logout(self):
        self._user_info = {"logged_in": False, "name": ""}
        self.layout.toolbar.set_logged_out()
        self.layout.account_panel.hide()
        self.layout.webview.clear_cookies()
        self.layout.webview.load_url(HOME_URL)

    def open_profile(self):
        self.layout.account_panel.hide()
        self.layout.webview.load_url(PROFILE_URL)

    def set_logged_in(self, name: str):
        if name and name != self._user_info.get("name"):
            self._user_info = {"logged_in": True, "name": name}
            self.layout.toolbar.set_logged_in(name)

    # Touches Android
    def on_start(self):
        if platform == "android":
            from android import activity
            activity.bind(on_key_down=self._key_down)

    def _key_down(self, keycode, *a):
        # Bouton retour Android
        if keycode == 27:
            self.go_back()
            return True
        return False


if __name__ == "__main__":
    MoodSyncApp().run()
