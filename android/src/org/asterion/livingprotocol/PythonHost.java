package org.asterion.livingprotocol;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.Messenger;
import android.os.Process;
import android.os.RemoteException;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.LinkedHashSet;

/** UI-process coordinator. Python executes only in the separately killable service. */
final class PythonHost {
    interface Events { void receive(JSONObject event); }
    private final Activity activity;
    private final Events events;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final LinkedHashSet<String> initializations = new LinkedHashSet<>();
    private Messenger service;
    private ServiceConnection connection;
    private Runnable initializationDeadline, executionDeadline;
    private String activeRequest, pythonVersion = "3.12.15";
    private int timeoutMs, generation;
    private Bundle queuedRun;
    private boolean closed;
    private volatile int childPid;
    private volatile boolean ready;

    PythonHost(Activity activity, Events events) { this.activity=activity;this.events=events; }
    int pid() { return childPid; }
    boolean isReady() { return ready; }
    private static boolean validId(String id) {
        return id != null && id.matches("[A-Za-z0-9_.:-]{1,160}");
    }
    private void emit(String type, String id, Object... pairs) {
        if(closed)return;
        try {
            JSONObject event = new JSONObject().put("type",type);
            if(id!=null)event.put("requestId",id);
            for(int i=0;i<pairs.length;i+=2)event.put((String)pairs[i],pairs[i+1]);
            events.receive(event);
        } catch(Exception error) { Log.e("AsterionPython","Cannot deliver Python event",error); }
    }
    private JSONObject result(String status, String message, String phase) {
        try { return new JSONObject().put("status",status).put("feedback",message)
            .put("phase",phase).put("stdout","").put("stderr","").put("checks",new JSONArray()); }
        catch(Exception impossible) { throw new IllegalStateException(impossible); }
    }
    void init(String requestId) {
        if(closed||!validId(requestId))return;
        if(ready) { emit("ready",requestId,"pythonVersion",pythonVersion);return; }
        initializations.add(requestId);
        emit("status",requestId,"message","Подготовка локального CPython…");
        ensureBound();
    }
    void run(String requestId, String exerciseId, String code, String variant, int milliseconds) {
        if(closed||!validId(requestId))return;
        if(activeRequest!=null) {
            emit("result",requestId,"result",result("error","Уже выполняется другая программа. Сначала остановите её.","execution"));return;
        }
        if(code==null||code.length()>128000||exerciseId==null||!exerciseId.matches("p[0-9]{2,4}")
                ||!("practice".equals(variant)||"transfer".equals(variant))) {
            emit("result",requestId,"result",result("error","Некорректные параметры программы или слишком большой исходник.","execution"));return;
        }
        activeRequest=requestId;
        timeoutMs=Math.max(50,Math.min(milliseconds,60000));
        queuedRun=new Bundle();queuedRun.putString("requestId",requestId);
        queuedRun.putString("exerciseId",exerciseId);queuedRun.putString("code",code);
        queuedRun.putString("variant",variant);
        if(ready)sendQueuedRun();else ensureBound();
    }
    private void ensureBound() {
        if(connection!=null||closed)return;
        final int epoch=++generation;
        final Messenger replies=new Messenger(new Handler(Looper.getMainLooper()) {
            @Override public void handleMessage(Message message) {
                if(epoch==generation&&!closed)onMessage(message);
            }
        });
        connection=new ServiceConnection() {
            @Override public void onServiceConnected(ComponentName name, IBinder binder) {
                if(epoch!=generation||closed)return;
                service=new Messenger(binder);
                Message hello=Message.obtain(null,PythonService.HELLO);hello.replyTo=replies;
                try { service.send(hello); }
                catch(RemoteException error) { failRuntime("Не удалось связаться с процессом Python.","initialization"); }
            }
            @Override public void onServiceDisconnected(ComponentName name) {
                if(epoch==generation&&!closed)failRuntime("Процесс Python завершился. Повторите запуск; исходник сохранён.",ready?"execution":"initialization");
            }
            @Override public void onBindingDied(ComponentName name) { onServiceDisconnected(name); }
            @Override public void onNullBinding(ComponentName name) { onServiceDisconnected(name); }
        };
        initializationDeadline=()->{
            if(epoch==generation&&!ready)failRuntime("Подготовка Python заняла слишком много времени. Повторите запуск.","initialization");
        };
        handler.postDelayed(initializationDeadline,120000);
        try {
            if(!activity.bindService(new Intent(activity,PythonService.class),connection,Context.BIND_AUTO_CREATE))
                failRuntime("Не удалось открыть процесс Python.","initialization");
        } catch(Exception error) { failRuntime("Не удалось открыть Python: "+error.getMessage(),"initialization"); }
    }
    private void onMessage(Message message) {
        Bundle data=message.getData();
        String id=data.getString("requestId");
        if(message.what==PythonService.PID) {
            int reported=data.getInt("pid");if(reported>0&&reported!=Process.myPid())childPid=reported;
        } else if(message.what==PythonService.READY) {
            ready=true;pythonVersion=data.getString("pythonVersion","3.12.15");
            int reported=data.getInt("pid");if(reported>0&&reported!=Process.myPid())childPid=reported;
            if(initializationDeadline!=null)handler.removeCallbacks(initializationDeadline);
            initializationDeadline=null;
            for(String requestId:initializations)emit("ready",requestId,"pythonVersion",pythonVersion);
            initializations.clear();
            sendQueuedRun();
        } else if(message.what==PythonService.STARTED&&activeRequest!=null&&activeRequest.equals(id)) {
            if(executionDeadline!=null)handler.removeCallbacks(executionDeadline);
            final int epoch=generation;final String running=id;
            executionDeadline=()->{
                if(epoch!=generation||!running.equals(activeRequest))return;
                activeRequest=null;queuedRun=null;
                emit("result",running,"result",result("timeout","Превышен лимит "+(timeoutMs/1000.0)+" с. Проверьте цикл или рекурсию.","execution"));
                resetProcess("Процесс Python остановлен по лимиту времени.");
            };
            handler.postDelayed(executionDeadline,timeoutMs);
            emit("status",id,"message","Выполняется Python на устройстве…");
        } else if(message.what==PythonService.RESULT&&activeRequest!=null&&activeRequest.equals(id)) {
            if(executionDeadline!=null)handler.removeCallbacks(executionDeadline);
            executionDeadline=null;activeRequest=null;queuedRun=null;
            try {
                String json=data.getString("resultJson","");
                if(json.length()>524288)throw new IllegalArgumentException("Ответ превышает допустимый размер.");
                JSONObject parsed=new JSONObject(json);
                if(!parsed.has("status"))throw new IllegalArgumentException("Нет статуса выполнения.");
                emit("result",id,"result",parsed);
            } catch(Exception error) { emit("result",id,"result",result("error","Некорректный ответ Python: "+error.getMessage(),"execution")); }
        } else if(message.what==PythonService.ERROR) {
            String phase=data.getString("phase","execution");
            String error=data.getString("message","Ошибка среды Python.");
            if("initialization".equals(phase))failRuntime(error,phase);
            else if(activeRequest!=null&&activeRequest.equals(id)) {
                if(executionDeadline!=null)handler.removeCallbacks(executionDeadline);
                executionDeadline=null;activeRequest=null;queuedRun=null;
                emit("result",id,"result",result("error",error,phase));
            }
        } else if(message.what==PythonService.STATUS) {
            String text=data.getString("message","Подготовка Python…");
            for(String requestId:initializations)emit("status",requestId,"message",text);
            if(activeRequest!=null)emit("status",activeRequest,"message",text);
        }
    }
    private void sendQueuedRun() {
        if(!ready||service==null||queuedRun==null)return;
        Message message=Message.obtain(null,PythonService.RUN);message.setData(queuedRun);
        queuedRun=null;
        try { service.send(message); }
        catch(RemoteException error) { failRuntime("Связь с Python прервана. Повторите запуск.","execution"); }
    }
    private void failRuntime(String message,String phase) {
        if(activeRequest!=null) {
            emit("result",activeRequest,"result",result("error",message,phase));activeRequest=null;
        }
        for(String id:initializations)emit("init-error",id,"message",message,"result",result("error",message,"initialization"));
        initializations.clear();queuedRun=null;
        resetProcess(message);
    }
    void stop(String requestId) {
        if(closed)return;
        if(activeRequest!=null) {
            emit("result",activeRequest,"result",result("cancelled","Выполнение остановлено. Исходник сохранён.","execution"));activeRequest=null;
        }
        for(String id:initializations)emit("init-error",id,"message","Подготовка Python остановлена.","result",result("cancelled","Подготовка Python остановлена.","initialization"));
        initializations.clear();queuedRun=null;
        resetProcess("Среда будет восстановлена при следующем запуске.");
    }
    private void resetProcess(String reason) {
        ++generation;ready=false;
        if(initializationDeadline!=null)handler.removeCallbacks(initializationDeadline);
        if(executionDeadline!=null)handler.removeCallbacks(executionDeadline);
        initializationDeadline=executionDeadline=null;
        ServiceConnection old=connection;connection=null;service=null;
        int oldPid=childPid;childPid=0;
        if(old!=null)try{activity.unbindService(old);}catch(Exception ignored){}
        try{activity.stopService(new Intent(activity,PythonService.class));}catch(Exception ignored){}
        if(oldPid>0&&oldPid!=Process.myPid())Process.killProcess(oldPid);
        emit("reset",null,"message",reason);
    }
    void close() { if(!closed){stop(null);closed=true;} }
}
