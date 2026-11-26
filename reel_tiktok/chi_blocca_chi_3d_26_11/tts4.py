# python3 tts4.py <cartella modelli kokoro> : voci naturali (nessun cambio di tono), una voce diversa per ruolo
import json,subprocess,numpy as np,wave,sys,hashlib,os
from kokoro_onnx import Kokoro
M=sys.argv[1]
K=Kokoro(M+'/kokoro-fp32.onnx',M+'/voices.bin')
ROLE={"bully":[("im_nicola",1.0)],"vA":[("if_sara",1.0)],"vB":[("im_nicola",0.5),("em_alex",0.5)],"nar":[("if_sara",1.0)]}
SPEED={"bully":1.03,"vA":1.05,"vB":1.06,"nar":1.03}
CTA="Prima di concimare, passa al banco di Studio 4."
SR=44100;FPS=30;RMS=0.13;os.makedirs('aud',exist_ok=True)
def style(spec):
    s=None
    for n,w in spec:
        x=K.get_voice_style(n)*w;s=x if s is None else s+x
    return s
def say(role,text):
    f='aud/'+hashlib.md5((role+json.dumps(ROLE[role])+str(SPEED[role])+text).encode()).hexdigest()[:10]+'.wav'
    if not os.path.exists(f):
        a,sr=K.create(text,voice=style(ROLE[role]),speed=SPEED[role],lang='it');a=np.asarray(a,dtype=np.float32)
        thr=np.abs(a).max()*10**(-42/20);idx=np.where(np.abs(a)>thr)[0];a=a[max(0,idx[0]-int(sr*0.02)):idx[-1]+int(sr*0.06)]
        n=int(sr*0.008);a[:n]*=np.linspace(0,1,n);a[-n:]*=np.linspace(1,0,n)
        fr=int(sr*0.03);e=np.array([np.sqrt((a[i:i+fr]**2).mean()) for i in range(0,len(a)-fr,fr)]);v=e[e>e.max()*0.1]
        g=RMS/np.sqrt((v**2).mean());g=min(g,0.9/np.abs(a).max());a=a*g
        w=wave.open('aud/tmp.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype(np.int16).tobytes());w.close()
        subprocess.run(['ffmpeg','-v','error','-y','-i','aud/tmp.wav','-af',f'aresample={SR}:resampler=soxr','-ac','1',f],check=True)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',f,'-f','s16le','-'])
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
for vid in json.load(open('videos.json')):
    if len(sys.argv)>2 and vid['id'] not in sys.argv[2:]: continue
    t=0.25;out=[];mix=[];L=vid['lines']+[["nar",CTA]]
    for i,(who,text) in enumerate(L):
        role='nar' if who=='nar' else 'bully' if i==0 else 'vA' if i==1 else 'vB'
        a=say(role,text)
        hop=SR//FPS;env=[float(np.sqrt((a[k:k+hop]**2).mean())) for k in range(0,len(a),hop)];m=max(env)
        out.append({'who':who,'text':text,'start':round(t,3),'dur':round(len(a)/SR,3),'env':[round(min(1,e/m*1.3),2) for e in env],'cta':who=='nar'})
        mix.append((t,a));t+=len(a)/SR+(0.3 if i==len(L)-2 else 0.15)
    tot=t-0.15+0.7;buf=np.zeros(int(tot*SR))
    for st,a in mix:s=int(st*SR);buf[s:s+len(a)]+=a
    w=wave.open(f"aud/{vid['id']}.wav",'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(buf,-1,1)*32767).astype(np.int16).tobytes());w.close()
    vid['total']=round(tot,3);vid['tl']=out;json.dump(vid,open(f"aud/{vid['id']}.json",'w'),ensure_ascii=False)
    print(vid['id'],round(tot,2),[(l['who'],l['start'],round(l['start']+l['dur'],2)) for l in out],flush=True)
