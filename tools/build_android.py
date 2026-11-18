"""Build a signed standalone APK from Java and bundled web assets, without Gradle.

Required: Android SDK platform35/build-tools35.0.0, JDK17+, zip utilities supplied by
Python. Set ASTERION_SDK and ASTERION_JDK if your paths differ. The private signing
key lives outside the project, never in the source archive.
"""
from pathlib import Path
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import zipfile
from stage_native_python import stage_native_python

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get("ASTERION_SDK", "/workspace/android-sdk"))
JDK = Path(os.environ.get("ASTERION_JDK", "/workspace/android-tools/jdk"))
TOOLS = SDK / "build-tools" / "35.0.0"
BUILD = ROOT / "android" / "build"
RELEASE = ROOT / "release"
SIGNING = Path(os.environ.get("ASTERION_SIGNING_DIR", "/workspace/android-tools/signing"))
ENV = dict(os.environ, JAVA_HOME=str(JDK), PATH=str(JDK / "bin") + os.pathsep + os.environ.get("PATH", ""))

def run(args):
    subprocess.run([str(a) for a in args], check=True, env=ENV, cwd=ROOT)

for needed in [JDK/"bin/javac", TOOLS/"aapt2", TOOLS/"d8", TOOLS/"apksigner", SDK/"platforms/android-35/android.jar"]:
    if not needed.exists():
        raise SystemExit("Missing build tool: " + str(needed))
if BUILD.exists():
    shutil.rmtree(BUILD)
for directory in (BUILD/"gen", BUILD/"classes", BUILD/"dex", BUILD/"assets", RELEASE, SIGNING, ROOT/"artifacts"):
    directory.mkdir(parents=True, exist_ok=True)
shutil.copytree(ROOT/"web", BUILD/"assets/web", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
native = stage_native_python(BUILD)
native_jars = [Path(path) for path in native["jars"]]
android_jar = SDK / "platforms/android-35/android.jar"
run([TOOLS/"aapt2", "compile", "--dir", ROOT/"android/res", "-o", BUILD/"res.zip"])
run([TOOLS/"aapt2", "link", "-o", BUILD/"resources.apk", "-I", android_jar,
     "--manifest", ROOT/"android/AndroidManifest.xml", "--java", BUILD/"gen",
     "-A", BUILD/"assets", "-0", "imy", "--auto-add-overlay", BUILD/"res.zip"])
sources = sorted((ROOT/"android/src").rglob("*.java")) + sorted((BUILD/"gen").rglob("*.java"))
run([JDK/"bin/javac", "--release", "8", "-encoding", "UTF-8",
     "-classpath", os.pathsep.join(str(path) for path in [android_jar,*native_jars]), "-d", BUILD/"classes", *sources])
run([JDK/"bin/jar", "cf", BUILD/"classes.jar", "-C", BUILD/"classes", "."])
run([TOOLS/"d8", "--lib", android_jar, "--min-api", "26", "--output", BUILD/"dex", BUILD/"classes.jar", *native_jars])
shutil.copy2(BUILD/"resources.apk", BUILD/"unsigned.apk")
with zipfile.ZipFile(BUILD/"unsigned.apk", "a", zipfile.ZIP_DEFLATED) as apk:
    for dex in (BUILD/"dex").glob("*.dex"):
        apk.write(dex, dex.name)
    for library in sorted(Path(native["lib_dir"]).rglob("*.so")):
        apk.write(library, "lib/"+library.relative_to(Path(native["lib_dir"])).as_posix())
run([TOOLS/"zipalign", "-p", "-f", "4", BUILD/"unsigned.apk", BUILD/"aligned.apk"])
password_file = SIGNING/"password.txt"
if not password_file.exists():
    password_file.write_text(secrets.token_urlsafe(32), encoding="utf-8")
    password_file.chmod(0o600)
ENV["ASTERION_SIGN_PASS"] = password_file.read_text(encoding="utf-8").strip()
keystore = SIGNING/"asterion-release.jks"
if not keystore.exists():
    run([JDK/"bin/keytool", "-genkeypair", "-keystore", keystore,
         "-alias", "asterion", "-storepass:env", "ASTERION_SIGN_PASS",
         "-keypass:env", "ASTERION_SIGN_PASS", "-keyalg", "RSA", "-keysize", "3072",
         "-validity", "10000", "-dname", "CN=Asterion Living Protocol, OU=Independent Educational Game"])
    keystore.chmod(0o600)
apk_path = RELEASE/"asterion. elf beauties teach me all about Machine Learning. V2.apk"
run([TOOLS/"apksigner", "sign", "--ks", keystore, "--ks-key-alias", "asterion",
     "--ks-pass", "env:ASTERION_SIGN_PASS", "--key-pass", "env:ASTERION_SIGN_PASS",
     "--out", apk_path, BUILD/"aligned.apk"])
run([TOOLS/"apksigner", "verify", "--verbose", apk_path])
report = {"apk": apk_path.name, "bytes": apk_path.stat().st_size,
          "sha256": hashlib.sha256(apk_path.read_bytes()).hexdigest(),
          "package": "org.asterion.livingprotocol", "version": "2.1.0", "versionCode": 3,
          "minSdk": 26, "targetSdk": 35, "signed": True, "build": "Java + aapt2 + d8",
          "privateKeyIncluded": False}
report.update({"abis":["arm64-v8a","x86_64"],"pythonBackend":"native process",
               "pythonVersion":native["pythonVersion"],"chaquopyVersion":native["chaquopyVersion"]})
asset_digest = hashlib.sha256()
for asset in sorted((BUILD/"assets/web").rglob("*")):
    if asset.is_file():
        asset_digest.update(str(asset.relative_to(BUILD/"assets/web")).encode("utf-8") + b"\0")
        asset_digest.update(asset.read_bytes())
report["webAssetSha256"] = asset_digest.hexdigest()
campaign = BUILD/"assets/web/data/campaign.json"
exercises = BUILD/"assets/web/python/exercises.json"
report["campaignLevels"] = len(json.loads(campaign.read_text())["levels"]) if campaign.exists() else 0
report["pythonExercises"] = len(json.loads(exercises.read_text())["exercises"]) if exercises.exists() else 0
(ROOT/"artifacts/android-build.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
