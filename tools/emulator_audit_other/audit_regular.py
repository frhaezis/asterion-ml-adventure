#!/usr/bin/env python3
"""Compare 90 stock emulator SIMD helpers with hardware x86 instructions.

Uses 1,858,000 deterministic cases with distinct and aliased operands. Supply
--source /path/to/qemu-system-x86_64 or set ASTERION_EMULATOR_SOURCE. Requires
an x86_64 Linux host, SSSE3/SSE4.1 and gcc. The emulator is never launched.
"""
import ctypes
import json
import random
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

from helpers import load_source, parse_arguments
from mapping import Array, EmulatorMapping, build_reference, write_results

RENAMES = {'paddl': 'paddd', 'psubl': 'psubd',
           'pcmpeql': 'pcmpeqd', 'pcmpgtl': 'pcmpgtd'}
EXCLUDED = {
    'phaddd', 'phaddw', 'phaddsw', 'phsubd', 'phsubw', 'phsubsw', 'palignr', 'pshufb',
    'pshufd', 'pshuflw', 'pshufhw', 'pslldq', 'psrldq', 'pblendvb', 'pblendw',
    'ptest', 'pmovmskb', 'pcmpestri', 'pcmpestrm', 'pcmpistri', 'pcmpistrm',
    'pclmulqdq', 'phminposuw',
}
SIGNATURE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)


def reference_assembly(operations):
    assembly = ['.intel_syntax noprefix', '.text']
    for name in operations:
        opcode = RENAMES.get(name, name)
        assembly += [
            '.p2align 4', f'.globl ref_{name}', f'.type ref_{name},@function',
            f'ref_{name}:', 'movdqu xmm0,[rsi]', 'movdqu xmm1,[rdx]',
            f'{opcode} xmm0,xmm1', 'movdqu [rsi],xmm0', 'ret',
        ]
    assembly += ['.section .note.GNU-stack,"",@progbits']
    return assembly


def run(function, destination, source, alias):
    aa, bb = Array(*destination), Array(*source)
    function(None, aa, aa if alias else bb)
    return bytes(aa)


def case_set(rng, operation, alias):
    destinations = [bytes(16), bytes([255])*16, bytes(range(16)),
                    bytes(range(255, 239, -1)),
                    bytes.fromhex('00008080007fff7fffff0000ffff0000')]
    sources = [bytes(16), bytes([255])*16, bytes(range(16)), bytes(range(255, 239, -1))]
    for destination in destinations:
        for source in sources:
            yield destination, destination if alias else source
    if operation in {'psllw', 'pslld', 'psllq', 'psrlw', 'psrld', 'psrlq', 'psraw', 'psrad'}:
        for shift in list(range(130))+[255, 0xffffffff, 0x100000000, 0xffffffffffffffff]:
            for _ in range(100):
                source = shift.to_bytes(8, 'little')+rng.randbytes(8)
                destination = source if alias else rng.randbytes(16)
                yield destination, source
    else:
        for _ in range(10000):
            destination, source = rng.randbytes(16), rng.randbytes(16)
            yield destination, destination if alias else source


def audit(image):
    operations = [name[:-4] for name in image.helpers
                  if name.endswith('_xmm') and name.startswith('p')
                  and name[:-4] not in EXCLUDED]
    results = []
    rng = random.Random(39184752)
    with EmulatorMapping(image) as mapped:
        with tempfile.TemporaryDirectory(prefix='asterion-simd-regular-') as temporary:
            library = build_reference(reference_assembly(operations), temporary, 'native_refs')
            for operation in sorted(operations):
                detail = image.helpers[operation+'_xmm']
                original = SIGNATURE(mapped.base+detail['va'])
                reference = getattr(library, 'ref_'+operation)
                reference.argtypes = [ctypes.c_void_p]*3
                reference.restype = None
                cases = failures = 0
                examples = []
                for alias in (False, True):
                    for destination, source in case_set(rng, operation, alias):
                        expected = run(reference, destination, source, alias)
                        actual = run(original, destination, source, alias)
                        cases += 1
                        if expected != actual:
                            failures += 1
                            if len(examples) < 4:
                                examples.append({
                                    'alias': alias, 'a': destination.hex(), 'b': source.hex(),
                                    'expected': expected.hex(), 'actual': actual.hex(),
                                })
                results.append({
                    'helper': operation+'_xmm', 'address': hex(detail['va']),
                    'file_offset': hex(detail['off']), 'cases': cases,
                    'failures': failures, 'examples': examples,
                })
                print(operation, cases, 'cases', failures, 'FAILURES', flush=True)
                if examples:
                    print(json.dumps(examples), flush=True)
    return results


def main():
    parser, args = parse_arguments(__doc__, 'emulator-other-simd-regular.json')
    try:
        results = audit(load_source(args.source))
        return write_results(results, args.output, 90, 1858000)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error)+'\n')


if __name__ == '__main__':
    sys.exit(main())
