/* Pyodide 0.26.4 intentionally uses a classic Worker (not current latest API). */
let engine = null;
let initialization = null;
const PYTHON_BRIDGE = `
import json as _asterion_json
import contextlib as _asterion_contextlib
import traceback as _asterion_traceback

class _AsterionOutput:
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

def _asterion_run(exercise_id, code, variant):
    out, err = _AsterionOutput(), _AsterionOutput()
    result = {'status':'error', 'checks':[], 'feedback':''}
    try:
        namespace = {'__name__':'__main__'}
        with _asterion_contextlib.redirect_stdout(out), _asterion_contextlib.redirect_stderr(err):
            exec(compile(code, '<player>', 'exec'), namespace)
            checked = _asterion_validator(exercise_id, namespace, variant)
        result.update(checked)
        result['status'] = 'passed' if checked['passed'] else 'failed'
    except BaseException as exc:
        result['feedback'] = type(exc).__name__ + ': ' + str(exc)[:2000]
        result['traceback'] = ''.join(_asterion_traceback.format_exception(type(exc), exc, exc.__traceback__))[-6000:]
    result['stdout'] = out.value()
    result['stderr'] = err.value() + ('\\n' + result.pop('traceback') if 'traceback' in result else '')
    return _asterion_json.dumps(result, ensure_ascii=False)
`;
async function initialize() {
  if (engine) return;
  if (initialization) return initialization;
  initialization = (async () => {
    const base = new URL('../vendor/pyodide/', self.location.href).href;
    importScripts(base + 'pyodide.js', base + 'pyodide.asm.js');
    // Pinned 0.26.4 exposes fatal reporting through Module.API.on_fatal and
    // Emscripten's onAbort. A fatal bootstrap error may otherwise leave its
    // ready promise unresolved. Keep the actual runtime and checksum checks intact.
    const createModule = self._createPyodideModule;
    let rejectFatal;
    let reportedFatal = false;
    const fatal = new Promise((resolve, reject) => { rejectFatal = reject; });
    const reportFatal = error => {
      if (reportedFatal) return;
      reportedFatal = true;
      const failure = error instanceof Error ? error : new Error(String(error));
      rejectFatal(failure);
      self.postMessage({type:'init-error', message:String(failure), stack:failure.stack || ''});
    };
    self._createPyodideModule = settings => {
      const previousFatal = settings.API?.on_fatal;
      const previousAbort = settings.onAbort;
      if (settings.API) settings.API.on_fatal = error => {
        reportFatal(error);
        previousFatal?.(error);
      };
      settings.onAbort = cause => {
        reportFatal(new Error('CPython bootstrap aborted: ' + String(cause)));
        previousAbort?.(cause);
      };
      return createModule(settings);
    };
    self.postMessage({type:'status', message:'Подготовка локального CPython…'});
    engine = await Promise.race([loadPyodide({indexURL:base}), fatal]);
    self.postMessage({type:'status', message:'Подготовка проверок Python…'});
    const response = await fetch(new URL('../python/validator.py', self.location.href));
    if (!response.ok) throw new Error('Не найден локальный validator.py');
    const source = await response.text();
    // Validator namespace is separate from the learner's fresh execution namespace.
    engine.globals.set('_asterion_validator_source', source);
    engine.runPython("_asterion_validator_ns = {}\nexec(_asterion_validator_source, _asterion_validator_ns)\n_asterion_validator = _asterion_validator_ns['validate']\ndel _asterion_validator_source");
    engine.runPython(PYTHON_BRIDGE);
  })();
  return initialization;
}
self.onmessage = async ({data}) => {
  if (data.type === 'init') {
    try { await initialize(); self.postMessage({type:'ready'}); }
    catch (error) { self.postMessage({type:'init-error', message:String(error), stack:error?.stack || ''}); }
    return;
  }
  if (data.type !== 'run') return;
  try {
    await initialize();
    engine.globals.set('_asterion_exercise_id', data.exerciseId);
    engine.globals.set('_asterion_player_code', data.code);
    engine.globals.set('_asterion_variant', data.variant);
    const json = await engine.runPythonAsync('_asterion_run(_asterion_exercise_id, _asterion_player_code, _asterion_variant)');
    self.postMessage({type:'result', id:data.id, result:JSON.parse(json)});
  } catch (error) {
    self.postMessage({type:'result', id:data.id, result:{status:'error', stdout:'', stderr:String(error), checks:[], feedback:'Ошибка среды Python. Остановите и повторите запуск.'}});
  } finally {
    if (engine) {
      for (const name of ['_asterion_exercise_id','_asterion_player_code','_asterion_variant']) engine.globals.delete(name);
    }
  }
};
