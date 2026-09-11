// Native editions keep stories locally. Online edition remains the separate signed-in Site.
import './mobile-speech.js';
const nativeFetch=window.fetch.bind(window);
const ready=new Promise((resolve,reject)=>{const open=indexedDB.open('mammo-native-stories',1);open.onupgradeneeded=()=>open.result.createObjectStore('stories',{keyPath:'id'});open.onsuccess=()=>resolve(open.result);open.onerror=()=>reject(open.error);});
function uid(){return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const n=crypto.getRandomValues(new Uint8Array(1))[0]%16;return (c==='x'?n:(n&3)|8).toString(16);});}
async function transact(mode,operation){const db=await ready;return new Promise((resolve,reject)=>{const tx=db.transaction('stories',mode),request=operation(tx.objectStore('stories'));let value;request.onsuccess=()=>{value=request.result;};request.onerror=()=>reject(request.error);tx.oncomplete=()=>resolve(value);tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error||Error('Lưu trữ đã bị hủy.'));});}
const reply=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json'}});
window.fetch=async(input,options={})=>{
 const url=new URL(typeof input==='string'?input:input.url,location.href),method=(options.method||'GET').toUpperCase();if(!url.pathname.startsWith('/api/'))return nativeFetch(input,options);
 try{
 if(url.pathname==='/api/media'&&method==='POST'){const blob=options.body;if(!(blob instanceof Blob)||blob.size>4*1024*1024||!['image/png','image/jpeg','image/webp'].includes(blob.type))return reply({error:'Chọn ảnh PNG, JPEG hoặc WebP dưới 4 MB.'},400);const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(reader.error);reader.readAsDataURL(blob);});return reply({url:data},201);}
 if(url.pathname==='/api/audio'&&method==='POST'){
  const blob=options.body;if(!(blob instanceof Blob)||!blob.size||blob.size>20*1024*1024)return reply({error:'Âm thanh cần nhỏ hơn hoặc bằng 20 MB.'},400);
  const bytes=new Uint8Array(await blob.slice(0,16).arrayBuffer()),ascii=(a,b)=>new TextDecoder().decode(bytes.slice(a,b));
  let mime='';if(ascii(0,4)==='RIFF'&&ascii(8,12)==='WAVE')mime='audio/wav';else if(ascii(0,3)==='ID3'&&[2,3,4].includes(bytes[3])||bytes[0]===255&&(bytes[1]&224)===224&&(bytes[1]&24)!==8&&(bytes[1]&6)!==0&&(bytes[2]&240)!==240&&(bytes[2]&240)!==0&&(bytes[2]&12)!==12)mime='audio/mpeg';else if(ascii(4,8)==='ftyp'&&['M4A ','M4B '].includes(ascii(8,12)))mime='audio/mp4';
  if(!mime)return reply({error:'Chọn file MP3, M4A hoặc WAV hợp lệ.'},415);
  const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(reader.error);reader.readAsDataURL(new Blob([blob],{type:mime}));});return reply({url:data,mime,size:blob.size},201);
 }
 if(url.pathname==='/api/stories'&&method==='GET'){const entries=await transact('readonly',s=>s.getAll());return reply({stories:entries.sort((a,b)=>b.updatedAt-a.updatedAt).map(({pages,...s})=>({...s,pageCount:pages.length,coverImage:pages[0]?.image||null}))});}
 if(url.pathname==='/api/stories'&&method==='POST'){const s=JSON.parse(options.body);if(!s.title?.trim()||!s.titleEn?.trim()||!s.pages?.length||s.pages.some(p=>!p.text?.trim()||!p.textEn?.trim()))return reply({error:'Truyện cần tên và nội dung Anh–Việt.'},400);const value={prompt:'Bé thích điều gì nhất trong câu chuyện?',promptEn:'What do you like most about this story?',...s,id:uid(),origin:'custom',revision:1,updatedAt:Date.now()};await transact('readwrite',store=>store.add(value));return reply(value,201);}
 const id=url.pathname.match(/^\/api\/stories\/([a-f0-9-]{36})$/)?.[1];if(id){const old=await transact('readonly',s=>s.get(id));if(!old)return reply({error:'Không tìm thấy truyện trên thiết bị này.'},404);if(method==='GET')return reply(old);if(method==='DELETE'){await transact('readwrite',s=>s.delete(id));return reply({deleted:true});}if(method==='PUT'){const value=JSON.parse(options.body);if(value.revision!==old.revision)return reply({error:'Truyện đã thay đổi. Hãy mở lại trước khi lưu.'},409);const saved={...value,id,origin:'custom',revision:old.revision+1,updatedAt:Date.now()};await transact('readwrite',s=>s.put(saved));return reply(saved);}}
 return reply({error:'Chức năng này không có trong bản lưu trên máy.'},404);
 }catch(e){return reply({error:'Chưa lưu được trên thiết bị. Nội dung vẫn được giữ trong bản nháp.'},503);}
};
