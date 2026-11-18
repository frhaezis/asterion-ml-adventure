import {NativePythonRunner, nativePythonAvailable} from './native-python-runner.js';
/* Local CPython in a disposable Worker. No remote interpreter or package fetches. */
export class PythonRunner {
  constructor({onStatus} = {}) {
    if (nativePythonAvailable()) return new NativePythonRunner({onStatus});
    this.onStatus = onStatus || (() => {});
    this.worker = null;
    this.ready = false;
    this.initializing = null;
    this.initResolve = null;
    this.initReject = null;
    this.pending = null;
    this.sequence = 0;
  }
  status(message) { this.onStatus(message); }
  init() {
    if (this.ready) return Promise.resolve();
    if (this.initializing) return this.initializing;
    this.status('Загрузка локального CPython…');
    const worker = new Worker(new URL('./python-worker.js', import.meta.url));
    this.worker = worker;
    this.initializing = new Promise((resolve, reject) => {
      this.initResolve = resolve;
      this.initReject = reject;
    });
    const promise = this.initializing;
    worker.onmessage = ({data}) => {
      if (this.worker !== worker) return;
      if (data.type === 'ready') {
        this.ready = true;
        const resolve = this.initResolve;
        this.initializing = this.initResolve = this.initReject = null;
        this.status('CPython 3.12 готов · офлайн');
        resolve?.();
      } else if (data.type === 'status') {
        this.status(data.message);
      } else if (data.type === 'init-error') {
        this.reset(data.message || 'Не удалось загрузить CPython.', 'error', data.stack || '');
      } else if (data.type === 'result' && this.pending?.id === data.id) {
        const pending = this.pending;
        this.pending = null;
        clearTimeout(pending.timer);
        this.status('CPython готов · офлайн');
        pending.resolve(data.result);
      }
    };
    worker.onerror = event => {
      event.preventDefault();
      this.reset(event.message || 'Ошибка Worker CPython.');
    };
    worker.postMessage({type: 'init'});
    return promise;
  }
  async run({exerciseId, code, variant = 'practice', timeoutMs = 15000}) {
    if (this.pending) return {status:'error', stdout:'', stderr:'', checks:[], feedback:'Уже выполняется программа. Остановите её перед новым запуском.'};
    const epoch = this.sequence;
    try { await this.init(); }
    catch (error) {
      return {status:error.status === 'cancelled' ? 'cancelled' : 'error', phase:'initialization', stdout:'', stderr:error.detail || '', checks:[], feedback:error.message};
    }
    if (epoch !== this.sequence) return {status:'cancelled', phase:'initialization', stdout:'', stderr:'', checks:[], feedback:'Выполнение отменено. Исходник сохранён.'};
    if (this.pending) return {status:'error', stdout:'', stderr:'', checks:[], feedback:'Уже выполняется программа.'};
    this.status('Выполняется Python…');
    const id = ++this.sequence;
    return new Promise(resolve => {
      const milliseconds = Math.max(50, Math.min(Number(timeoutMs) || 15000, 60000));
      const timer = setTimeout(() => {
        if (this.pending?.id !== id) return;
        this.reset(`Превышен лимит ${milliseconds / 1000} с. Проверьте цикл или рекурсию.`, 'timeout');
      }, milliseconds);
      this.pending = {id, resolve, timer};
      this.worker.postMessage({type:'run', id, exerciseId, code:String(code), variant});
    });
  }
  reset(message, status = 'error', detail = '') {
    const pending = this.pending;
    const reject = this.initReject;
    this.sequence++;
    this.pending = null;
    this.ready = false;
    this.initializing = this.initResolve = this.initReject = null;
    this.worker?.terminate();
    this.worker = null;
    if (pending) {
      clearTimeout(pending.timer);
      pending.resolve({status, stdout:'', stderr:detail, checks:[], feedback:message});
    }
    reject?.(Object.assign(new Error(message), {status, detail}));
    this.status(status === 'cancelled' ? 'Остановлено · следующий запуск восстановит CPython' : 'Среда будет восстановлена при следующем запуске');
  }
  stop() { this.reset('Выполнение остановлено. Исходник сохранён; среда будет создана заново.', 'cancelled'); }
}
