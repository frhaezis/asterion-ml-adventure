/* Android adapter: CPython runs in a separate, killable native service process. */
const requests = new Map();
const adapters = new Set();
let requestSequence = 0;
let routerInstalled = false;

function installRouter() {
  if (routerInstalled) return;
  routerInstalled = true;
  const previous = window.onNativePythonMessage;
  window.onNativePythonMessage = raw => {
    let event;
    try { event = typeof raw === 'string' ? JSON.parse(raw) : raw; }
    catch { return; }
    if (!event || typeof event !== 'object') return;
    const handler = requests.get(String(event.requestId));
    if (handler) handler(event);
    else if (event.type === 'reset' && !event.requestId) {
      for (const adapter of adapters) adapter.resetFromService(event.message);
    } else if (typeof previous === 'function') previous(raw);
  };
}

export function nativePythonAvailable() {
  return typeof window !== 'undefined' &&
    ['pythonInit','pythonRun','pythonStop'].every(name => typeof window.Android?.[name] === 'function');
}

export class NativePythonRunner {
  constructor({onStatus} = {}) {
    this.bridge = window.Android;
    this.onStatus = onStatus || (() => {});
    this.ready = false;
    this.initializing = null;
    this.initialization = null;
    this.pending = null;
    this.generation = 0;
    adapters.add(this);
    installRouter();
  }
  requestId() { return 'python-' + (++requestSequence); }
  status(message) { this.onStatus(message); }
  init() {
    if (this.ready) return Promise.resolve();
    if (this.initializing) return this.initializing;
    this.status('Подготовка локального CPython…');
    const id = this.requestId();
    this.initializing = new Promise((resolve, reject) => {
      this.initialization = {id, resolve, reject};
    });
    const promise = this.initializing;
    requests.set(id, event => {
      if (event.type === 'status') { this.status(event.message || 'Подготовка Python…'); return; }
      if (event.type === 'ready') {
        requests.delete(id);
        const initialization = this.initialization;
        this.initializing = this.initialization = null;
        this.ready = true;
        this.status('CPython готов · на устройстве');
        initialization?.resolve();
      } else if (event.type === 'init-error' || event.type === 'reset') {
        this.failInitialization(event.message || 'Не удалось подготовить CPython.', 'error', event.stack || '');
      }
    });
    try { this.bridge.pythonInit(id); }
    catch (error) { this.failInitialization(error.message || String(error)); }
    return promise;
  }
  failInitialization(message, status = 'error', detail = '') {
    const initialization = this.initialization;
    this.ready = false;
    this.initializing = this.initialization = null;
    if (initialization) {
      requests.delete(initialization.id);
      initialization.reject(Object.assign(new Error(message), {status, detail}));
    }
    this.status(message);
  }
  async run({exerciseId, code, variant = 'practice', timeoutMs = 15000}) {
    if (this.pending) return {status:'error', stdout:'', stderr:'', checks:[], feedback:'Уже выполняется программа.'};
    const generation = this.generation;
    try { await this.init(); }
    catch (error) {
      return {status:error.status === 'cancelled' ? 'cancelled' : 'error', phase:'initialization', stdout:'', stderr:error.detail || '', checks:[], feedback:error.message};
    }
    if (generation !== this.generation) return {status:'cancelled', phase:'initialization', stdout:'', stderr:'', checks:[], feedback:'Выполнение отменено.'};
    if (this.pending) return {status:'error', stdout:'', stderr:'', checks:[], feedback:'Уже выполняется программа.'};
    const id = this.requestId();
    const milliseconds = Math.max(50, Math.min(Number(timeoutMs) || 15000, 60000));
    this.status('Выполняется Python на устройстве…');
    return new Promise(resolve => {
      const finish = result => {
        if (this.pending?.id !== id) return;
        clearTimeout(this.pending.timer);
        requests.delete(id);
        this.pending = null;
        if (['timeout','cancelled'].includes(result.status) || result.phase === 'initialization') this.ready = false;
        this.status(this.ready ? 'CPython готов · на устройстве' : 'Среда будет восстановлена при следующем запуске');
        resolve(result);
      };
      // Java starts the execution deadline only after the service reports
      // MSG_STARTED, and owns the separate 120-second initialization deadline.
      this.pending = {id, finish};
      requests.set(id, event => {
        if (event.type === 'status') { this.status(event.message || 'Выполняется Python…'); return; }
        if (event.type === 'result') {
          let result = event.result;
          try { if (typeof result === 'string') result = JSON.parse(result); } catch { result = null; }
          finish(result && typeof result === 'object' ? result : {status:'error', stdout:'', stderr:'', checks:[], feedback:'Некорректный ответ среды Python.'});
        } else if (event.type === 'init-error') {
          finish({status:'error', phase:'initialization', stdout:'', stderr:event.stack || '', checks:[], feedback:event.message || 'Не удалось подготовить Python.'});
        } else if (event.type === 'reset') {
          this.ready = false;
          finish({status:'error', phase:'initialization', stdout:'', stderr:'', checks:[], feedback:event.message || 'Процесс Python завершился. Повторите запуск.'});
        }
      });
      try { this.bridge.pythonRun(id, exerciseId, String(code), variant, Math.round(milliseconds)); }
      catch (error) { finish({status:'error', phase:'initialization', stdout:'', stderr:'', checks:[], feedback:error.message || String(error)}); }
    });
  }
  resetFromService(message) {
    // Broadcast reset invalidates readiness only. Java separately reports the
    // correlated timeout/cancellation/error; do not replace that result here.
    this.ready = false;
    if (!this.pending && !this.initializing && message) this.status(message);
  }
  stop() {
    this.generation++;
    const id = this.pending?.id || this.initialization?.id || this.requestId();
    this.ready = false;
    try { this.bridge.pythonStop(id); } catch {}
    this.failInitialization('Выполнение остановлено. Исходник сохранён.', 'cancelled');
    this.pending?.finish({status:'cancelled', phase:'execution', stdout:'', stderr:'', checks:[], feedback:'Выполнение остановлено. Исходник сохранён.'});
    this.status('Остановлено · следующий запуск восстановит CPython');
  }
}
