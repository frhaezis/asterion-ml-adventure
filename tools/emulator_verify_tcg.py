#!/usr/bin/env python3
"""Verify the allowlisted private emulator repair against scalar ISA references."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from emulator_audit_simd import run


def verify(manifest_path):
    manifest=json.loads(manifest_path.read_text())
    if 'ssse3' not in Path('/proc/cpuinfo').read_text().split():
        raise RuntimeError('Host SSSE3 required')
    for item in manifest['files']:
        original=Path(item['source']).read_bytes()
        patched=Path(item['patched']).read_bytes()
        assert hashlib.sha256(original).hexdigest()==item['original_sha256']
        assert hashlib.sha256(patched).hexdigest()==item['patched_sha256']
        reconstructed=bytearray(original)
        for helper in item['helpers']:
            offset=int(helper['helper_file_offset'],16)
            before,after=bytes.fromhex(helper['before_hex']),bytes.fromhex(helper['after_hex'])
            assert original[offset:offset+len(before)]==before
            reconstructed[offset:offset+len(after)]=after
        assert bytes(reconstructed)==patched, 'Changes outside the declared helpers'
        with tempfile.TemporaryDirectory(prefix='asterion-cpu-') as directory:
            report=Path(directory)/'verification.json'
            run(Path(item['patched']),report,100000,item['patched_sha256'])
            checks=json.loads(report.read_text())['records']
            assert all(r['failures_distinct']==0 and r['failures_alias']==0 for r in checks)
            print('PASS',Path(item['patched']).name,sum(r['cases'] for r in checks),'reference cases')
    print('PASS: original hashes unchanged; only six declared helper regions changed')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True,type=Path)
    verify(parser.parse_args().manifest)
