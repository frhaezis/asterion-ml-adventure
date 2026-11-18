"""Verify and stage the vendored, offline Chaquopy/CPython Android runtime.

The build imports stage_native_python(BUILD), or runs this file with --build-dir.
No Gradle, pip, network, account, or native compiler is needed. Java compilation
and D8 must both include the returned jars. Add lib_dir contents to APK lib/.
Keep every assets/chaquopy/*.imy file uncompressed in the final APK.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "android/runtime"


def _digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def _write_zip(destination, files):
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (1980, 2, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)


def stage_native_python(build_dir):
    build = Path(build_dir).resolve()
    metadata = json.loads((RUNTIME / "manifest.json").read_text(encoding="utf-8"))
    for relative, expected in metadata["files"].items():
        path = RUNTIME / relative
        if not path.is_file() or path.stat().st_size != expected["bytes"] or _digest(path) != expected["sha256"]:
            raise RuntimeError("Native Python artifact failed checksum verification: " + str(path))

    assets = build / "assets/chaquopy"
    native = build / "native-python"
    libs = native / "lib"
    for path in (assets, native):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(RUNTIME / metadata["runtimeArchive"]) as archive:
        actual = {info.filename for info in archive.infolist() if not info.is_dir()}
        if actual != set(metadata["archiveEntries"]):
            raise RuntimeError("Native Python archive contains unexpected or missing files")
        for info in archive.infolist():
            if info.is_dir():
                continue
            relative = PurePosixPath(info.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError("Unsafe native runtime path: " + str(relative))
            data = archive.read(info)
            if hashlib.sha256(data).hexdigest() != metadata["archiveEntries"][info.filename]:
                raise RuntimeError("Native Python archive entry failed checksum verification: " + info.filename)
            if info.filename.startswith("assets/chaquopy/"):
                destination = assets / relative.relative_to("assets/chaquopy")
            elif info.filename.startswith("lib/"):
                destination = libs / relative.relative_to("lib")
            else:
                raise RuntimeError("Unexpected native runtime location: " + info.filename)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)

    python_sources = {name: ROOT / "web/python" / name for name in ("native_runner.py", "validator.py")}
    _write_zip(assets / "app.imy", {name: source.read_bytes() for name, source in python_sources.items()})
    asset_hashes = {str(path.relative_to(assets)): hashlib.sha1(path.read_bytes()).hexdigest()
                    for path in sorted(assets.rglob("*")) if path.is_file()}
    (assets / "build.json").write_text(json.dumps({"python_version": "3.12",
        "extract_packages": [], "assets": asset_hashes}, indent=2), encoding="utf-8")

    license_source = RUNTIME / "licenses"
    if not (license_source / "NOTICE.txt").is_file():
        raise RuntimeError("Native Python license notices are missing")
    license_destination = build / "assets/native-python-licenses"
    if license_destination.exists():
        shutil.rmtree(license_destination)
    shutil.copytree(license_source, license_destination)
    shutil.copyfile(RUNTIME / "manifest.json", license_destination / "runtime-manifest.json")
    report = {"pythonVersion": metadata["pythonVersion"], "chaquopyVersion": metadata["chaquopyVersion"],
              "abis": metadata["abis"], "jars": [str(RUNTIME / name) for name in metadata["jars"]],
              "lib_dir": str(libs), "asset_dir": str(assets), "offline": True,
              "runtimeArchiveSha256": metadata["files"][metadata["runtimeArchive"]]["sha256"],
              "pythonSourceSha256": {name: _digest(source) for name, source in python_sources.items()}}
    (build / "native-python.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, required=True)
    options = parser.parse_args()
    print(json.dumps(stage_native_python(options.build_dir), indent=2))
