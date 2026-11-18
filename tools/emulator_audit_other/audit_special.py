#!/usr/bin/env python3
"""Compare 15 stock emulator SIMD helpers with hardware x86 instructions.

Uses 1,260,812 deterministic cases, including all 256 shuffle/shift/blend
immediates and five operand/mask alias arrangements. Supply --source or set
ASTERION_EMULATOR_SOURCE. Requires x86_64 Linux, SSSE3/SSE4.1 and gcc.
"""
import ctypes
import json
import random
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
from helpers import load_source, parse_arguments
from mapping import Array as Arr, EmulatorMapping, build_reference, write_results

def audit(image):
    helpers = image.helpers
    with EmulatorMapping(image) as mapped:
        base = mapped.base
        with tempfile.TemporaryDirectory(prefix='asterion-simd-special-') as temporary:
            asm = ['.intel_syntax noprefix', '.text']
            shuffles = ['pshufd', 'pshuflw', 'pshufhw']
            byteshifts = ['pslldq', 'psrldq']
            immops = ['pblendw', 'blendps', 'blendpd', 'mpsadbw']

            def fn(name, body):
                asm.extend(['.p2align 4', f'.globl ref_{name}', f'.type ref_{name},@function', f'ref_{name}:'] + body + ['ret'])
            for op in shuffles:
                for k in range(256):
                    fn(op + '_' + str(k), ['movdqu xmm1,[rsi]', f'{op} xmm0,xmm1,{k}', 'movdqu [rdi],xmm0'])
            for op in byteshifts:
                for k in range(256):
                    fn(op + '_' + str(k), ['movdqu xmm0,[rsi]', f'{op} xmm0,{k}', 'movdqu [rsi],xmm0'])
            for op in immops:
                for k in range(256):
                    fn(op + '_' + str(k), ['movdqu xmm0,[rsi]', 'movdqu xmm1,[rdx]', f'{op} xmm0,xmm1,{k}', 'movdqu [rsi],xmm0'])
            for op in ['pblendvb', 'blendvps', 'blendvpd']:
                fn(op, ['movdqu xmm0,[rdi+0x318]', 'movdqu xmm1,[rsi]', 'movdqu xmm2,[rdx]', f'{op} xmm1,xmm2', 'movdqu [rsi],xmm1'])
            fn('phminposuw', ['movdqu xmm1,[rdx]', 'phminposuw xmm0,xmm1', 'movdqu [rsi],xmm0'])
            fn('pmovmskb', ['movdqu xmm0,[rsi]', 'pmovmskb eax,xmm0'])
            fn('ptest', ['movdqu xmm0,[rsi]', 'movdqu xmm1,[rdx]', 'ptest xmm0,xmm1', 'pushfq', 'pop rax', 'and eax,0x41', 'mov [rdi+0x98],rax'])
            asm += ['.section .note.GNU-stack,"",@progbits']
            lib = build_reference(asm, temporary, 'native_special')
            sig3 = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
            sigshuffle = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int)
            sig4 = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int)
            rng = random.Random(7398154)
            results = []

            def native(name, argtypes):
                f = getattr(lib, 'ref_' + name)
                f.argtypes = argtypes
                return f

            def vec_run(fn, a, b, alias, k=None, style='normal'):
                aa, bb = (Arr(*a), Arr(*b))
                if style == 'shuffle':
                    fn(aa, aa if alias else bb, k)
                elif k is None:
                    fn(None, aa, aa if alias else bb)
                else:
                    fn(None, aa, aa if alias else bb, k)
                return bytes(aa)

            def finish(op, cases, failures, examples):
                detail = helpers[op + '_xmm']
                r = {'helper': op + '_xmm', 'address': hex(detail['va']), 'file_offset': hex(detail['off']), 'cases': cases, 'failures': failures, 'examples': examples}
                results.append(r)
                print(op, cases, 'cases', failures, 'FAILURES', flush=True)
                if examples:
                    print(json.dumps(examples), flush=True)
            for op in shuffles + byteshifts + immops:
                cases = failures = 0
                examples = []
                signature = sigshuffle if op in shuffles else sig3 if op in byteshifts else sig4
                old = signature(base + helpers[op + '_xmm']['va'])
                for k in range(256):
                    ref = native(op + '_' + str(k), [ctypes.c_void_p] * 2 + [ctypes.c_int] if op in shuffles else [ctypes.c_void_p] * 3 + [ctypes.c_int])
                    for alias in [False, True]:
                        for _ in range(100):
                            a, b = (rng.randbytes(16), rng.randbytes(16))
                            if op in byteshifts:
                                b = k.to_bytes(4, 'little') + b[4:]
                                if alias:
                                    a = b
                                actual = vec_run(old, a, b, alias)
                                expected = vec_run(ref, a, b, alias, k)
                            else:
                                if alias:
                                    b = a
                                style = 'shuffle' if op in shuffles else 'normal'
                                actual = vec_run(old, a, b, alias, k, style)
                                expected = vec_run(ref, a, b, alias, k, style)
                            cases += 1
                            if actual != expected:
                                failures += 1
                                if len(examples) < 5:
                                    examples.append({'alias': alias, 'imm': k, 'a': a.hex(), 'b': b.hex(), 'expected': expected.hex(), 'actual': actual.hex()})
                finish(op, cases, failures, examples)

            def blend_run(fn, a, b, m, alias):
                env = ctypes.create_string_buffer(1024)
                e = ctypes.addressof(env)
                mask = e + 792
                ctypes.memmove(mask, m, 16)
                aa, bb = (Arr(*a), Arr(*b))
                ap, bp = (ctypes.addressof(aa), ctypes.addressof(bb))
                if alias == 'ds':
                    bp = ap
                elif alias == 'dm':
                    ap = mask
                elif alias == 'sm':
                    bp = mask
                elif alias == 'all':
                    ap = bp = mask
                fn(e, ap, bp)
                return ctypes.string_at(ap, 16)
            for op in ['pblendvb', 'blendvps', 'blendvpd']:
                old = sig3(base + helpers[op + '_xmm']['va'])
                ref = native(op, [ctypes.c_void_p] * 3)
                cases = failures = 0
                examples = []
                for alias in ['none', 'ds', 'dm', 'sm', 'all']:
                    for _ in range(20000):
                        a, b, m = (rng.randbytes(16), rng.randbytes(16), rng.randbytes(16))
                        actual = blend_run(old, a, b, m, alias)
                        expected = blend_run(ref, a, b, m, alias)
                        cases += 1
                        if actual != expected:
                            failures += 1
                            if len(examples) < 5:
                                examples.append({'alias': alias, 'a': a.hex(), 'b': b.hex(), 'mask': m.hex(), 'expected': expected.hex(), 'actual': actual.hex()})
                finish(op, cases, failures, examples)
            for op in ['phminposuw']:
                old = sig3(base + helpers[op + '_xmm']['va'])
                ref = native(op, [ctypes.c_void_p] * 3)
                cases = failures = 0
                examples = []
                for alias in [False, True]:
                    for _ in range(100000):
                        a, b = (rng.randbytes(16), rng.randbytes(16))
                        if alias:
                            b = a
                        actual = vec_run(old, a, b, alias)
                        expected = vec_run(ref, a, b, alias)
                        cases += 1
                        if actual != expected:
                            failures += 1
                            if len(examples) < 5:
                                examples.append({'alias': alias, 'a': a.hex(), 'b': b.hex(), 'expected': expected.hex(), 'actual': actual.hex()})
                finish(op, cases, failures, examples)
            for op in ['pmovmskb']:
                old = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p)(base + helpers[op + '_xmm']['va'])
                ref = native(op, [ctypes.c_void_p] * 2)
                cases = failures = 0
                examples = []
                for _ in range(100000):
                    a = rng.randbytes(16)
                    aa = Arr(*a)
                    actual = old(None, aa)
                    expected = ref(None, aa)
                    cases += 1
                    if actual != expected:
                        failures += 1
                        if len(examples) < 5:
                            examples.append({'a': a.hex(), 'expected': expected, 'actual': actual})
                finish(op, cases, failures, examples)
            for op in ['ptest']:
                old = sig3(base + helpers[op + '_xmm']['va'])
                ref = native(op, [ctypes.c_void_p] * 3)
                cases = failures = 0
                examples = []
                edge_pairs = [(bytes(16), bytes(16)), (bytes(16), bytes([255]) * 16), (bytes([255]) * 16, bytes(16)), (bytes([255]) * 16, bytes([255]) * 16), (bytes([85]) * 16, bytes([170]) * 16), (bytes([85]) * 16, bytes([85]) * 16)]
                for alias in [False, True]:
                    for i in range(100006):
                        a, b = edge_pairs[i] if i < len(edge_pairs) else (rng.randbytes(16), rng.randbytes(16))
                        if alias:
                            b = a
                        aa, bb = (Arr(*a), Arr(*b))
                        env = ctypes.create_string_buffer(1024)
                        old(env, aa, aa if alias else bb)
                        actual = bytes(env)[152:160]
                        ref(env, aa, aa if alias else bb)
                        expected = bytes(env)[152:160]
                        cases += 1
                        if actual != expected:
                            failures += 1
                            if len(examples) < 5:
                                examples.append({'alias': alias, 'a': a.hex(), 'b': b.hex(), 'expected': expected.hex(), 'actual': actual.hex()})
                finish(op, cases, failures, examples)
            return results

def main():
    parser, args = parse_arguments(__doc__, 'emulator-other-simd-special.json')
    try:
        results = audit(load_source(args.source))
        return write_results(results, args.output, 15, 1260812)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')
if __name__ == '__main__':
    sys.exit(main())
