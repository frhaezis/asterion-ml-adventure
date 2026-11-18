package org.asterion.livingprotocol;

import android.app.Service;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.Messenger;
import android.os.RemoteException;
import android.util.Log;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Disposable CPython process. Process separation permits cancellation, not a security sandbox. */
public final class PythonService extends Service {
    public static final int HELLO = 1, RUN = 2;
    public static final int PID = 10, READY = 11, STARTED = 12, RESULT = 13, ERROR = 14, STATUS = 15;
    private static final String TAG = "AsterionPython";
    private static final int MAX_CODE_CHARS = 256 * 1024;
    private static final int MAX_RESULT_CHARS = 192 * 1024;

    private final Handler main = new Handler(Looper.getMainLooper());
    private final ExecutorService executor = Executors.newSingleThreadExecutor(
        work -> new Thread(work, "AsterionCPython"));
    private final Messenger endpoint = new Messenger(new Handler(Looper.getMainLooper()) {
        @Override public void handleMessage(Message message) { receive(message); }
    });
    private Messenger client;
    private boolean initializing, ready, busy;
    private volatile boolean destroyed;
    private String pythonVersion = "", initializationError;

    @Override public IBinder onBind(Intent intent) { return endpoint.getBinder(); }
    @Override public int onStartCommand(Intent intent, int flags, int startId) { return START_NOT_STICKY; }

    private void receive(Message message) {
        if (destroyed) return;
        Messenger target = message.replyTo == null ? client : message.replyTo;
        if (target == null) return;
        if (message.what == HELLO) {
            client = target;
            Bundle identity = new Bundle();
            identity.putInt("pid", android.os.Process.myPid());
            send(target, PID, identity);
            if (ready) {
                sendReady(target);
            } else if (initializationError != null) {
                sendError(target, null, "initialization", initializationError);
            } else if (!initializing) {
                initializing = true;
                Bundle status = new Bundle();
                status.putString("message", "Подготовка локального CPython…");
                send(target, STATUS, status);
                executor.execute(this::initializePython);
            }
            return;
        }
        if (message.what != RUN) return;
        Bundle request = new Bundle(message.getData());
        if (!ready) {
            sendError(target, request, "initialization", initializationError == null
                ? "CPython ещё не готов к выполнению." : initializationError);
            return;
        }
        if (busy) {
            sendError(target, request, "execution", "Уже выполняется программа.");
            return;
        }
        String code = request.getString("code");
        String exerciseId = request.getString("exerciseId");
        String variant = request.getString("variant", "practice");
        if (code == null || code.length() > MAX_CODE_CHARS || exerciseId == null
                || !("practice".equals(variant) || "transfer".equals(variant))) {
            sendError(target, request, "execution", "Неверные параметры запуска или слишком большой исходник.");
            return;
        }
        busy = true;
        executor.execute(() -> execute(target, request, exerciseId, code, variant));
    }

    private void initializePython() {
        try {
            Log.i(TAG, "PYTHON_START_BEGIN pid=" + android.os.Process.myPid());
            if (!Python.isStarted()) Python.start(new AndroidPlatform(this));
            String version;
            try (PyObject sys = Python.getInstance().getModule("sys");
                 PyObject value = sys.get("version")) {
                version = value.toJava(String.class);
            }
            // Import the trusted wrapper and validator before announcing readiness.
            try (PyObject ignored = Python.getInstance().getModule("native_runner")) { }
            final String resultVersion = version;
            main.post(() -> {
                if (destroyed) return;
                pythonVersion = resultVersion;
                initializing = false;
                ready = true;
                Log.i(TAG, "PYTHON_READY " + pythonVersion);
                if (client != null) sendReady(client);
            });
        } catch (Throwable failure) {
            Log.e(TAG, "PYTHON_INITIALIZATION_ERROR", failure);
            final String description = describe(failure);
            main.post(() -> {
                if (destroyed) return;
                initializing = false;
                initializationError = description;
                if (client != null) sendError(client, null, "initialization", description);
            });
        }
    }

    private void execute(Messenger target, Bundle request, String exerciseId, String code, String variant) {
        if (destroyed) return;
        send(target, STARTED, responseFor(request));
        try {
            String json;
            try (PyObject runner = Python.getInstance().getModule("native_runner");
                 PyObject result = runner.callAttr("run", exerciseId, code, variant)) {
                json = result.toJava(String.class);
            }
            if (json == null || json.length() > MAX_RESULT_CHARS) {
                throw new IllegalStateException("Результат Python превышает допустимый размер.");
            }
            Bundle result = responseFor(request);
            result.putString("resultJson", json);
            main.post(() -> {
                if (destroyed) return;
                busy = false;
                send(target, RESULT, result);
            });
        } catch (Throwable failure) {
            Log.e(TAG, "PYTHON_EXECUTION_ERROR", failure);
            final String description = describe(failure);
            main.post(() -> {
                if (destroyed) return;
                busy = false;
                sendError(target, request, "execution", description);
            });
        }
    }

    private void sendReady(Messenger target) {
        Bundle result = new Bundle();
        result.putInt("pid", android.os.Process.myPid());
        result.putString("pythonVersion", pythonVersion);
        send(target, READY, result);
    }

    private void sendError(Messenger target, Bundle request, String phase, String description) {
        Bundle result = responseFor(request);
        result.putString("phase", phase);
        result.putString("message", description);
        send(target, ERROR, result);
    }

    private static Bundle responseFor(Bundle request) {
        Bundle response = new Bundle();
        if (request == null) return response;
        Object id = request.get("requestId");
        if (id instanceof Integer) response.putInt("requestId", (Integer) id);
        else if (id instanceof Long) response.putLong("requestId", (Long) id);
        else if (id instanceof String) response.putString("requestId", (String) id);
        return response;
    }

    private void send(Messenger target, int type, Bundle data) {
        if (destroyed || target == null) return;
        Message reply = Message.obtain(null, type);
        reply.setData(data);
        try { target.send(reply); }
        catch (RemoteException failure) { Log.w(TAG, "Python client disconnected", failure); }
    }

    private static String describe(Throwable failure) {
        String text = failure.getClass().getSimpleName() + ": " + String.valueOf(failure.getMessage());
        return text.length() > 6000 ? text.substring(0, 6000) : text;
    }

    @Override public void onDestroy() {
        destroyed = true;
        main.removeCallbacksAndMessages(null);
        executor.shutdownNow();
        super.onDestroy();
        // Chaquopy cannot be finalized and restarted within this process. The manifest
        // places this service in :python, so its death leaves the activity and saves alive.
        android.os.Process.killProcess(android.os.Process.myPid());
    }
}
