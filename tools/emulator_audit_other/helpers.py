#!/usr/bin/env python3
"""Locate SIMD helper bodies in the one audited stock Android Emulator binary."""
import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True

SOURCE_SHA256 = '2aee49182648ea1e757996a0e4265eee2d0cab12c923c8d4e0634e82ba934453'
REPOSITORY = Path(__file__).resolve().parents[2]


@dataclass
class EmulatorImage:
    path: Path
    data: bytes
    helpers: dict


def load_source(path):
    """Check the complete binary hash before parsing or executing any code."""
    path = Path(path).expanduser().resolve()
    data = path.read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != SOURCE_SHA256:
        raise ValueError(
            f'Unsupported emulator binary: SHA256={actual_hash}; '
            f'expected audited stock binary {SOURCE_SHA256}')
    if data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected a little-endian ELF64 emulator binary')
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
    text, rodata = sections['.text'], sections['.rodata']
    helpers = {}
    for offset, addend in relative.items():
        if rodata[3] <= addend < rodata[3]+rodata[5] and offset-8 in relative:
            address = relative[offset-8]
            if text[3] <= address < text[3]+text[5]:
                name_bytes = data[addend:data.find(b'\0', addend)]
                if name_bytes.endswith((b'_xmm', b'_mmx')):
                    name = name_bytes.decode('ascii')
                    helpers[name] = {
                        'va': address, 'off': address-text[3]+text[4]
                    }
    if not helpers:
        raise ValueError('No SIMD helpers found in the audited binary')
    return EmulatorImage(path, data, helpers)


def parse_arguments(description, output_name=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--source', type=Path, default=os.environ.get('ASTERION_EMULATOR_SOURCE'),
        help='Full path to the stock qemu-system-x86_64 binary; alternatively '
             'set ASTERION_EMULATOR_SOURCE')
    if output_name:
        parser.add_argument(
            '--output', type=Path, default=REPOSITORY/'artifacts'/output_name,
            help='Result JSON path (default: repository artifacts/'+output_name+')')
    args = parser.parse_args()
    if args.source is None:
        parser.error('Provide --source or set ASTERION_EMULATOR_SOURCE')
    return parser, args


if __name__ == '__main__':
    parser, args = parse_arguments(__doc__)
    try:
        image = load_source(args.source)
        for name in sorted(image.helpers):
            if name.endswith('_xmm'):
                print(name, hex(image.helpers[name]['va']))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error)+'\n')
