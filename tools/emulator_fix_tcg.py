#!/usr/bin/env python3
"""Create a private Android Emulator 36 copy with correct horizontal-SIMD alias semantics.

This corrects the host emulator only. Guest images, WebView, V8 checks, snapshots
and application APKs are untouched. Both SIMD operands are loaded before output
is stored, including when source and destination are the same guest register.
Requires an x86_64 host with SSSE3; the original SDK is left unchanged.

Example:
  python3 tools/emulator_fix_tcg.py --source /path/to/emulator36 \
    --dest /path/to/emulator36-fixed --manifest /path/to/patch-manifest.json
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile

# Only helpers with independently proven original failures are changed.
HELPERS = {
    'phaddw_xmm': (
        bytes.fromhex('0fb746020fb74e0666010666034e0466894e020fb7460a66034608668946040f'),
        bytes.fromhex('f30f6f06f30f6f0a660f3801c1f30f7f06c3').ljust(32, b'\x90')), 
    'phaddd_xmm': (
        bytes.fromhex('8b46048b4e0c0106034e08894e048b420403028946088b420c03420889460cc3'),
        bytes.fromhex('f30f6f06f30f6f0a660f3802c1f30f7f06c3').ljust(32, b'\x90')), 
    'phaddsw_xmm': (
        bytes.fromhex('660f6e06660fc4460401660fc4460802660fc4460c030fb74602660f6ec8660f'),
        bytes.fromhex('f30f6f06f30f6f0a660f3803c1f30f7f06c3').ljust(32, b'\x90')), 
    'phsubw_xmm': (
        bytes.fromhex('0fb746020fb74e04662906662b4e0666894e020fb74608662b460a668946040f'),
        bytes.fromhex('f30f6f06f30f6f0a660f3805c1f30f7f06c3').ljust(32, b'\x90')), 
    'phsubd_xmm': (
        bytes.fromhex('8b46048b4e0829062b4e0c894e048b022b42048946088b42082b420c89460cc3'),
        bytes.fromhex('f30f6f06f30f6f0a660f3806c1f30f7f06c3').ljust(32, b'\x90')), 
    'phsubsw_xmm': (
        bytes.fromhex('660f6e06660fc4460401660fc4460802660fc4460c030fb74602660f6ec8660f'),
        bytes.fromhex('f30f6f06f30f6f0a660f3807c1f30f7f06c3').ljust(32, b'\x90')), 
}
ALLOWLIST = {
    'qemu-system-x86_64':
        '2aee49182648ea1e757996a0e4265eee2d0cab12c923c8d4e0634e82ba934453',
    'qemu-system-x86_64-headless':
        'a0755fc20ec0fa9d0550bccd6762d648549ca7bf9a2b485baeed102f11198eeb',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def require_host():
    require('ssse3' in Path('/proc/cpuinfo').read_text().split(),
            'This local patch requires host SSSE3 support')

def find_helper(data, name):
    require(data[:6] == b'\x7fELF\x02\x01', 'Expected little-endian ELF64')
    shoff = struct.unpack_from('<Q', data, 40)[0]
    size, count, strings_index = struct.unpack_from('<HHH', data, 58)
    sections = [struct.unpack_from('<IIQQQQIIQQ', data, shoff+i*size)
                for i in range(count)]
    string_section = sections[strings_index]
    names = data[string_section[4]:string_section[4]+string_section[5]]
    sections = {
        names[s[0]:names.find(b'\0', s[0])].decode(): s for s in sections
    }
    rela = sections['.rela.dyn']
    relative = {}
    for i in range(rela[4], rela[4]+rela[5], 24):
        offset, kind, addend = struct.unpack_from('<QQq', data, i)
        if kind == 8:  # R_X86_64_RELATIVE
            relative[offset] = addend
    matches = []
    for offset, addend in relative.items():
        if data[addend:addend+len(name)+1] == name.encode()+b'\0':
            virtual_address = relative[offset-8]
            text = sections['.text']
            require(text[3] <= virtual_address < text[3]+text[5],
                    'Helper must be inside executable .text')
            file_offset = virtual_address-text[3]+text[4]
            matches.append((virtual_address, file_offset))
    require(len(matches) == 1, f'Expected exactly one {name} helper')
    return matches[0]

def create(source, dest, manifest_path):
    require_host()
    source, dest = source.resolve(), dest.resolve()
    manifest_path = manifest_path.resolve()
    require(source.is_dir(), f'Missing emulator SDK directory: {source}')
    require(not dest.exists(), f'Refusing to overwrite destination: {dest}')
    require(not manifest_path.exists(), f'Refusing to overwrite manifest: {manifest_path}')
    require(source not in dest.parents and dest not in source.parents,
            'Source and destination must be independent directories')
    require(dest not in manifest_path.parents,
            'Manifest must be outside the new emulator directory')
    records = []
    binaries = {}
    # Fail closed before any output is created, on full hash and helper bytes.
    for name, expected_hash in ALLOWLIST.items():
        original_path = source/'qemu'/'linux-x86_64'/name
        data = original_path.read_bytes()
        require(sha(data) == expected_hash,
                f'Unsupported emulator binary {name}; SHA256={sha(data)}')
        patched = bytearray(data)
        helpers = []
        for helper_name, (original_bytes, replacement) in HELPERS.items():
            address, offset = find_helper(data, helper_name)
            require(data[offset:offset+len(original_bytes)] == original_bytes,
                    f'Unexpected {helper_name} bytes in {name}')
            patched[offset:offset+len(original_bytes)] = replacement
            helpers.append({
                'helper': helper_name,
                'helper_virtual_address': hex(address),
                'helper_file_offset': hex(offset),
                'before_hex': original_bytes.hex(), 'after_hex': replacement.hex(),
            })
        binaries[name] = patched
        records.append({
            'source': str(original_path),
            'patched': str(dest/'qemu'/'linux-x86_64'/name),
            'original_sha256': sha(data), 'patched_sha256': sha(patched),
            'helpers': helpers,
        })
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=dest.name+'.tmp-', dir=dest.parent))
    try:
        for item in source.iterdir():
            if item.name == 'qemu':
                continue
            if item.name == 'emulator':
                # A symlink makes /proc/self/exe select the original SDK.
                shutil.copy2(item, temporary/item.name)
            else:
                (temporary/item.name).symlink_to(item, target_is_directory=item.is_dir())
        qemu_target = temporary/'qemu'/'linux-x86_64'
        qemu_target.mkdir(parents=True)
        for item in (source/'qemu'/'linux-x86_64').iterdir():
            output = qemu_target/item.name
            if item.name in binaries:
                output.write_bytes(binaries[item.name])
                shutil.copymode(item, output)
            else:
                output.symlink_to(item)
        temporary.rename(dest)
    except BaseException:
        shutil.rmtree(temporary)
        raise
    manifest = {
        'operation': 'Correct six proven horizontal-SIMD alias errors in local host emulator only',
        'host_requirement': 'x86_64 with SSSE3',
        'sdk_resources': 'Symlinks require the original SDK to remain available',
        'files': records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open('x') as output:
        json.dump(manifest, output, indent=2)
        output.write('\n')
    print(json.dumps(manifest, indent=2))
    print('Private emulator launcher:', dest/'emulator')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path,
                        help='Unmodified Android Emulator 36 SDK directory')
    parser.add_argument('--dest', required=True, type=Path,
                        help='New private emulator directory; must not exist')
    parser.add_argument('--manifest', required=True, type=Path,
                        help='New JSON manifest outside --dest; must not exist')
    args = parser.parse_args()
    try:
        create(args.source, args.dest, args.manifest)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error)+'\n')

if __name__ == '__main__':
    main()
