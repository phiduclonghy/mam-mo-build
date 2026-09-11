// Each track owns a cancellation token: a late play/error cannot restart an old page.
let context;
function getContext(){const C=globalThis.AudioContext||globalThis.webkitAudioContext;if(!context&&C)context=new C();return context;}
export class AudioTrack{
 constructor({onState=()=>{},onError=()=>{},makeAudio=()=>new Audio(),audioContext=getContext}={}){
  this.audio=makeAudio();this.audio.preload='none';this.audio.setAttribute('playsinline','');
  this.onState=onState;this.onError=onError;this.audioContext=audioContext;this.token=0;this.active=false;
 }
 stop(){this.token++;this.audio.onended=null;this.audio.onerror=null;this.audio.pause();try{this.audio.currentTime=0;}catch{}this.active=false;this.onState(false);}
 async play(url,{volume=1,rate=1,loop=false}={}){
  this.stop();const token=this.token;this.audio.src=url;this.audio.loop=loop;this.audio.playbackRate=rate;this.active=true;this.onState(true);
  const fail=error=>{if(token!==this.token)return;this.stop();this.onError(error);};
  this.audio.onended=()=>{if(token===this.token)this.stop();};this.audio.onerror=()=>fail(Error('Không đọc được tệp âm thanh.'));
  try{
   const ctx=this.audioContext();
   if(ctx&&!this.gain){const source=ctx.createMediaElementSource(this.audio);this.gain=ctx.createGain();source.connect(this.gain);this.gain.connect(ctx.destination);}
   if(this.gain)this.gain.gain.value=volume;else this.audio.volume=volume;
   // Start both synchronously inside the click gesture, including on iPhone.
   const resume=ctx?.state==='suspended'?ctx.resume():Promise.resolve();const play=this.audio.play();
   await Promise.all([resume,play]);
  }catch(error){fail(error);}
 }
}
export function narrationSource(story,page,language){return story?.pages?.[page]?.[language==='en'?'audioEn':'audioVi']||null;}
