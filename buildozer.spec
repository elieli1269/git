[app]
# ── Identité ──────────────────────────────────────────────────────────────────
title           = MoodSync Browser
package.name    = moodsyncbrowser
package.domain  = net.alwaysdata.moodsync
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json
version         = 2.0

# ── Point d'entrée ────────────────────────────────────────────────────────────
source.main      = main.py

# ── Dépendances Python ────────────────────────────────────────────────────────
requirements = python3,kivy==2.3.1,kivymd,android,pyjnius

# ── Permissions Android ───────────────────────────────────────────────────────
android.permissions = \
    INTERNET,\
    ACCESS_NETWORK_STATE,\
    ACCESS_WIFI_STATE,\
    CAMERA,\
    RECORD_AUDIO,\
    READ_EXTERNAL_STORAGE,\
    WRITE_EXTERNAL_STORAGE,\
    DOWNLOAD_WITHOUT_NOTIFICATION

# ── SDK / NDK ─────────────────────────────────────────────────────────────────
android.api             = 33
android.minapi          = 26
android.ndk             = 25b
android.ndk_api         = 21
android.sdk             = 33
android.accept_sdk_license = True

# ── Architectures (arm64 = moderne, armeabi = compatibilité) ──────────────────
android.archs = arm64-v8a, armeabi-v7a

# ── APK type ─────────────────────────────────────────────────────────────────
android.release_artifact = apk
# Pour AAB (Google Play) : android.release_artifact = aab

# ── Features Android ─────────────────────────────────────────────────────────
android.features = \
    android.hardware.touchscreen,\
    android.hardware.wifi

# ── Activité Java ─────────────────────────────────────────────────────────────
android.entrypoint      = org.kivy.android.PythonActivity
android.apptheme        = @android:style/Theme.NoTitleBar

# ── Orientation ───────────────────────────────────────────────────────────────
orientation = portrait

# ── Icône et splash ───────────────────────────────────────────────────────────
# icon.filename         = %(source.dir)s/icon.png
# presplash.filename    = %(source.dir)s/presplash.png
presplash.color         = #161619

# ── Gradle / Java extras ─────────────────────────────────────────────────────
android.gradle_dependencies = \
    com.android.support:appcompat-v7:28.0.0

# Activer le mode hardwareAccelerated pour WebView
android.manifest.intent_filters =

# ── p4a (python-for-android) ──────────────────────────────────────────────────
p4a.branch              = develop

# Garder les fichiers de build pour accélérer les rebuilds
android.skip_update     = False
android.accept_sdk_license = True

[buildozer]
# Niveau de log : 0 = erreurs, 1 = info, 2 = debug
log_level   = 2
warn_on_root= 1
