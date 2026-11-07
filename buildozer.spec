[app]

# (str) Title of your application
title = MobiURL-Guard

# (str) Package name
package.name = mobiurlguard

# (str) Package domain (needed for android/ios packaging)
package.domain = org.cybersecurity.mobiurlguard

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,yaml,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,config/*,models/exported/*,models/manifests/*,src/*

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Note: MobiURL-Guard on-device inference runs pure Python with zero native compilation dependencies!
requirements = python3,kivy,pillow,pyyaml

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Camera only needed if physical QR scanning is used by user
android.permissions = INTERNET,CAMERA

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 26

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = False

# (str) Presplash and icon
# icon.filename = %(source.dir)s/assets/icons/icon.png

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
