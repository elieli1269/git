"""
MoodSync Browser — Android App
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty

HOME_URL    = "https://moodsync.alwaysdata.net"
LOGIN_URL   = "https://moodsync.alwaysdata.net/login.php"
PROFILE_URL = "https://moodsync.alwaysdata.net/profile.php"

MS_BG       = (0.086, 0.086, 0.102, 1)
MS_SURFACE  = (0.122, 0.122, 0.149, 1)
MS_TOOLBAR  = (0.102, 0.102, 0.122, 1)
MS_ACCENT   = (0.655, 0.545, 0.988, 1)
MS_ACCENT2  = (0.541, 0.361, 0.988, 1)
MS_TEXT     = (0.910, 0.902, 0.941, 1)
MS_TEXT_DIM = (0.533, 0.502, 0.627, 1)
MS_GREEN    = (0.506, 0.788, 0.584, 1)
MS_RED      = (0.949, 0.545, 0.510, 1)

if platform == "android":
    from android.runnable import run_on_ui_thread
    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    WebView        = autoclass("android.webkit.WebView")
    WebViewClient  = autoclass("android.webkit.WebViewClient")
    CookieManager  = autoclass("android.webkit.CookieManager")
    LayoutParams   = autoclass("android.view.ViewGroup$LayoutParams")
    Color_java     = autoclass("android.graphics.Color")

    class AndroidWebView(Widget):
        url            = StringProperty(HOME_URL)
        can_go_back_v  = BooleanProperty(False)
        can_go_fwd_v   = BooleanProperty(False)
        page_title     = StringProperty("MoodSync")
        current_url    = StringProperty(HOME_URL)
        on_title_cb    = None
        on_url_cb      = None

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self._wv = None
            Clock.schedule_once(self._create, 0)
            self.bind(pos=self._update, size=self._update)

        @run_on_ui_thread
        def _create(self, *a):
            activity = PythonActivity.mActivity
            cm = CookieManager.getInstance()
            cm.setAcceptCookie(True)

            self._wv = WebView(activity)
            s = self._wv.getSettings()
            s.setJavaScriptEnabled(True)
            s.setDomStorageEnabled(True)
            s.setLoadWithOverviewMode(True)
            s.setUseWideViewPort(True)
            s.setBuiltInZoomControls(True)
            s.setDisplayZoomControls(False)
            s.setMediaPlaybackRequiresUserGesture(False)
            ua = s.getUserAgentString()
            s.setUserAgentString(ua + " MoodSyncApp/2.0")

            wv_ref = self

            class MSClient(WebViewClient):
                def onPageStarted(this, wv, url, fav):
                    wv_ref.current_url = url or ""
                    if wv_ref.on_url_cb:
                        Clock.schedule_once(lambda dt: wv_ref.on_url_cb(url), 0)

                def onPageFinished(this, wv, url):
                    wv_ref.current_url    = url or ""
                    wv_ref.can_go_back_v  = wv.canGoBack()
                    wv_ref.can_go_fwd_v   = wv.canGoForward()
                    t = wv.getTitle()
                    if t:
                        wv_ref.page_title = t
                        if wv_ref.on_title_cb:
                            Clock.schedule_once(lambda dt: wv_ref.on_title_cb(t), 0)
                    wv.evaluateJavascript("""
                        (function(){
                            var m = document.querySelector('meta[name="username"]');
                            if(m && m.content) return m.content;
                            var u = document.querySelector('[data-username]');
                            if(u) return u.getAttribute('data-username');
                            return '';
                        })()
                    """, None)

                def shouldOverrideUrlLoading(this, wv, url):
                    return False

            self._wv.setWebViewClient(MSClient())
            self._wv.setBackgroundColor(Color_java.parseColor("#161619"))
            activity.addContentView(self._wv, LayoutParams(
                LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT
            ))
            self._wv.loadUrl(HOME_URL)
            Clock.schedule_once(self._update, 0.1)

        @run_on_ui_thread
        def _update(self, *a):
            if not self._wv:
                return
            from kivy.core.window import Window as W
            self._wv.setX(int(self.x))
            self._wv.setY(int(W.height - self.y - self.height))
            lp = self._wv.getLayoutParams()
            lp.width  = int(self.width)
            lp.height = int(self.height)
            self._wv.setLayoutParams(lp)
            self._wv.requestLayout()

        @run_on_ui_thread
        def load_url(self, url):
            if self._wv:
                if not url.startswith("http"):
                    url = "https://www.google.com/search?q=" + url
                self._wv.loadUrl(url)

        @run_on_ui_thread
        def go_back(self):
            if self._wv and self._wv.canGoBack():
                self._wv.goBack()

        @run_on_ui_thread
        def go_forward(self):
            if self._wv and self._wv.canGoForward():
                self._wv.goForward()

        @run_on_ui_thread
        def reload(self):
            if self._wv:
                self._wv.reload()

        @run_on_ui_thread
        def clear_cookies(self):
            CookieManager.getInstance().removeAllCookies(None)

else:
    class AndroidWebView(Widget):
        url           = StringProperty(HOME_URL)
        can_go_back_v = BooleanProperty(False)
        can_go_fwd_v  = BooleanProperty(False)
        page_title    = StringProperty("MoodSync")
        current_url   = StringProperty(HOME_URL)
        on_title_cb   = None
        on_url_cb     = None
        def load_url(self, url): pass
        def go_back(self): pass
        def go_forward(self): pass
        def reload(self): pass
        def clear_cookies(self): pass


class AvatarWidget(Button):
    def __init__(self, **kwargs):
        super().__init__(text="?", **kwargs)
        self._av_color = MS_TEXT_DIM
        self.background_normal = ""
        self.background_color  = (0, 0, 0, 0)
        self.color             = (1, 1, 1, 1)
        self.font_size         = sp(13)
        self.bold              = True
        self.bind(pos=self._draw, size=self._draw)

    def set_user(self, name):
        parts = name.strip().split()
        self.text      = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
        self._av_color = MS_ACCENT
        self._draw()

    def set_logged_out(self):
        self.text      = "?"
        self._av_color = MS_TEXT_DIM
        self._draw()

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._av_color)
            Ellipse(pos=self.pos, size=self.size)


class BrowserToolbar(BoxLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.app         = app_ref
        self.size_hint_y = None
        self.height      = dp(100)
        self._build()

    def _build(self):
        with self.canvas.before:
            Color(*MS_TOOLBAR)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *a: setattr(self._bg, 'pos', self.pos),
                  size=lambda *a: setattr(self._bg, 'size', self.size))

        # Ligne 1 : nav + urlbar + avatar
        row1 = BoxLayout(size_hint_y=None, height=dp(52),
                         padding=[dp(6), dp(6)], spacing=dp(2))

        self.btn_back  = self._ibtn("‹", self.app.go_back)
        self.btn_fwd   = self._ibtn("›", self.app.go_forward)
        self.btn_reload= self._ibtn("↻", self.app.reload_page)
        row1.add_widget(self.btn_back)
        row1.add_widget(self.btn_fwd)
        row1.add_widget(self.btn_reload)

        # URL wrap
        url_wrap = FloatLayout(size_hint_x=1)
        with url_wrap.canvas.before:
            Color(*MS_SURFACE)
            self._url_bg = RoundedRectangle(
                pos=url_wrap.pos, size=url_wrap.size, radius=[dp(18)])
        url_wrap.bind(
            pos =lambda *a: setattr(self._url_bg, 'pos',  url_wrap.pos),
            size=lambda *a: setattr(self._url_bg, 'size', url_wrap.size))

        self.urlbar = TextInput(
            text=HOME_URL, multiline=False,
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0},
            background_color=(0,0,0,0),
            foreground_color=MS_TEXT,
            cursor_color=MS_ACCENT,
            font_size=sp(13),
            padding=[dp(12), dp(10)],
            hint_text="URL ou recherche",
            hint_text_color=MS_TEXT_DIM,
        )
        self.urlbar.bind(on_text_validate=lambda *a: self.app.navigate())
        url_wrap.add_widget(self.urlbar)
        row1.add_widget(url_wrap)

        self.avatar = AvatarWidget(size_hint=(None,None), size=(dp(34),dp(34)))
        self.avatar.bind(on_press=lambda *a: self.app.toggle_account_panel())
        row1.add_widget(self.avatar)
        self.add_widget(row1)

        # Ligne 2 : titre + statut
        row2 = BoxLayout(size_hint_y=None, height=dp(22),
                         padding=[dp(12), 0])
        self.title_lbl = Label(text="MoodSync", color=MS_TEXT_DIM,
                               font_size=sp(11), halign="left", valign="middle")
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        row2.add_widget(self.title_lbl)

        self.conn_lbl = Label(text="Non connecté", color=MS_TEXT_DIM,
                              font_size=sp(11), size_hint_x=None,
                              width=dp(120), halign="right")
        row2.add_widget(self.conn_lbl)
        self.add_widget(row2)

        # Ligne 3 : progress
        self.progress = Widget(size_hint_y=None, height=dp(3))
        self._prog_val = 0
        self.add_widget(self.progress)

    def _ibtn(self, txt, fn):
        b = Button(text=txt, size_hint=(None,None), size=(dp(40),dp(40)),
                   font_size=sp(20), background_normal="",
                   background_color=(0,0,0,0), color=MS_TEXT_DIM)
        b.bind(on_press=lambda *a: fn())
        return b

    def set_title(self, t):   self.title_lbl.text = t
    def set_url(self, u):
        if not self.urlbar.focus: self.urlbar.text = u

    def set_logged_in(self, name):
        self.avatar.set_user(name)
        self.conn_lbl.text  = f"● {name}"
        self.conn_lbl.color = MS_GREEN

    def set_logged_out(self):
        self.avatar.set_logged_out()
        self.conn_lbl.text  = "Non connecté"
        self.conn_lbl.color = MS_TEXT_DIM


class AccountPanel(FloatLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app      = app_ref
        self._visible = False
        self.opacity  = 0
        self.size_hint= (None, None)
        self.size     = (dp(260), dp(260))
        self._build()

    def _build(self):
        with self.canvas.before:
            Color(0.18, 0.18, 0.22, 0.97)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos =lambda *a: setattr(self._bg,'pos', self.pos),
                  size=lambda *a: setattr(self._bg,'size',self.size))

        lay = BoxLayout(orientation="vertical", padding=dp(16),
                        spacing=dp(8), size_hint=(1,1))

        self.lbl_title = Label(text="🎵  MoodSync", font_size=sp(17),
                               bold=True, color=MS_ACCENT,
                               size_hint_y=None, height=dp(32))
        lay.add_widget(self.lbl_title)

        self.lbl_user = Label(text="Non connecté", font_size=sp(12),
                              color=MS_TEXT_DIM, size_hint_y=None, height=dp(22))
        lay.add_widget(self.lbl_user)

        self.btn_login = self._btn("Se connecter", MS_ACCENT, self.app.do_login)
        lay.add_widget(self.btn_login)

        self.btn_profile = self._btn("👤  Mon profil", MS_SURFACE, self.app.open_profile)
        self.btn_profile.opacity  = 0
        self.btn_profile.disabled = True
        lay.add_widget(self.btn_profile)

        self.btn_logout = self._btn("🚪  Déconnexion", (0.3,0.1,0.1,1), self.app.do_logout)
        self.btn_logout.opacity  = 0
        self.btn_logout.disabled = True
        lay.add_widget(self.btn_logout)

        btn_close = Button(text="✕ Fermer", size_hint_y=None, height=dp(34),
                           background_normal="", background_color=(0,0,0,0),
                           color=MS_TEXT_DIM, font_size=sp(12))
        btn_close.bind(on_press=lambda *a: self.hide())
        lay.add_widget(btn_close)
        lay.add_widget(Widget())
        self.add_widget(lay)

    def _btn(self, txt, col, fn):
        b = Button(text=txt, size_hint_y=None, height=dp(40),
                   background_normal="", background_color=col,
                   color=(1,1,1,1), font_size=sp(13))
        b.bind(on_press=lambda *a: (fn(), self.hide()))
        return b

    def show_logged_in(self, name):
        self.lbl_user.text        = f"👤  {name}"
        self.lbl_user.color       = MS_TEXT
        self.btn_login.opacity    = 0
        self.btn_login.disabled   = True
        self.btn_profile.opacity  = 1
        self.btn_profile.disabled = False
        self.btn_logout.opacity   = 1
        self.btn_logout.disabled  = False
        self._show()

    def show_logged_out(self):
        self.lbl_user.text        = "Non connecté"
        self.lbl_user.color       = MS_TEXT_DIM
        self.btn_login.opacity    = 1
        self.btn_login.disabled   = False
        self.btn_profile.opacity  = 0
        self.btn_profile.disabled = True
        self.btn_logout.opacity   = 0
        self.btn_logout.disabled  = True
        self._show()

    def _show(self):
        self._visible = True
        self.opacity  = 1

    def hide(self):
        self._visible = False
        self.opacity  = 0

    def toggle(self, logged_in, name=""):
        if self._visible:
            self.hide()
        elif logged_in:
            self.show_logged_in(name)
        else:
            self.show_logged_out()


class BrowserLayout(FloatLayout):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self._app = app_ref

        self.webview = AndroidWebView(size_hint=(1,1), pos_hint={"x":0,"y":0})
        self.webview.on_title_cb = lambda t: self.toolbar.set_title(t)
        self.webview.on_url_cb   = lambda u: self.toolbar.set_url(u)
        self.add_widget(self.webview)

        self.toolbar = BrowserToolbar(app_ref, size_hint=(1,None),
                                      pos_hint={"x":0,"top":1})
        self.add_widget(self.toolbar)
        self.toolbar.bind(height=self._adjust)
        Clock.schedule_once(self._adjust, 0.2)

        self.panel = AccountPanel(app_ref)
        self.add_widget(self.panel)
        Clock.schedule_once(self._pos_panel, 0.3)

    def _adjust(self, *a):
        th = self.toolbar.height
        h  = self.height - th
        if h > 0:
            self.webview.size_hint = (1, None)
            self.webview.height    = h
            self.webview.y         = 0

    def _pos_panel(self, *a):
        self.panel.pos = (
            self.width - self.panel.width - dp(8),
            self.height - self.toolbar.height - self.panel.height - dp(4)
        )

    def on_size(self, *a):
        self._adjust()
        self._pos_panel()


class MoodSyncApp(App):
    def build(self):
        Window.clearcolor = MS_BG
        if platform == "android":
            Window.fullscreen = True
        self._user = {"logged_in": False, "name": ""}
        self.layout = BrowserLayout(self)
        return self.layout

    def navigate(self):
        url = self.layout.toolbar.urlbar.text.strip()
        if not url: return
        if not url.startswith("http"):
            url = ("https://" + url) if ("." in url and " " not in url) \
                  else "https://www.google.com/search?q=" + url
        self.layout.webview.load_url(url)
        self.layout.toolbar.urlbar.focus = False

    def go_back(self):       self.layout.webview.go_back()
    def go_forward(self):    self.layout.webview.go_forward()
    def reload_page(self):   self.layout.webview.reload()

    def toggle_account_panel(self):
        self.layout.panel.toggle(self._user["logged_in"], self._user.get("name",""))

    def do_login(self):
        self.layout.webview.load_url(LOGIN_URL)

    def do_logout(self):
        self._user = {"logged_in": False, "name": ""}
        self.layout.toolbar.set_logged_out()
        self.layout.webview.clear_cookies()
        self.layout.webview.load_url(HOME_URL)

    def open_profile(self):
        self.layout.webview.load_url(PROFILE_URL)

    def set_logged_in(self, name):
        if name and name != self._user.get("name"):
            self._user = {"logged_in": True, "name": name}
            self.layout.toolbar.set_logged_in(name)

    def on_start(self):
        if platform == "android":
            from android import activity
            activity.bind(on_key_down=self._key_down)

    def _key_down(self, keycode, *a):
        if keycode == 27:
            self.go_back()
            return True
        return False


if __name__ == "__main__":
    MoodSyncApp().run()