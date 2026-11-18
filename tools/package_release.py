"""Package the exact tested Asterion novel V2; exclude keys and toolchains."""
from pathlib import Path
import hashlib
import io
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/'release'
BASE='asterion. elf beauties teach me all about Machine Learning. V2'
APK=RELEASE/(BASE+'.apk')
SOURCE=RELEASE/(BASE+' — source.zip')
DOCS=('ASSETS.md','CURRICULUM.md','EMULATOR_COMPATIBILITY.md','PYTHON.md',
      'SOURCES.md','TEST_REPORT.md','MOBILE_PYTHON_TEACHING.md','mobile_curriculum_review.md',
      'MOBILE_UI_V2.md','ANDROID_V2_QA.md')
TESTS=('browser_runtime.py','browser_novel_route.py','browser_novel_ui.py',
       'browser_native_adapter.py','browser_android.py','browser_android_cdp.py')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def source_files():
    for name in ('README_RU.md','android/AndroidManifest.xml','android/README.md'):
        yield ROOT/name
    for directory in ('web','android/src','android/res','android/runtime','tools'):
        for path in sorted((ROOT/directory).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc':yield path
    for name in DOCS:
        path=ROOT/'docs'/name
        if path.exists():yield path
    for path in sorted((ROOT/'tests').iterdir()):
        if path.is_file() and (path.name in TESTS or path.name.startswith(('test_','android_v2_'))):yield path
    for path in sorted((ROOT/'artifacts').iterdir()):
        # Only final reports and explicitly current-edition images enter delivery.
        if path.is_file() and path.suffix in ('.json','.png','.log'):
            if any(word in path.name for word in ('interim','debug','failure','initial')):continue
            if path.name in {'v2-code-mobile.png','v2-story-desktop.png','v2-story-mobile.png','v2-welcome-desktop.png'}:continue
            if path.name.startswith(('v2-','android-v2-','android-signature','android-build','mobile-','unit-','emulator-cpu-','emulator-horizontal-')):yield path

def main():
    campaign=json.loads((ROOT/'web/data/campaign.json').read_text())
    exercises=json.loads((ROOT/'web/python/exercises.json').read_text())
    assert len(campaign['levels'])==100 and len(exercises['exercises'])==40
    assert all(l.get('teaching') and l.get('mandatoryCombat') is False for l in campaign['levels'])
    assert all(e.get('teaching') for e in exercises['exercises'])
    unit=json.loads((ROOT/'artifacts/unit-tests.json').read_text())
    assert unit['passed']
    for name,expected in unit['sha256'].items():assert sha(ROOT/name)==expected,name
    build=json.loads((ROOT/'artifacts/android-build.json').read_text())
    assert build['sha256']==sha(APK)
    assert build['campaignLevels']==100 and build['pythonExercises']==40
    assert build['pythonBackend']=='native process'
    with zipfile.ZipFile(APK) as apk:
        for path in (ROOT/'web').rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc':
                assert apk.read('assets/web/'+path.relative_to(ROOT/'web').as_posix())==path.read_bytes(),f'Rebuild APK: changed asset {path}'
        assert apk.getinfo('assets/chaquopy/app.imy').compress_type==zipfile.ZIP_STORED
        with zipfile.ZipFile(io.BytesIO(apk.read('assets/chaquopy/app.imy'))) as app:
            for name in ('native_runner.py','validator.py'):
                assert app.read(name)==(ROOT/'web/python'/name).read_bytes()
        for abi in ('arm64-v8a','x86_64'):
            assert apk.getinfo(f'lib/{abi}/libpython3.12.so').file_size>0
    for name in ('v2-browser-route.json','v2-browser-ui.json','android-v2-qa.json',
                 'android-v2-keyboard.json','android-v2-storage.json'):
        report=json.loads((ROOT/'artifacts'/name).read_text())
        assert report.get('passed') is True,f'Failing/missing verification: {name}'
        if name=='v2-browser-route.json':
            assert report.get('curriculumFinal') is True
            assert report['campaignSha256']==sha(ROOT/'web/data/campaign.json')
            assert report['appJsSha256']==sha(ROOT/'web/js/app.js')
        if name.startswith('android-'):assert report['apkSha256']==sha(APK),name
        if name=='android-v2-qa.json':
            assert len(report['solutions'])==40
            assert all(r['practice']==r['transfer']=='passed' for r in report['solutions'])
    signature=json.loads((ROOT/'artifacts/android-signature.json').read_text())
    assert signature['verified'] and signature['sha256']==sha(APK)
    paths=sorted(set(source_files()))
    manifests={}
    with zipfile.ZipFile(SOURCE,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in paths:
            assert path.suffix.lower() not in {'.jks','.keystore','.pem','.p12'}
            name=path.relative_to(ROOT).as_posix()
            manifests[name]=sha(path)
            archive.write(path,BASE+'/'+name)
        archive.writestr(BASE+'/MANIFEST.json',json.dumps(manifests,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(SOURCE) as archive:assert archive.testzip() is None
    manifest={'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in (APK,SOURCE)]}
    (RELEASE/'SHA256SUMS.txt').write_text(''.join(f"{item['sha256']}  {item['name']}\n" for item in manifest['files']))
    (RELEASE/'release-manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
