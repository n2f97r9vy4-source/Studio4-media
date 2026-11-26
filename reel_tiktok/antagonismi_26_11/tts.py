import json,subprocess,numpy as np,wave,sys
from kokoro_onnx import Kokoro
K=Kokoro(sys.argv[1]+'/kokoro.onnx',sys.argv[1]+'/voices.bin')
# voice, speed, pitch factor
V={"nar":("im_nicola",1.05,1.0),"P":("im_nicola",1.0,1.18),"K":("im_nicola",1.0,1.22),"N":("im_nicola",0.98,0.97),
   "S":("im_nicola",0.95,0.95),"Ca":("if_sara",1.05,1.12),"Mg":("if_sara",1.05,1.2),"Zn":("if_sara",1.05,1.25),
   "Fe":("im_nicola",1.05,1.35),"Mn":("im_nicola",0.95,1.15),"Mo":("if_sara",1.05,1.28)}
L=json.load(open('script.json'))
for i,l in enumerate(L):
    v,sp,pf=V[l['who']]
    if l['who']=='Mg' and l['scene']==5: v,sp,pf=("if_sara",1.0,1.05)
    if l['who']=='Ca' and l['scene']==4: v,sp,pf=("if_sara",0.98,1.02)
    a,sr=K.create(l['text'],voice=v,speed=sp,lang='it')
    w=wave.open(f'raw_{i:02d}.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(a,-1,1)*32767).astype(np.int16).tobytes());w.close()
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'raw_{i:02d}.wav','-af',f'asetrate={int(sr*pf)},aresample=44100,atempo={1/pf:.4f},silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-15:TP=-1.5','-ar','44100','-ac','1',f'v_{i:02d}.wav'],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'v_{i:02d}.wav']))
    l['dur']=round(d,3);print(i,l['who'],d)
json.dump(L,open('script_t.json','w'),ensure_ascii=False,indent=1)
