package ru.washeratlas.app;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.*;
import android.view.View;
import android.widget.Toast;
import java.io.*;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;

/** Offline local WebView. No Internet or storage permissions; documents use SAF. */
public final class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final int PICK = 20, SAVE = 21;
    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private String pendingExport;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(244,246,245));
        setContentView(web);
        // Android 15 enforces edge-to-edge: retain safe system-bar padding.
        web.setOnApplyWindowInsetsListener((v, insets) -> {
            v.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                    insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportMultipleWindows(false);
        web.addJavascriptInterface(new ExportOnly(), "AndroidFiles");
        web.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if (!"https".equals(uri.getScheme()) || !HOST.equals(uri.getHost())) return blocked();
                String path = uri.getPath();
                if (path == null || path.equals("/")) path = "/index.html";
                // Only bundled, explicit files are reachable; never expose arbitrary local paths.
                if (!(path.equals("/index.html") || path.equals("/style.css") || path.equals("/app.js") || path.equals("/core.js") || path.equals("/catalog.json"))) return blocked();
                String mime = path.endsWith(".html") ? "text/html" : path.endsWith(".css") ? "text/css" : path.endsWith(".json") ? "application/json" : "application/javascript";
                try { return new WebResourceResponse(mime, "UTF-8", getAssets().open(path.substring(1))); }
                catch (IOException e) { return blocked(); }
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u=request.getUrl();
                if (HOST.equals(u.getHost()) && "https".equals(u.getScheme())) return false;
                if (request.isForMainFrame() && ("https".equals(u.getScheme()) || "http".equals(u.getScheme()))) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, u)); }
                    catch (ActivityNotFoundException e) { message("Нет приложения для открытия ссылки"); }
                }
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback!=null) fileCallback.onReceiveValue(null);
                fileCallback=callback;
                Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("*/*");
                intent.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/json","text/plain","application/octet-stream"});
                try { startActivityForResult(intent,PICK); }
                catch (ActivityNotFoundException e) { fileCallback.onReceiveValue(null); fileCallback=null; message("Системный выбор файла недоступен"); }
                return true;
            }
            @Override public boolean onJsConfirm(WebView view,String url,String message,JsResult result) {
                new android.app.AlertDialog.Builder(MainActivity.this).setMessage(message)
                    .setPositiveButton("Продолжить",(d,w)->result.confirm())
                    .setNegativeButton("Отмена",(d,w)->result.cancel())
                    .setOnCancelListener(d->result.cancel()).show(); return true;
            }
        });
        if(state!=null) pendingExport=state.getString("pendingExport");
        web.loadUrl("https://"+HOST+"/index.html");
    }
    private static WebResourceResponse blocked() { return new WebResourceResponse("text/plain", "UTF-8",404,"Not Found",java.util.Collections.emptyMap(),new ByteArrayInputStream(new byte[0])); }
    private void message(String text) { runOnUiThread(()->Toast.makeText(this,text,Toast.LENGTH_LONG).show()); }
    private final class ExportOnly {
        @JavascriptInterface public void save(String json) {
            if(json==null || json.length()>5*1024*1024) { message("Слишком большой файл экспорта"); return; }
            try { new JSONObject(json); } catch(Exception e) { message("Некорректный JSON"); return; }
            runOnUiThread(()->{
                if(pendingExport!=null){message("Завершите предыдущее сохранение");return;}
                pendingExport=json;
                Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType("application/json");intent.putExtra(Intent.EXTRA_TITLE,"mastercode-backup.json");
                try { startActivityForResult(intent,SAVE); }
                catch(ActivityNotFoundException e){pendingExport=null;message("Сохранение файла недоступно");}
            });
        }
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request==PICK && fileCallback!=null) {
            fileCallback.onReceiveValue(result==RESULT_OK && data!=null && data.getData()!=null?new Uri[]{data.getData()}:null);fileCallback=null;
        } else if(request==SAVE) {
            String text=pendingExport;pendingExport=null;
            if(result==RESULT_OK && data!=null && data.getData()!=null && text!=null) {
                Uri uri=data.getData();
                new Thread(()->{try(OutputStream stream=getContentResolver().openOutputStream(uri,"wt")) {
                    if(stream==null)throw new IOException();stream.write(text.getBytes(StandardCharsets.UTF_8));message("Резервная копия сохранена");
                } catch(IOException|SecurityException e){message("Не удалось сохранить резервную копию");}}).start();
            }
        }
    }
    @Override protected void onSaveInstanceState(Bundle state){super.onSaveInstanceState(state);if(pendingExport!=null && pendingExport.length()<100000)state.putString("pendingExport",pendingExport);}
    @Override public void onBackPressed(){web.evaluateJavascript("(function(){var m=document.getElementById('modal');if(m&&!m.hidden){closeModal();return true}return false})()",value->{if(!"true".equals(value))super.onBackPressed();});}
    @Override protected void onDestroy(){if(fileCallback!=null)fileCallback.onReceiveValue(null);web.removeJavascriptInterface("AndroidFiles");web.destroy();super.onDestroy();}
}
