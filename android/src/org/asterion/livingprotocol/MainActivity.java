package org.asterion.livingprotocol;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.res.AssetManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.view.WindowInsets;
import android.graphics.Rect;
import android.widget.FrameLayout;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.RenderProcessGoneDetail;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;

/** Offline game host. No account, analytics, external API or remote assets. */
public final class MainActivity extends Activity {
    private static final int EXPORT_SAVE = 401, IMPORT_SAVE = 402, MAX_SAVE = 8 * 1024 * 1024;
    private WebView web;
    private AssetServer server;
    private SaveStore saves;
    private PythonHost pythonHost;
    private byte[] pendingExport;
    private String base;
    private boolean pageReady, diagnostics;

    @Override public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        saves = new SaveStore(new File(getFilesDir(), "novel-v2"));
        diagnostics = getIntent().getBooleanExtra("diagnostics", false)
            && Settings.Global.getInt(getContentResolver(), Settings.Global.ADB_ENABLED, 0) != 0;
        try {
            server = new AssetServer(getAssets(), diagnostics);
            server.start();
            base = "http://127.0.0.1:" + server.port() + "/";
            web = new WebView(this);
            pythonHost = new PythonHost(this, event -> {
                if(web!=null)web.post(()->{
                    if(web!=null)web.evaluateJavascript("if(window.onNativePythonMessage){window.onNativePythonMessage("+JSONObject.quote(event.toString())+");}",null);
                });
            });
            web.setBackgroundColor(0xff071b22);
            WebSettings settings = web.getSettings();
            settings.setJavaScriptEnabled(true);
            settings.setDomStorageEnabled(true);
            settings.setDatabaseEnabled(true);
            settings.setAllowFileAccess(false);
            settings.setAllowContentAccess(false);
            settings.setMediaPlaybackRequiresUserGesture(true);
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
            settings.setSupportZoom(false);
            settings.setUseWideViewPort(true);
            settings.setLoadWithOverviewMode(true);
            settings.setCacheMode(WebSettings.LOAD_DEFAULT);
            // Both an explicit diagnostic launch and enabled ADB are required.
            WebView.setWebContentsDebuggingEnabled(diagnostics);
            web.addJavascriptInterface(new Bridge(), "Android");
            web.setWebChromeClient(new WebChromeClient() {
                @Override public boolean onConsoleMessage(android.webkit.ConsoleMessage message) {
                    if (diagnostics)
                        Log.d("AsterionWeb", message.messageLevel() + ": " + message.message());
                    return true;
                }
            });
            web.setWebViewClient(new WebViewClient() {
                @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                    String target = request.getUrl().toString();
                    if (target.startsWith(base)) return false;
                    if (request.hasGesture() && "https".equals(request.getUrl().getScheme())) {
                        try {startActivity(new Intent(Intent.ACTION_VIEW, request.getUrl()));}
                        catch (Exception ignored) {showMessage("Нет приложения для открытия этой ссылки.");}
                    }
                    return true;
                }
                @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                    String target = request.getUrl().toString();
                    if (target.startsWith(base) || target.startsWith("blob:") || target.startsWith("data:")) return null;
                    return new WebResourceResponse("text/plain", "UTF-8", 403, "Offline",
                        Collections.singletonMap("Cache-Control", "no-store"),
                        new ByteArrayInputStream("External resource blocked".getBytes(StandardCharsets.UTF_8)));
                }
                @Override public void onPageFinished(WebView view, String url) {
                    pageReady = true;
                    Log.i("Asterion", "GAME_PAGE_READY");
                }
                @Override public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
                    pageReady=false;
                    if(pythonHost!=null)pythonHost.stop(null);
                    Log.e("Asterion","WEBVIEW_RENDERER_STOPPED crashed="+detail.didCrash());
                    view.removeJavascriptInterface("Android");
                    setContentView(new android.widget.FrameLayout(MainActivity.this));
                    view.destroy();web=null;
                    new AlertDialog.Builder(MainActivity.this).setTitle("Среда отображения остановилась")
                        .setMessage("Последнее сохранение осталось в памяти устройства. Перезапустите игру; если ошибка повторится, обновите Android System WebView.")
                        .setPositiveButton("Перезапустить",(dialog,which)->recreate())
                        .setNegativeButton("Закрыть",(dialog,which)->finish()).setCancelable(false).show();
                    return true;
                }
            });
            FrameLayout viewport = new FrameLayout(this);
            viewport.addView(web, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
            // Immersive edge-to-edge windows do not reliably honor adjustResize.
            // Resize the actual WebView so its CSS viewport and focused editor
            // remain above the keyboard, instead of merely painting over it.
            if (Build.VERSION.SDK_INT >= 30) {
                viewport.setOnApplyWindowInsetsListener((view, insets) -> {
                    int keyboard = 0;
                    if (insets.isVisible(WindowInsets.Type.ime())) {
                        int[] position = new int[2]; view.getLocationOnScreen(position);
                        int keyboardTop = getWindowManager().getCurrentWindowMetrics().getBounds().bottom
                            - insets.getInsets(WindowInsets.Type.ime()).bottom;
                        keyboard = Math.max(0, position[1] + view.getHeight() - keyboardTop);
                    }
                    if (view.getPaddingBottom() != keyboard) view.setPadding(0, 0, 0, keyboard);
                    return insets;
                });
            } else {
                viewport.getViewTreeObserver().addOnGlobalLayoutListener(() -> {
                    Rect visible = new Rect(); viewport.getWindowVisibleDisplayFrame(visible);
                    int[] position = new int[2]; viewport.getLocationOnScreen(position);
                    int height = viewport.getHeight();
                    int obscured = Math.max(0, position[1] + height - visible.bottom);
                    int keyboard = obscured > height / 5 ? obscured : 0;
                    if (viewport.getPaddingBottom() != keyboard) viewport.setPadding(0, 0, 0, keyboard);
                });
            }
            setContentView(viewport);
            viewport.requestApplyInsets();
            immersive();
            web.loadUrl(base + "index.html");
        } catch (Exception error) {
            showMessage("Не удалось запустить локальную игру: " + error.getMessage());
        }
    }
    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }
    @Override public void onWindowFocusChanged(boolean focus) {super.onWindowFocusChanged(focus);if(focus)immersive();}
    @Override protected void onPause() {
        if (web != null && pageReady) web.evaluateJavascript(
            "if(window.onAppPause){window.onAppPause();}else{document.dispatchEvent(new Event('asterionpause'));}", null);
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume();
        if (web != null) {
            web.onResume();
            web.evaluateJavascript("if(window.onAppResume){window.onAppResume();}", null);
            immersive();
        }
    }
    @Override protected void onDestroy() {
        if(pythonHost!=null)pythonHost.close();
        if (web != null) {WebView previous=web;web=null;previous.removeJavascriptInterface("Android");previous.destroy();}
        if (server != null) server.close();
        super.onDestroy();
    }
    @Override public void onBackPressed() {
        if (web != null) web.evaluateJavascript(
            "if(window.onNativeBack){window.onNativeBack();}else if(window.onAppPause){window.onAppPause();}", null);
    }
    private void showMessage(String message) {
        runOnUiThread(() -> new AlertDialog.Builder(this).setTitle("Астерион").setMessage(message)
            .setPositiveButton("Понятно", (d,w) -> {}).show());
    }
    private static String failure(Exception e) {
        try {return new JSONObject().put("ok", false).put("error", e.getMessage() == null ? e.toString() : e.getMessage()).toString();}
        catch (Exception ignored) {return "{\"ok\":false,\"error\":\"Ошибка данных\"}";}
    }
    public final class Bridge {
        @JavascriptInterface public String appVersion(){return "2.1.0";}
        @JavascriptInterface public String loadSave(){return saves.load();}
        @JavascriptInterface public String saveState(String state){return saves.save(state);}
        @JavascriptInterface public String recoverSave(){return saves.recover();}
        @JavascriptInterface public void pythonInit(String requestId){runOnUiThread(()->{if(pythonHost!=null)pythonHost.init(requestId);});}
        @JavascriptInterface public void pythonRun(String requestId,String exerciseId,String code,String variant,int timeoutMs){
            runOnUiThread(()->{if(pythonHost!=null)pythonHost.run(requestId,exerciseId,code,variant,timeoutMs);});
        }
        @JavascriptInterface public void pythonStop(String requestId){runOnUiThread(()->{if(pythonHost!=null)pythonHost.stop(requestId);});}
        @JavascriptInterface public String getDiagnostics(){
            try {
                JSONObject info = new JSONObject().put("platform", "Android").put("sdk", Build.VERSION.SDK_INT)
                    .put("appVersion", "2.1.0").put("campaignEdition", "elf-beauties-v2").put("offlineAssets", true).put("nativeSave", true)
                    .put("python", "CPython 3.12.15 / Chaquopy 17.2.0, separate native process")
                    .put("pythonBackend","native").put("pythonProcessPid",pythonHost==null?0:pythonHost.pid())
                    .put("pythonReady",pythonHost!=null&&pythonHost.isReady())
                    .put("supportedAbis",new JSONArray(Arrays.asList(Build.SUPPORTED_ABIS))).put("port", server.port());
                if (Build.VERSION.SDK_INT >= 26 && WebView.getCurrentWebViewPackage() != null)
                    info.put("webView", WebView.getCurrentWebViewPackage().versionName);
                return info.toString();
            } catch (Exception e){return failure(e);}
        }
        @JavascriptInterface public void exportSave(){
            try {
                String exported = saves.load();
                JSONObject parsed = new JSONObject(exported);
                if (parsed.has("error")) throw new IOException(parsed.getString("error"));
                if (!parsed.has("payload")) throw new IOException("Пока нет сохранённой игры.");
                pendingExport = exported.getBytes(StandardCharsets.UTF_8);
                runOnUiThread(() -> {
                    Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE)
                        .setType("application/json").putExtra(Intent.EXTRA_TITLE, "asterion-elf-beauties-v2-save.json");
                    startActivityForResult(intent, EXPORT_SAVE);
                });
            } catch(Exception e){showMessage("Экспорт не выполнен: " + e.getMessage());}
        }
        @JavascriptInterface public void importSave(){
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE)
                    .setType("application/json");
                startActivityForResult(intent, IMPORT_SAVE);
            });
        }
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request,result,data);
        if (result != RESULT_OK || data == null || data.getData() == null) return;
        try {
            if (request == EXPORT_SAVE && pendingExport != null) {
                try (OutputStream out = getContentResolver().openOutputStream(data.getData(), "wt")) {
                    if(out == null)throw new IOException("Файл не открыт");
                    out.write(pendingExport);out.flush();
                }
                pendingExport = null;showMessage("Копия сохранения записана.");
            } else if (request == IMPORT_SAVE) {
                byte[] content;
                try (InputStream in = getContentResolver().openInputStream(data.getData())) {content=readBounded(in, MAX_SAVE);}
                String envelope = saves.importEnvelope(new String(content,StandardCharsets.UTF_8));
                JSONObject parsed = new JSONObject(envelope);
                if(parsed.has("error"))throw new IOException(parsed.getString("error"));
                web.evaluateJavascript("if(window.onNativeImport){window.onNativeImport("+JSONObject.quote(envelope)+");}",null);
            }
        } catch(Exception e){showMessage("Операция с сохранением не выполнена: "+e.getMessage());}
    }
    private static byte[] readBounded(InputStream in,int limit)throws IOException{
        if(in==null)throw new IOException("Нет потока данных");
        ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] chunk=new byte[32768];int n;
        while((n=in.read(chunk))!=-1){if(out.size()+n>limit)throw new IOException("Файл слишком большой");out.write(chunk,0,n);}
        return out.toByteArray();
    }

    /** Transactional private app save, with checksum and retained prior working copy. */
    static final class SaveStore {
        final File primary, backup, directory;String blocked;
        SaveStore(File directory){this.directory=directory;directory.mkdirs();primary=new File(directory,"save.json");backup=new File(directory,"save.previous.json");}
        static String digest(String text)throws Exception{
            byte[] bytes=MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8));
            StringBuilder out=new StringBuilder();for(byte b:bytes)out.append(String.format(Locale.ROOT,"%02x",b&255));return out.toString();
        }
        JSONObject validate(String raw)throws Exception{
            if(raw.getBytes(StandardCharsets.UTF_8).length>MAX_SAVE)throw new IOException("Сохранение превышает 8 МБ.");
            JSONObject envelope=new JSONObject(raw);
            if(!"asterion-save".equals(envelope.optString("format"))||envelope.optInt("version")!=2)
                throw new IOException("Неподдерживаемый формат сохранения.");
            String payload=envelope.getString("payload");
            JSONObject state=new JSONObject(payload);
            if(!"elf-beauties-v2".equals(state.optString("campaignEdition")))
                throw new IOException("Это сохранение другой редакции Астериона. Для обновлённой учебной истории нужен отдельный прогресс; прежнее сохранение остаётся в старой редакции.");
            if(state.optInt("version")!=2||!(state.opt("levels") instanceof JSONObject)||!(state.opt("completed") instanceof JSONArray))
                throw new IOException("Повреждена структура прогресса.");
            if(!digest(payload).equals(envelope.optString("checksum")))
                throw new IOException("Контрольная сумма сохранения не совпадает.");
            return envelope;
        }
        String read(File file)throws Exception{try(InputStream in=new FileInputStream(file)){return new String(readBounded(in,MAX_SAVE),StandardCharsets.UTF_8);}}
        void atomic(File destination,String value)throws Exception{
            File tmp=new File(directory,destination.getName()+".tmp");
            try(FileOutputStream out=new FileOutputStream(tmp)){out.write(value.getBytes(StandardCharsets.UTF_8));out.flush();out.getFD().sync();}
            try{Files.move(tmp.toPath(),destination.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException e){Files.move(tmp.toPath(),destination.toPath(),StandardCopyOption.REPLACE_EXISTING);}
        }
        synchronized String load(){
            try{
                if(!primary.exists()){
                    if(backup.exists())throw new IOException("Основное сохранение отсутствует. Восстановите резервную копию.");
                    return new JSONObject().put("format","asterion-save").put("version",2).put("state",JSONObject.NULL).toString();
                }
                JSONObject valid=validate(read(primary));blocked=null;return valid.toString();
            }catch(Exception e){
                blocked=e.getMessage();
                try{return new JSONObject().put("error",blocked).put("recoveryAvailable",backup.exists()).toString();}
                catch(Exception ignored){return failure(e);}
            }
        }
        synchronized String save(String raw){
            try{
                if(blocked!=null)throw new IOException("Сначала восстановите или импортируйте сохранение: "+blocked);
                JSONObject envelope=new JSONObject().put("format","asterion-save").put("version",2)
                    .put("savedAt",System.currentTimeMillis()).put("checksum",digest(raw)).put("payload",raw);
                String value=envelope.toString();validate(value);
                if(primary.exists()){
                    String old;
                    try{old=read(primary);validate(old);}
                    catch(Exception e){blocked=e.getMessage();throw e;}
                    atomic(backup,old);
                }
                atomic(primary,value);
                return new JSONObject().put("ok",true).put("savedAt",envelope.getLong("savedAt")).toString();
            }catch(Exception e){return failure(e);}
        }
        synchronized String recover(){
            try{
                String prior=read(backup);validate(prior);
                if(primary.exists())atomic(new File(directory,"save.damaged."+System.currentTimeMillis()+".json"),read(primary));
                atomic(primary,prior);blocked=null;return prior;
            }catch(Exception e){return failure(e);}
        }
        synchronized String importEnvelope(String raw){
            try{
                JSONObject imported=validate(raw);
                if(primary.exists()){
                    String old=read(primary);
                    try{validate(old);atomic(backup,old);}catch(Exception e){atomic(new File(directory,"save.damaged."+System.currentTimeMillis()+".json"),old);}
                }
                atomic(primary,imported.toString());blocked=null;return imported.toString();
            }catch(Exception e){return failure(e);}
        }
    }

    /** Read-only loopback server for packaged web assets; no filesystem or API routes. */
    static final class AssetServer {
        final AssetManager assets;final ServerSocket socket;final ExecutorService clients=Executors.newFixedThreadPool(6);final boolean diagnostics;
        volatile boolean running=true;
        AssetServer(AssetManager assets,boolean diagnostics)throws IOException{this.assets=assets;this.diagnostics=diagnostics;socket=new ServerSocket(0,32,InetAddress.getByName("127.0.0.1"));}
        int port(){return socket.getLocalPort();}
        void start(){Thread thread=new Thread(()->{while(running){try{Socket client=socket.accept();clients.execute(()->serve(client));}catch(IOException e){if(running)Log.e("Asterion","Asset server accept failed");}}},"AsterionAssets");thread.setDaemon(true);thread.start();}
        void close(){running=false;try{socket.close();}catch(IOException ignored){}clients.shutdownNow();}
        void serve(Socket client){
            try(Socket connection=client){
                connection.setSoTimeout(15000);
                BufferedReader reader=new BufferedReader(new InputStreamReader(connection.getInputStream(),StandardCharsets.US_ASCII));
                String first=reader.readLine();if(first==null||first.length()>8192)return;
                String[] parts=first.split(" ");if(parts.length<2)return;
                int count=0;String line;while((line=reader.readLine())!=null&&!line.isEmpty()){if(++count>80)return;}
                if(!parts[0].equals("GET")&&!parts[0].equals("HEAD")){respond(connection,405,"text/plain","Method not allowed".getBytes(StandardCharsets.UTF_8),false);return;}
                String path=URLDecoder.decode(parts[1].split("\\?",2)[0],"UTF-8");
                if(diagnostics)Log.d("AsterionAssets",parts[0]+" "+path);
                if(path.equals("/"))path="/index.html";
                if(path.contains("..")||path.contains("\\")||path.indexOf(0)>=0){respond(connection,403,"text/plain",new byte[0],false);return;}
                try(InputStream asset=assets.open("web"+path,AssetManager.ACCESS_STREAMING)){
                    // Resources are small enough for bounded reads; wasm compressed in APK decompresses once per worker boot.
                    byte[] bytes=readBounded(asset,64*1024*1024);
                    respond(connection,200,mime(path),bytes,parts[0].equals("HEAD"));
                }catch(FileNotFoundException e){respond(connection,404,"text/plain",("Not found: "+path).getBytes(StandardCharsets.UTF_8),false);}
            }catch(Exception e){Log.d("Asterion","Asset connection ended: "+e.getClass().getSimpleName());}
        }
        static String mime(String p){
            if(p.endsWith(".html"))return "text/html; charset=utf-8";
            if(p.endsWith(".js")||p.endsWith(".mjs"))return "text/javascript; charset=utf-8";
            if(p.endsWith(".css"))return "text/css; charset=utf-8";
            if(p.endsWith(".json"))return "application/json; charset=utf-8";
            if(p.endsWith(".wasm"))return "application/wasm";
            if(p.endsWith(".zip")||p.endsWith(".whl"))return "application/zip";
            if(p.endsWith(".png"))return "image/png";
            if(p.endsWith(".webp"))return "image/webp";
            if(p.endsWith(".svg"))return "image/svg+xml";
            if(p.endsWith(".py")||p.endsWith(".txt"))return "text/plain; charset=utf-8";
            return "application/octet-stream";
        }
        static void respond(Socket socket,int status,String mime,byte[] body,boolean head)throws IOException{
            OutputStream out=socket.getOutputStream();
            String headers="HTTP/1.1 "+status+" "+(status==200?"OK":"Error")+"\r\nContent-Type: "+mime+
                "\r\nContent-Length: "+body.length+"\r\nConnection: close\r\nCache-Control: no-cache"+
                "\r\nCross-Origin-Opener-Policy: same-origin\r\nCross-Origin-Embedder-Policy: require-corp"+
                "\r\nCross-Origin-Resource-Policy: same-origin\r\nX-Content-Type-Options: nosniff\r\n\r\n";
            out.write(headers.getBytes(StandardCharsets.US_ASCII));if(!head)out.write(body);out.flush();
        }
    }
}
