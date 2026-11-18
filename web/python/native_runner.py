"""Pure CPython execution entry point for the isolated Android Python process.
Java owns process termination and the execution timeout; this module owns output
capture, fresh learner namespaces, and behavior-based exercise validation.
"""
import contextlib
import json
import traceback
from validator import validate


class BoundedOutput:
    def __init__(self):
        self.parts = []
        self.size = 0

    def write(self, text):
        text = str(text)
        remaining = 32768 - self.size
        if remaining > 0:
            self.parts.append(text[:remaining])
            self.size += min(remaining, len(text))
        if len(text) > remaining:
            raise RuntimeError('Вывод превышает 32768 символов. Уменьшите печать в цикле.')
        return len(text)

    def flush(self):
        pass

    def value(self):
        return ''.join(self.parts)


def run(exercise_id, code, variant='practice'):
    out, err = BoundedOutput(), BoundedOutput()
    result = {'status': 'error', 'phase': 'execution', 'checks': [], 'feedback': ''}
    try:
        namespace = {'__name__': '__main__'}
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            exec(compile(code, '<player>', 'exec'), namespace)
            checked = validate(exercise_id, namespace, variant)
        result.update(checked)
        result['status'] = 'passed' if checked['passed'] else 'failed'
    except BaseException as exc:
        result['feedback'] = type(exc).__name__ + ': ' + str(exc)[:2000]
        result['traceback'] = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-6000:]
    result['stdout'] = out.value()
    result['stderr'] = err.value() + ('\n' + result.pop('traceback') if 'traceback' in result else '')
    return json.dumps(result, ensure_ascii=False)


def info():
    import sys
    return json.dumps({'version': sys.version, 'implementation': sys.implementation.name}, ensure_ascii=False)
