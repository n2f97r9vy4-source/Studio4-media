import json,subprocess,numpy as np
L=json.load(open('script_t.json'))
FPS=30;SR=44100
LEAD,GAP,TAIL={0:0.3},0.28,{0:0.7,7:4.5}
t=0;scenes=[];audio=[]
cur=None
for i,l in enumerate(L):
    if l['scene']!=cur:
        if cur is not None:
            t+=TAIL.get(cur,0.45);scenes[-1]['end']=round(t,3)
        cur=l['scene'];scenes.append({'scene':cur,'start':round(t,3)});t+=LEAD.get(cur,0.25)
    else: t+=GAP
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',f'v_{i:02d}.wav','-af','atempo=1.08','-f','s16le','-ac','1','-ar',str(SR),'-'])
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    hop=SR//FPS;env=[float(np.sqrt((a[k:k+hop]**2).mean())) for k in range(0,len(a),hop)]
    m=max(env) or 1;env=[round(min(1,e/m*1.3),2) for e in env]
    l['dur']=round(len(a)/SR,3);l.update(start=round(t,3),env=env);audio.append((t,a))
    t+=l['dur']
t+=TAIL.get(cur,0.45);scenes[-1]['end']=round(t,3)
tot=t;mix=np.zeros(int(tot*SR)+SR)
for st,a in audio: s=int(st*SR);mix[s:s+len(a)]+=a
import wave
w=wave.open('voce.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(mix[:int(tot*SR)],-1,1)*32767).astype(np.int16).tobytes());w.close()
json.dump({'total':round(tot,3),'scenes':scenes,'lines':L},open('timeline.json','w'),ensure_ascii=False)
print(tot);[print(s) for s in scenes]
