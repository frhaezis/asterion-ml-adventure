"""Start the free official Android API35 x86_64 emulator without KVM.

SDK system image and emulator must already be installed. This launches a local
headless software emulator; it does not run or alter a user's physical phone.
See docs/EMULATOR_COMPATIBILITY.md for the local horizontal-SIMD repairs required by the
tested legacy TCG engine. Set ASTERION_EMULATOR_DIR to that private engine copy.
"""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get("ASTERION_SDK", "/workspace/android-sdk"))
EMULATOR = Path(os.environ.get("ASTERION_EMULATOR_DIR", str(SDK/"emulator")))
STATE = Path(os.environ.get("ASTERION_EMULATOR_STATE", "/workspace/android-tools"))
record = STATE/"emulator-process.json"
if record.exists():
    try:
        previous = json.loads(record.read_text())
        command = Path("/proc")/str(previous["pid"])/"cmdline"
        if "Asterion_API35" in command.read_text():
            print(json.dumps(dict(previous, alreadyRunning=True), indent=2))
            sys.exit(0)
    except (OSError, ValueError, KeyError):
        pass
AVD_ROOT = STATE/"avd"
AVD = AVD_ROOT/"Asterion_API35.avd"
AVD.mkdir(parents=True, exist_ok=True)
(STATE/"user").mkdir(exist_ok=True)
config = {
    "avd.ini.encoding": "UTF-8", "AvdId": "Asterion_API35", "avd.ini.displayname": "Asterion API35 software test",
    "abi.type": "x86_64", "hw.cpu.arch": "x86_64", "hw.cpu.ncore": "2",
    "hw.ramSize": "2048", "hw.lcd.width": "1280", "hw.lcd.height": "720",
    "hw.lcd.density": "240", "hw.initialOrientation": "landscape",
    "hw.gpu.enabled": "yes", "hw.gpu.mode": "swiftshader_indirect",
    "hw.keyboard": "yes", "hw.mainKeys": "no", "hw.audioInput": "no", "hw.audioOutput": "no",
    "hw.battery": "yes", "hw.camera.back": "none", "hw.camera.front": "none",
    "image.sysdir.1": str(SDK/"system-images/android-35/default/x86_64") + "/",
    "disk.dataPartition.size": "4G", "skin.name": "1280x720", "showDeviceFrame": "no",
    "tag.display": "Default", "tag.id": "default", "PlayStore.enabled": "false",
    "fastboot.forceColdBoot": "yes", "fastboot.forceFastBoot": "no",
    "runtime.network.latency": "none", "runtime.network.speed": "full",
}
(AVD/"config.ini").write_text("\n".join(k+"="+v for k,v in config.items())+"\n")
(AVD_ROOT/"Asterion_API35.ini").write_text("avd.ini.encoding=UTF-8\npath="+str(AVD)+"\ntarget=android-35\n")
env=dict(os.environ,ANDROID_HOME=str(SDK),ANDROID_SDK_ROOT=str(SDK),
         ANDROID_AVD_HOME=str(AVD_ROOT),ANDROID_USER_HOME=str(STATE/"user"),ANDROID_I_WANT_MY_TCG="yes")
# Official zip extraction through Python does not retain executable mode bits.
for path in EMULATOR.rglob("*"):
    if path.is_file():
        with path.open("rb") as handle:
            signature=handle.read(4)
        if signature==b"\x7fELF" or path.name in ("emulator","emulator-check","mksdcard"):
            path.chmod(path.stat().st_mode|0o111)
args=[str(EMULATOR/"emulator"),"-avd","Asterion_API35","-port","5554",
      "-no-window","-no-audio","-no-boot-anim","-no-snapshot","-no-metrics","-accel","off",
      "-gpu","swiftshader_indirect","-feature","-Vulkan","-cores","2","-memory","2048","-show-kernel"]
# Keep Android's x86_64 baseline; a generic qemu64 CPU omits required features.
# The override is useful for diagnosing host emulator CPU compatibility.
args += ["-qemu","-cpu",os.environ.get("ASTERION_EMULATOR_CPU","android64")]
with (STATE/"emulator.log").open("ab",buffering=0) as log:
    process=subprocess.Popen(args,env=env,stdout=log,stderr=log,start_new_session=True)
record.write_text(json.dumps({"pid":process.pid,"serial":"emulator-5554","log":str(STATE/"emulator.log")},indent=2))
print(json.dumps({"pid":process.pid,"serial":"emulator-5554","log":str(STATE/"emulator.log")},indent=2))
