[app]
title           = MoodSync Browser
package.name    = moodsyncbrowser
package.domain  = net.alwaysdata.moodsync
source.dir      = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json
version         = 2.0
source.main     = main.py

requirements = python3,kivy==2.3.1,android,pyjnius

android.permissions = \
    INTERNET,\
    ACCESS_NETWORK_STATE,\
    ACCESS_WIFI_STATE,\
    CAMERA,\
    RECORD_AUDIO,\
    READ_EXTERNAL_STORAGE,\
    WRITE_EXTERNAL_STORAGE

android.api             = 33
android.minapi          = 26
android.ndk             = 25b
android.ndk_api         = 21
android.sdk             = 33
android.accept_sdk_license = True
android.archs           = arm64-v8a, armeabi-v7a
android.entrypoint      = org.kivy.android.PythonActivity
android.apptheme        = @android:style/Theme.NoTitleBar
orientation             = portrait
presplash.color         = #161619
p4a.branch              = develop

[buildozer]
log_level    = 2
warn_on_root = 1