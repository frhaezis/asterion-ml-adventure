# Asterion · Elf Beauties · V2 — native Android host

This directory hosts the offline game UI in a Java Activity and Android WebView.
Android exercises run in bundled CPython 3.12.15, through the MIT-licensed
Chaquopy 17.2.0 runtime. The browser edition uses its bundled Pyodide worker.
No interpreter download, account, remote website or paid SDK is required.
Packaged UI assets are served through a read-only loopback HTTP server.
The fullscreen host resizes the WebView around the Android keyboard using the
actual occluded area. On Android 15, two measured keyboard cycles changed the
CSS viewport from 480 to 180 pixels and restored it to 480; editor controls
remained reachable by scrolling. Earlier Android versions use a visible-frame
fallback; this compatibility path was reviewed but not device-tested.
No camera, microphone, contacts, notification or accessibility permissions are
requested. The INTERNET permission is used for the loopback transport; external
WebView resources are blocked. Explicit source links may open the system browser.

Build with a free JDK 17 or newer and the official Android SDK command-line tools.
Install the SDK components with Google's `sdkmanager` (accept its license before
installation):

    sdkmanager "platforms;android-35" "build-tools;35.0.0" "platform-tools"

Then build:

    python tools/build_android.py

Set ASTERION_SDK and ASTERION_JDK for different tool locations. Signing material
is generated outside this project in ASTERION_SIGNING_DIR and is never archived.
Use your own signing key for your own releases; Android updates require matching
signatures.

Native saves are in private application files and survive app updates. Uninstalling
the application removes them: export a JSON copy first using Android's document
picker. The previous working save remains as a backup. Invalid imports are rejected.

The native storage envelope contains the exact state JSON string as payload and
its SHA256 checksum. This makes browser/native export compatible without relying
on object-key order. Saved envelope format version is 2. This edition additionally requires
`campaignEdition: "elf-beauties-v2"`. Its files live in the separate `novel-v2`
subdirectory. The previous edition’s save files are retained and are never
automatically counted as completion of the rewritten lessons. The Android
package is unchanged; release versionName is 2.1.0 and versionCode is 3.

Normal launches disable WebView inspection. For developer testing on a device
with authorized adb debugging:

    adb shell am start -n org.asterion.livingprotocol/.MainActivity --ez diagnostics true

The diagnostics flag enables WebView's standard adb inspection and console logs
only when Android's ADB setting is also enabled. Ordinary launches disable it.
No diagnostic server is exposed to the network.

`PythonService` runs in a separate, nonexported `:python` process. Initialization
happens in the background; the code deadline starts after the service reports
execution has begun. Stop, timeout and shutdown terminate that process. The next
run creates a new interpreter. `PythonHost` correlates asynchronous results with
request IDs; drafts and progress remain in the UI process.

This is process separation for execution control, not a hostile-code sandbox:
the service shares the app's Android UID and Chaquopy exposes Java access.
The app requests no broad storage or device-control permissions.

`tools/stage_native_python.py` verifies the vendored runtime hashes, builds a fresh
`app.imy` containing `native_runner.py` and `validator.py`, and stages both ABIs.
The `.imy` archives remain uncompressed in the APK for seekable access; native
libraries are extracted by Android. Official runtime notices are included in
`android/runtime/licenses` and packaged assets. Builds need no runtime downloads.

For the official Android 15 emulator used during verification:

    sdkmanager "emulator" "system-images;android-35;default;x86_64"
    python tools/emulator_start.py
    adb -s emulator-5554 shell getprop sys.boot_completed
    adb -s emulator-5554 install -r "release/asterion. elf beauties teach me all about Machine Learning. V2.apk"
    adb -s emulator-5554 shell am start -n org.asterion.livingprotocol/.MainActivity --ez diagnostics true

The helper deliberately supports software CPU emulation without KVM and stores
its emulator files outside the source directory. First boot can take several
minutes. Software emulation timings do not measure physical phone performance.
For this cloud machine, alias defects in the emulator's horizontal SIMD helpers
required a local emulator repair. The APK and Android System WebView receive no
emulator-specific modifications. See [the evidence and reproduction steps](../docs/EMULATOR_COMPATIBILITY.md)
before using software CPU emulation; hardware accelerated devices do not need
this test environment repair.
The APK contains both `arm64-v8a` and `x86_64` native runtimes. It requires a 64-bit
Android device, Android 8 or newer, and a current Android System WebView.
Its native ELF segments support 16 KB page alignment.
