# Android emulator verification and CPU repair

The CPU repair and probe evidence below were established while preparing the previous release. V2 reuses this already repaired test environment; those probes were not repeated for every content rebuild. The V2 game checks are separate, current reports with the installed APK SHA256.

The Android 15 emulator runs the release APK after a local repair to six faulty
horizontal SIMD instructions in its software CPU. Independent guest probes
confirm correct instruction results and the original WebView snapshot checksum.
The Android image, WebView, snapshot and checksum verification remain unchanged;
the APK contains no emulator-specific modifications.

The game tests and their final results are recorded separately in
`artifacts/android-v2-qa.json` and `docs/TEST_REPORT.md`.

## Cause and evidence

This cloud machine has no KVM device. Official Android Emulator versions
35.6.11, 36.2.12 and 37.3.9 produced an incorrect result for the x86 `PHADDD`
instruction when both operands referred to the same register. The stock helper
wrote the first half of its result before reading the second, aliased input.
That violated the instruction's semantics and broke WebView 124's optimized
Adler32 calculation before any game JavaScript or Python ran. Minimal HTML
reproduced the startup failure independently of the game.

| Independent guest check | Stock software CPU | Repaired software CPU | Reference |
|---|---|---|---|
| PHADDD of `[1,2,3,4]` with itself | `[3,7,10,14]` | `[3,7,3,7]` | `[3,7,3,7]` |
| Actual Chromium SIMD checksum | `b2987c76` | `882b7eae` | `882b7eae` |
| Independent scalar checksum | `882b7eae` | `882b7eae` | `882b7eae` |

The original snapshot header also contains `882b7eae`. Its SHA256 is
`f10aada9cfd5446cb0036ecb879f7262189e0ddeadaaeef33e1b236d49da6d48`.
The renderer's original `SIGTRAP` at `libwebviewchromium.so+0x17971cc`
corresponds exactly to V8's failed startup checksum assertion.

Upstream V8 source matching the system WebView:
https://raw.githubusercontent.com/v8/v8/12.4.254.16/src/snapshot/snapshot.cc

Disabling SSSE3 globally is unsuitable: Android's `/init` itself requires the
SSSE3 `PALIGNR` instruction. The repair preserves all original Android CPU
features and corrects the faulty operation instead. A broader audit found the
same aliasing error in five related instructions: PHADDW, PHADDSW, PHSUBW,
PHSUBD and PHSUBSW. The final test environment repairs all six.

## Repaired test environment

- Official Android 15/API35 AOSP x86_64 image, revision2.
- Fingerprint `Android/sdk_phone64_x86_64/emu64x:15/AE3A.240806.019/12368160:userdebug/test-keys`.
- Android System WebView `124.0.6367.219`, embedded V8 `12.4.254.16`.
- Private copy of Android Emulator `36.2.12`, software CPU, original `android64`
  CPU features, SwiftShader graphics, 1280×720 landscape, density240.
- Only six 32-byte helper regions in each host emulator binary are changed.
  Both input vectors are loaded before the result is stored. The replacement
  uses the host's verified SSSE3 support.
- Each patched binary passed 1,531,422 scalar-reference cases across the six
  repaired instructions plus PSHUFB and PALIGNR. These cover distinct and
  aliased inputs, signed saturation, overflow and all PALIGNR immediates.
- The actual Android guest passed 148,192 instruction cases with zero failures,
  as well as the exact Chromium checksum probe. A supplementary host audit of
  105 other packed SIMD helpers passed 3,118,812 comparisons; this is not an
  exhaustive validation of the emulator's complete instruction set.
- The release APK reached `GAME_PAGE_READY`. Native CPython initializes and
  executes the exercise bank in the installed game.

This repair is needed for this software emulation environment. Installing the
APK on a physical Android phone does not require it. Software emulator timings
are not measurements of phone performance. No SDK or emulator binaries are
included in the source archive.

## Python runtime in the release

The Android release uses CPython 3.12.15 through the free MIT-licensed Chaquopy
17.2 runtime in a separate, killable service process. All interpreter files and
exercises are bundled, so execution needs no network. The browser edition uses
Pyodide 0.26.4. A diagnostic Android WebView/Pyodide trial failed during its
JavaScript-to-Python bootstrap; that failed route is not the shipped Android
backend and its cause was not conclusively established. Native CPython passed
all 80 practice/transfer reference runs in an independent installed Android
probe, followed by the installed game's own UI and exercise checks recorded in
`artifacts/android-v2-qa.json`. Do not infer physical arm64 device testing
from x86_64 emulator results.

## Reproduce the host repair

Use the official Linux emulator archive:
https://dl.google.com/android/repository/emulator-linux_x64-14214601.zip

Archive SHA256:
`55e7ce272dd27413855c81b4629c107a1553d07a2f77fa55a6049fdca22f4221`.

On a Linux x86_64 host with SSSE3, extract it to a separate directory and run:

```sh
python tools/emulator_fix_tcg.py --source /path/to/emulator36 --dest /path/to/emulator36-fixed --manifest /path/to/patch-manifest.json
python tools/emulator_verify_tcg.py --manifest /path/to/patch-manifest.json
ASTERION_EMULATOR_DIR=/path/to/emulator36-fixed python tools/emulator_start.py
```

The patcher checks allowlisted complete binary hashes and the exact original
helper bytes. It refuses unsupported inputs or an existing destination and
leaves the original emulator installation intact. Exact offsets, old/new bytes
and before/after binary hashes are in `artifacts/emulator-cpu-patch.json`.
Host and guest results are in `artifacts/emulator-cpu-host-validation.json`
and `artifacts/emulator-cpu-verification.json`. Captured Android guest stdout
for the 148,192-case instruction probe is in
`artifacts/emulator-horizontal-guest.json`.

## Reproduce the independent guest probes

The source includes the instruction microprobe, not its executable:

```sh
gcc -static -O2 -msse4.1 tools/emulator_probe_simd.c -o /tmp/asterion-simd-probe
adb push /tmp/asterion-simd-probe /data/local/tmp/asterion-simd-probe
adb shell chmod 755 /data/local/tmp/asterion-simd-probe
adb shell /data/local/tmp/asterion-simd-probe
gcc -static -O2 -mssse3 tools/emulator_probe_horizontal.c -o /tmp/asterion-horizontal-probe
adb push /tmp/asterion-horizontal-probe /data/local/tmp/asterion-horizontal-probe
adb shell chmod 755 /data/local/tmp/asterion-horizontal-probe
adb shell /data/local/tmp/asterion-horizontal-probe
```

The exact-checksum probe is generated from the developer's own unmodified
system WebView APK. The generator verifies the known library and snapshot
hashes before extracting the arithmetic function and relocating its constants:

```sh
adb pull /product/app/webview/webview.apk /tmp/webview.apk
python tools/emulator_probe_checksum.py --webview-apk /tmp/webview.apk --output-c /tmp/asterion-checksum.c
gcc -static -O2 /tmp/asterion-checksum.c -o /tmp/asterion-checksum
adb push /tmp/asterion-checksum /data/local/tmp/asterion-checksum
adb shell chmod 755 /data/local/tmp/asterion-checksum
adb shell /data/local/tmp/asterion-checksum
```

The successful guest output is:

```
V8 snapshot bytes=74109 expected=882b7eae scalar=882b7eae exactChromiumSIMD=882b7eae
```

The probe generates no changes to the Android image or the application.
