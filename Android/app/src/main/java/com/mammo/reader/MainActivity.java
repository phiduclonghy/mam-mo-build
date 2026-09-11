package com.mammo.reader;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.graphics.Color;
import android.view.View;
import android.webkit.*;
import android.widget.*;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

/** Offline assets stay on an intercepted HTTPS origin. No auth tokens are embedded. */
public final class MainActivity extends Activity {
 private static final String ORIGIN="https://appassets.androidplatform.net";
 private static final String ONLINE="https://mam-mo-book-1109.margaretevansa9281.chatgpt.site";
 private static final int PICK_IMAGE=7001;
 private WebView web;
 private TextToSpeech tts;
 private volatile boolean ttsReady=false;
 private ValueCallback<Uri[]> chooser;
 @Override public void onCreate(Bundle saved){super.onCreate(saved);
  getWindow().setStatusBarColor(Color.rgb(23,63,57));
  LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(Color.rgb(250,248,242));root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(0,insets.getSystemWindowInsetTop(),0,insets.getSystemWindowInsetBottom());return insets;});
  LinearLayout toolbar=new LinearLayout(this);toolbar.setPadding(14,8,14,8);toolbar.setGravity(android.view.Gravity.CENTER_VERTICAL);
  TextView label=new TextView(this);label.setText("Mầm Mơ · Đọc trên máy");label.setTextColor(Color.rgb(23,63,57));label.setTextSize(16);toolbar.addView(label,new LinearLayout.LayoutParams(0,-2,1));
  Button online=new Button(this);online.setText("Website ↗");online.setOnClickListener(v->startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(ONLINE))));toolbar.addView(online);
  root.addView(toolbar);web=new WebView(this);root.addView(web,new LinearLayout.LayoutParams(-1,0,1));setContentView(root);
  WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);settings.setAllowFileAccess(false);settings.setAllowContentAccess(true);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);settings.setMediaPlaybackRequiresUserGesture(true);
  tts=new TextToSpeech(this,status->{ttsReady=status==TextToSpeech.SUCCESS;});
  tts.setOnUtteranceProgressListener(new UtteranceProgressListener(){public void onStart(String id){String[] p=id.split("\\|");if(p.length==3&&p[1].equals("0"))speechEvent(p[0],"start");}public void onDone(String id){String[] p=id.split("\\|");if(p.length==3&&Integer.parseInt(p[1])==Integer.parseInt(p[2])-1)speechEvent(p[0],"end");}public void onError(String id){speechEvent(id.split("\\|")[0],"error");}});
  web.addJavascriptInterface(new SpeechBridge(),"MamMoNative");
  web.setWebViewClient(new WebViewClient(){
   @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request){Uri uri=request.getUrl();if(!"appassets.androidplatform.net".equals(uri.getHost()))return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));String path=uri.getPath();if(path==null||path.equals("/"))path="/index.html";if(path.contains("..")||path.indexOf('\0')>=0)return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));try{return new WebResourceResponse(mime(path),isText(path)?"UTF-8":null,getAssets().open("web"+path));}catch(IOException e){return new WebResourceResponse("text/plain","UTF-8",404,"Not Found",Collections.emptyMap(),new ByteArrayInputStream(new byte[0]));}}
   @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){Uri uri=request.getUrl();if("appassets.androidplatform.net".equals(uri.getHost()))return false;if("https".equals(uri.getScheme())&&request.isForMainFrame())startActivity(new Intent(Intent.ACTION_VIEW,uri));return true;}
  });
  web.setWebChromeClient(new WebChromeClient(){@Override public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params){if(chooser!=null)chooser.onReceiveValue(null);chooser=callback;Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);boolean audioFile=false;for(String accepted:params.getAcceptTypes()){if(accepted.startsWith("audio/")||accepted.equals(".mp3")||accepted.equals(".m4a")||accepted.equals(".wav")){audioFile=true;break;}}intent.setType(audioFile?"audio/*":"image/*");intent.addCategory(Intent.CATEGORY_OPENABLE);try{startActivityForResult(intent,PICK_IMAGE);}catch(Exception e){chooser.onReceiveValue(null);chooser=null;}return true;}});
  if(saved!=null)web.restoreState(saved);else web.loadUrl(ORIGIN+"/index.html");
 }
 private boolean isText(String p){return p.endsWith(".html")||p.endsWith(".css")||p.endsWith(".js")||p.endsWith(".json")||p.endsWith(".svg");}
 private String mime(String p){if(p.endsWith(".html"))return "text/html";if(p.endsWith(".js"))return "application/javascript";if(p.endsWith(".css"))return "text/css";if(p.endsWith(".json"))return "application/json";if(p.endsWith(".webp"))return "image/webp";if(p.endsWith(".png"))return "image/png";if(p.endsWith(".svg"))return "image/svg+xml";return "application/octet-stream";}
 private void speechEvent(String id,String event){runOnUiThread(()->{if(web!=null)web.evaluateJavascript("window.__mammoSpeechEvent && window.__mammoSpeechEvent("+JSONObject.quote(id)+","+JSONObject.quote(event)+")",null);});}
 public final class SpeechBridge {
  @JavascriptInterface public String voices(){JSONArray result=new JSONArray();if(!ttsReady)return result.toString();try{for(android.speech.tts.Voice voice:tts.getVoices()){String lang=voice.getLocale().toLanguageTag();if(lang.startsWith("vi")||lang.startsWith("en")){JSONObject value=new JSONObject();value.put("name",voice.getName());value.put("lang",lang);value.put("localService",!voice.isNetworkConnectionRequired());result.put(value);}}}catch(Exception ignored){}return result.toString();}
  @JavascriptInterface public void speak(String id,String text,String language,float rate){runOnUiThread(()->{if(!ttsReady){speechEvent(id,"error");return;}int available=tts.setLanguage(Locale.forLanguageTag(language));if(available<0){speechEvent(id,"error");return;}tts.setSpeechRate(Math.max(.5f,Math.min(rate,2f)));List<String> parts=new ArrayList<>();int cursor=0;while(cursor<text.length()){int end=Math.min(cursor+3500,text.length());if(end<text.length()){int space=text.lastIndexOf(" ",end);if(space>cursor)end=space;}parts.add(text.substring(cursor,end));cursor=end;}if(parts.isEmpty()){speechEvent(id,"end");return;}for(int i=0;i<parts.size();i++){int status=tts.speak(parts.get(i),i==0?TextToSpeech.QUEUE_FLUSH:TextToSpeech.QUEUE_ADD,new Bundle(),id+"|"+i+"|"+parts.size());if(status==TextToSpeech.ERROR){speechEvent(id,"error");break;}}});}
  @JavascriptInterface public void stop(){runOnUiThread(()->{if(tts!=null)tts.stop();});}
 }
 @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request==PICK_IMAGE&&chooser!=null){chooser.onReceiveValue(result==RESULT_OK&&data!=null&&data.getData()!=null?new Uri[]{data.getData()}:null);chooser=null;}}
 @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
 @Override protected void onSaveInstanceState(Bundle state){web.saveState(state);super.onSaveInstanceState(state);}
 @Override protected void onPause(){if(tts!=null)tts.stop();if(web!=null){web.evaluateJavascript("window.dispatchEvent(new Event(\"mammo-pause\"))",null);web.onPause();}super.onPause();}
 @Override protected void onResume(){super.onResume();if(web!=null)web.onResume();}
 @Override protected void onDestroy(){if(tts!=null){tts.stop();tts.shutdown();}if(web!=null){web.removeJavascriptInterface("MamMoNative");web.destroy();web=null;}super.onDestroy();}
}
