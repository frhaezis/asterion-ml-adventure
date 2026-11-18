#!/usr/bin/env python3
"""Map the audited ELF layout anonymously and build native SIMD references."""
import ctypes
import hashlib
import json
import mmap
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys

sys.dont_write_bytecode = True

from helpers import SOURCE_SHA256, load_source, parse_arguments

Array = ctypes.c_ubyte*16


def require_host():
    if platform.machine().lower() not in ('x86_64', 'amd64'):
        raise RuntimeError('These audits require an x86_64 Linux host')
    flags = set(Path('/proc/cpuinfo').read_text().split())
    if not {'ssse3', 'sse4_1'}.issubset(flags):
        raise RuntimeError('These audits require host SSSE3 and SSE4.1 support')
    if shutil.which('gcc') is None:
        raise RuntimeError('gcc is required to build the native SIMD references')


class EmulatorMapping:
    """Keep original virtual-address distances for RIP-relative constants."""

    def __init__(self, image):
        require_host()
        data = image.data
        # Recheck at the execution boundary; never map an arbitrary caller blob.
        if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
            raise ValueError('Refusing to map a binary outside the full-hash allowlist')
        phoff = struct.unpack_from('<Q', data, 32)[0]
        size, count = struct.unpack_from('<HH', data, 54)
        segments = [struct.unpack_from('<IIQQQQQQ', data, phoff+i*size)
                    for i in range(count)]
        segments = [p for p in segments if p[0] == 1]  # PT_LOAD
        self.memory = mmap.mmap(
            -1, max(p[3]+p[6] for p in segments),
            prot=mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC)
        self.base = ctypes.addressof(ctypes.c_char.from_buffer(self.memory))
        self.helpers = image.helpers
        for _, flags, offset, address, physical, file_size, memory_size, align in segments:
            self.memory[address:address+file_size] = data[offset:offset+file_size]
        # PSLLDQ/PSRLDQ tail-call memset. Bind that one known PLT target only in
        # this anonymous mapping. The emulator binary on disk is never changed.
        memset = ctypes.cast(ctypes.CDLL(None).memset, ctypes.c_void_p).value
        self.memory[0x1bf5090:0x1bf509c] = (
            b'\x48\xb8'+struct.pack('<Q', memset)+b'\xff\xe0')

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        self.memory.close()


def build_reference(assembly, temporary_directory, name):
    """Caller owns a TemporaryDirectory; no build files enter the repository."""
    source = Path(temporary_directory)/(name+'.S')
    library = Path(temporary_directory)/(name+'.so')
    source.write_text('\n'.join(assembly)+'\n')
    subprocess.run(['gcc', '-shared', '-fPIC', '-o', str(library), str(source)],
                   check=True)
    return ctypes.CDLL(str(library))


def write_results(results, output, helper_count, case_count):
    actual_cases = sum(result['cases'] for result in results)
    if len(results) != helper_count or actual_cases != case_count:
        raise RuntimeError(
            f'Unexpected coverage: {len(results)} helpers, {actual_cases} cases')
    output = Path(output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2)+'\n')
    failures = sum(result['failures'] for result in results)
    print('TOTAL', actual_cases, 'CASES', failures, 'FAILURES')
    print('Result JSON:', output)
    return 1 if failures else 0


if __name__ == '__main__':
    parser, args = parse_arguments(__doc__)
    try:
        with EmulatorMapping(load_source(args.source)) as mapped:
            print('Validated and anonymously mapped', len(mapped.helpers), 'SIMD helpers')
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, str(error)+'\n')
