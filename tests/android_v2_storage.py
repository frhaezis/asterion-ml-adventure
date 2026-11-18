"""Real DocumentsUI export/import and private save recovery on test emulator.

Only this new V2 test profile and uniquely named test JSON documents are changed.
The previous edition's private save is checked for byte-for-byte preservation.
"""
import copy
import hashlib
import json
import os
import shlex
import tempfile
import time
from android_v2_common import *


def alert_text():
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        message='\n'.join(n.get('text','') for n in ui_nodes() if n.get('resource-id')=='android:id/message')
        if message:return message
        time.sleep(.5)
    raise TimeoutError('Android app alert was not displayed')


def select_document(name):
    # The provider remembers the Downloads folder used by the export. Scroll
    # the real file grid if an older file sorts beyond the visible rows.
    for attempt in range(8):
        tree=ui_dump();nodes=[n.attrib for n in tree.iter('node')]
        wanted=next((n for n in tree.iter('node') if n.get('text')==name),None)
        if wanted is not None:
            parents={child:parent for parent in tree.iter() for child in parent}
            target=wanted
            cursor=wanted
            # Grid captions can sit underneath Android's navigation bar. Tap
            # the body of their visible card, rather than the covered caption.
            while cursor in parents:
                candidate=parents[cursor]
                b=list(map(int,re.findall(r'\d+',candidate.get('bounds',''))))
                if len(b)==4 and b[3]-b[1]>120 and b[2]-b[0]<500:
                    target=candidate;break
                cursor=candidate
            b=list(map(int,re.findall(r'\d+',target.get('bounds'))))
            adb('shell','input','tap',str((b[0]+b[2])//2),str((b[1]+b[3])//2))
            return
        if attempt==0 and any(n.get('content-desc')=='Show roots' for n in nodes):
            # Use the standard location chooser, never a fake JS import event.
            ui_tap(description='Show roots');ui_tap(text='Downloads')
        else:
            adb('shell','input','swipe','1080','600','1080','260','450')
    raise RuntimeError('Document not visible in Android picker: '+name)


def pause(p):
    if p.locator('#exportSave').is_visible():return
    if p.locator('#closePanel').is_visible():tap(p,'#closePanel')
    tap(p,'#pauseButton')


def run():
    result={'passed':False,'apkSha256':apk_hash(),'checks':{},'method':'Real Android DocumentsUI selections through ADB; CDP reads state and game buttons.'}
    original_hash=adb('shell','sha256sum',PRIVATE+'/save.json').split()[0]
    try:
        exported=os.environ.get('ASTERION_QA_RESUME_EXPORT')
        if exported:
            assert Path(exported).name==exported and exported.startswith('asterion-elf-beauties-v2-save')
            _,p=connect(None)
            if os.environ.get('ASTERION_QA_RESUME_AFTER_EXPORT')=='1':
                prior=json.loads((ART/'android-v2-storage.json').read_text())
                assert prior['apkSha256']==result['apkSha256']
                assert prior['checks']['realSafExport']['name']==exported
                assert prior['checks']['realSafExport']['validChecksum'] is True
                result['exportContinuation']='Continues the previously verified real DocumentsUI export on this exact APK after correcting picker-coordinate handling. The export file checksum is checked again.'
            else:
                message=alert_text();assert 'записана' in message,message
                dismiss_message()
                result['exportContinuation']='Continues a real DocumentsUI export after a fresh-tree ADB SAVE tap; current native success alert is required.'
        else:
            p=open_app();begin(p);pause(p)
            old_files=set(adb('shell','ls','-1','/sdcard/Download').splitlines())
            tap(p,'#exportSave');ui_tap(res='android:id/button1')
            message=alert_text();assert 'записана' in message,message
            dismiss_message()
            new_files=set(adb('shell','ls','-1','/sdcard/Download').splitlines())-old_files
            exported=next(n for n in new_files if n.startswith('asterion-elf-beauties-v2-save') and n.endswith('.json'))
        raw=adb('shell','cat',shlex.quote('/sdcard/Download/'+exported))
        envelope=json.loads(raw)
        assert hashlib.sha256(envelope['payload'].encode()).hexdigest()==envelope['checksum']
        payload=json.loads(envelope['payload']);assert payload['campaignEdition']=='elf-beauties-v2'
        result['checks']['realSafExport']={'name':exported,'bytes':len(raw.encode()),'validChecksum':True}
        stamp=str(time.time_ns())
        payload['lastAction']='V2_SAF_IMPORT_'+stamp
        payload['ui']={'kind':'level','id':'l001','tab':'python'}
        payload['levels']['l001']['draft']+='\n# V2_SAF_IMPORTED_DRAFT\n'
        # Editing a verified program explicitly invalidates its old result.
        payload['levels']['l001']['pythonPassed']=False
        payload['levels']['l001']['codeTransferPassed']=False
        valid=copy.deepcopy(envelope);valid['payload']=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
        valid['checksum']=hashlib.sha256(valid['payload'].encode()).hexdigest()
        invalid=copy.deepcopy(valid);invalid['checksum']='0'*64
        legacy=copy.deepcopy(valid);legacy_payload=copy.deepcopy(payload);legacy_payload.pop('campaignEdition')
        legacy['payload']=json.dumps(legacy_payload,ensure_ascii=False,separators=(',',':'));legacy['checksum']=hashlib.sha256(legacy['payload'].encode()).hexdigest()
        names={kind:'v2-'+kind+'-'+stamp+'.json' for kind in ['valid','bad','legacy']}
        with tempfile.TemporaryDirectory(prefix='asterion-v2-storage-') as directory:
            for kind,value in [('valid',valid),('bad',invalid),('legacy',legacy)]:
                local=Path(directory)/names[kind];local.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
                adb('push',str(local),'/sdcard/Download/'+local.name)
            for kind,expected in [('bad','Контрольная сумма'),('legacy','другой редакции')]:
                pause(p);before=p.evaluate('JSON.parse(Android.loadSave()).payload')
                tap(p,'#importSave');select_document(names[kind])
                message=alert_text();assert expected in message,message
                dismiss_message()
                after=p.evaluate('JSON.parse(Android.loadSave()).payload')
                assert after==before,kind
                result['checks']['reject_'+kind]={'message':message,'currentPayloadPreserved':True}
            pause(p);tap(p,'#importSave');select_document(names['valid'])
            p.wait_for_selector('#begin')
            imported=save_state(p)
            assert imported['lastAction']==payload['lastAction']
            assert 'V2_SAF_IMPORTED_DRAFT' in imported['levels']['l001']['draft']
            result['checks']['realSafImport']={'marker':payload['lastAction'],'draftPreserved':True}
            p=open_app();begin(p);p.wait_for_selector('#codeEditor')
            assert 'V2_SAF_IMPORTED_DRAFT' in p.locator('#codeEditor').input_value()
            result['checks']['importSurvivesForceStop']=True
            pause(p)
            # Two writes provide a known working backup before deliberate
            # corruption of this emulator-only new-edition profile.
            saved=p.evaluate('''()=>{const value=JSON.parse(Android.loadSave()).payload;return [JSON.parse(Android.saveState(value)),JSON.parse(Android.saveState(value))];}''')
            assert all(x['ok'] for x in saved)
            prior=json.loads(adb('shell','cat',PROFILE+'/save.previous.json'))
            adb('shell','am','force-stop',PACKAGE)
            damaged=Path(directory)/'damaged.json';damaged.write_text('{BROKEN_V2_QA_PROFILE',encoding='utf-8')
            adb('push',str(damaged),'/sdcard/v2-qa-damaged.json')
            adb('shell','cp','/sdcard/v2-qa-damaged.json',PROFILE+'/save.json')
            start();_,p=connect(None);p.wait_for_selector('#recoverSave')
            assert adb('shell','cat',PROFILE+'/save.json')=='{BROKEN_V2_QA_PROFILE'
            rejected=p.evaluate('JSON.parse(Android.saveState('+json.dumps(prior['payload'])+'))')
            assert rejected['ok'] is False
            assert adb('shell','cat',PROFILE+'/save.json')=='{BROKEN_V2_QA_PROFILE'
            screenshot('android-v2-recovery.png')
            tap(p,'#recoverSave');p.wait_for_selector('#begin')
            assert save_state(p)['lastAction']==json.loads(prior['payload'])['lastAction']
            assert 'save.damaged.' in adb('shell','ls','-1',PROFILE)
            result['checks']['corruptionRecovery']={'blockedOverwrite':True,'retainedDamagedCopy':True,'restoredBackup':True}
            p=open_app();begin(p)
            assert 'V2_SAF_IMPORTED_DRAFT' in save_state(p)['levels']['l001']['draft']
            result['checks']['recoverySurvivesForceStop']=True
        assert adb('shell','sha256sum',PRIVATE+'/save.json').split()[0]==original_hash
        result['checks']['previousEditionSaveUnchanged']=True
        result['passed']=True
    except Exception as e:
        result['failure']=str(e);raise
    finally:
        write_report('android-v2-storage.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':run()
