const bridge=window.MamMoNative;
if(bridge){
 let current=null;const events=new EventTarget();
 function Utterance(text){this.text=text||'';this.lang='vi-VN';this.rate=1;this.voice=null;}
 window.__mammoSpeechEvent=(id,type)=>{if(!current||current.id!==id)return;const u=current.utterance;if(type==='start')u.onstart?.({});else{current=null;if(type==='end')u.onend?.({});else u.onerror?.({error:'synthesis-failed'});}};
 const synthesis={getVoices(){try{return JSON.parse(bridge.voices());}catch{return []; }},speak(u){this.cancel();const id=String(Date.now())+'-'+Math.random().toString(16).slice(2);current={id,utterance:u};bridge.speak(id,u.text,u.lang||u.voice?.lang||'vi-VN',Number(u.rate)||1);},cancel(){current=null;bridge.stop();},addEventListener:events.addEventListener.bind(events),removeEventListener:events.removeEventListener.bind(events)};
 Object.defineProperty(window,'SpeechSynthesisUtterance',{configurable:true,value:Utterance});Object.defineProperty(window,'speechSynthesis',{configurable:true,value:synthesis});
}
