import * as THREE from 'three';
import {lerp,clamp,sstep,rng,fbm,canvasTex,gridIndex,makeGeo,superXZ,capsuleY,lum} from './util.js';

export const EL={
 P:{name:['FOSFORO'],c:'#7a3fb4',d:'#34135a',l:'#b48ae2',gran:['#e3d6f3','#bfa3e0','#f4eefb','#9a78c9']},
 K:{name:['POTASSIO'],c:'#f08a1c',d:'#7a3503',l:'#ffc266',gran:['#d9534a','#e98a7c','#c23b34','#f0b0a4']},
 N:{name:['AZOTO AMMONIACALE'],c:'#2f7fd8',d:'#0f3468',l:'#8cc4ff',gran:['#ffffff','#e6eef8','#cfe0f4','#f6f9fd']},
 Ca:{name:['CALCIO'],c:'#ebe2ce',d:'#6b5435',l:'#ffffff',gran:['#ffffff','#f1ede4','#ddd6c8','#faf7f0']},
 Mg:{name:['MAGNESIO'],c:'#2fa866',d:'#0d4a28',l:'#8ee3b0',gran:['#d8f3e2','#a9e0bf','#f1fbf5','#7fcf9f']},
 S:{name:['ZOLFO'],c:'#f2cb1e',d:'#6f5500',l:'#fff08a',gran:['#ffe45c','#f7d32f','#fff3a0','#e9c21a']},
 Zn:{c:'#8fa3b5',d:'#3b4f63',l:'#d7e3ee',rough:0.3,metal:0.35},
 Fe:{c:'#b5442a',d:'#55180b',l:'#e8836a',rough:0.62,metal:0.1,rust:true},
 Mn:{c:'#75658a',d:'#2c2238',l:'#a99bb8',rough:0.45,metal:0.2},
 Mo:{c:'#4fa7ba',d:'#1b4f5c',l:'#b5e6ef',rough:0.3,metal:0.35},
};
const X=new THREE.Vector3(1,0,0),Y=new THREE.Vector3(0,1,0),Z=new THREE.Vector3(0,0,1);
const std=o=>new THREE.MeshStandardMaterial(o);
export const M={
 sclera:new THREE.MeshPhysicalMaterial({color:'#fbfbf8',roughness:0.12,clearcoat:1,clearcoatRoughness:0.08}),
 iris:std({color:'#6a3d1c',roughness:0.35}),
 pupil:std({color:'#0c0806',roughness:0.2}),
 hl:new THREE.MeshBasicMaterial({color:new THREE.Color(1.6,1.6,1.6)}),
 mouth:std({color:'#3a0a0f',roughness:0.9}),
 tongue:std({color:'#e0676f',roughness:0.45}),
 teeth:std({color:'#fdfdf8',roughness:0.25}),
 brow:std({color:'#231510',roughness:0.7}),
 glove:std({color:'#f5f1e8',roughness:0.62}),
 shoe:std({color:'#33241d',roughness:0.45}),
 gold:std({color:'#f3b21e',roughness:0.28,metalness:1}),
};
let weave=null,fleck=null;
function shared(){
 if(weave)return;
 weave=canvasTex(128,128,(g,w)=>{g.fillStyle='#808080';g.fillRect(0,0,w,w);const n=8,s=w/n;
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){const hz=(i+j)%2===0;const gr=hz?g.createLinearGradient(0,j*s,0,(j+1)*s):g.createLinearGradient(i*s,0,(i+1)*s,0);
   gr.addColorStop(0,'#4a4a4a');gr.addColorStop(.5,'#e2e2e2');gr.addColorStop(1,'#4a4a4a');g.fillStyle=gr;g.fillRect(i*s,j*s,s,s)}},{srgb:false,repeat:[16,7]});
 fleck=canvasTex(256,256,(g,w)=>{const r=rng(77);g.fillStyle='#808080';g.fillRect(0,0,w,w);
  for(let i=0;i<2600;i++){const v=Math.floor(60+r()*140);g.fillStyle=`rgb(${v},${v},${v})`;const s=1+r()*3;g.beginPath();g.arc(r()*w,r()*w,s,0,7);g.fill()}},{srgb:false,repeat:[3,2]});
}
function mix(a,b,t){return '#'+new THREE.Color(a).lerp(new THREE.Color(b),t).getHexString()}

// ------------------------------------------------------------------ occhi, sopracciglia, bocca
function makeEye(r,lidMat){
 const g=new THREE.Group();
 g.add(new THREE.Mesh(new THREE.SphereGeometry(r,36,24),M.sclera));
 const gaze=new THREE.Group();g.add(gaze);
 const iris=new THREE.Mesh(new THREE.SphereGeometry(r*1.008,32,10,0,Math.PI*2,0,0.52),M.iris);iris.rotation.x=Math.PI/2;gaze.add(iris);
 const pupil=new THREE.Mesh(new THREE.SphereGeometry(r*1.016,28,8,0,Math.PI*2,0,0.30),M.pupil);pupil.rotation.x=Math.PI/2;gaze.add(pupil);
 const hl=new THREE.Mesh(new THREE.SphereGeometry(r*0.105,12,8),M.hl);hl.position.set(-r*0.22,r*0.26,r*0.95);gaze.add(hl);
 const hl2=new THREE.Mesh(new THREE.SphereGeometry(r*0.05,10,6),M.hl);hl2.position.set(r*0.18,-r*0.14,r*0.985);gaze.add(hl2);
 const lidU=new THREE.Group();const lu=new THREE.Mesh(new THREE.SphereGeometry(r*1.06,36,14,0,Math.PI*2,0,Math.PI/2),lidMat);lidU.add(lu);g.add(lidU);
 const lidL=new THREE.Group();const ll=new THREE.Mesh(new THREE.SphereGeometry(r*1.06,36,14,0,Math.PI*2,0,Math.PI/2),lidMat);ll.rotation.x=Math.PI;lidL.add(ll);g.add(lidL);
 g.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true}});
 g.userData={gaze,lidU,lidL};return g;
}
function segShape(y0,y1,R=0.93){ // parte del cerchio unitario tra y0 e y1
 const s=new THREE.Shape();const a0=Math.asin(clamp(y0/R,-1,1)),a1=Math.asin(clamp(y1/R,-1,1));const n=24;
 for(let i=0;i<=n;i++){const a=lerp(a0,a1,i/n);const x=R*Math.cos(a),y=R*Math.sin(a);if(i===0)s.moveTo(x,y);else s.lineTo(x,y)}
 for(let i=n;i>=0;i--){const a=lerp(a0,a1,i/n);s.lineTo(-R*Math.cos(a),R*Math.sin(a))}
 s.closePath();return s;
}
function makeMouth(w,h,lipMat,kind){
 const g=new THREE.Group(),mg=new THREE.Group();g.add(mg);
 const cav=new THREE.Mesh(new THREE.SphereGeometry(1,32,20),M.mouth);cav.scale.set(1,1,0.06);cav.position.z=-0.02;mg.add(cav);
 const lip=new THREE.Mesh(new THREE.TorusGeometry(1,0.12,10,56),lipMat);lip.scale.set(1,1,0.22);mg.add(lip);
 const ex=(sh,d)=>new THREE.ExtrudeGeometry(sh,{depth:d,bevelEnabled:false,curveSegments:8});
 const tU=new THREE.Mesh(ex(segShape(0.34,0.93),0.02),M.teeth);tU.position.z=0.022;mg.add(tU);
 const tU2=new THREE.Mesh(ex(segShape(0.07,0.93),0.02),M.teeth);tU2.position.z=0.024;mg.add(tU2);
 const tL2=new THREE.Mesh(ex(segShape(-0.93,-0.07),0.02),M.teeth);tL2.position.z=0.024;mg.add(tL2);
 const tg=new THREE.Mesh(new THREE.SphereGeometry(1,20,14),M.tongue);tg.scale.set(0.62,0.42,0.045);tg.position.set(0,-0.5,0.02);mg.add(tg);
 let frown=null;
 if(kind==='victim'){frown=new THREE.Mesh(new THREE.TorusGeometry(w*0.95,w*0.17,8,24,Math.PI*0.8),M.brow);frown.rotation.z=Math.PI*0.1;frown.position.set(0,-w*0.55,0.012);g.add(frown);tU2.visible=tL2.visible=false}
 g.traverse(o=>{if(o.isMesh){o.castShadow=false}});
 g.userData={set(o,grit){ // o apertura 0..1, grit 0..1 (denti stretti)
   if(kind==='victim'){const sp=o>0.06;mg.visible=sp;frown.visible=!sp;if(sp){mg.scale.set(w*(0.6+0.22*o),h*(0.5+1.0*o),1);tU.visible=false;tg.visible=o>0.4}}
   else{const hh=h*(0.34+0.72*o);mg.scale.set(w*(1-0.1*o),hh,1);const gr=grit>0.5;tU2.visible=tL2.visible=gr;tU.visible=!gr;tg.visible=!gr&&o>0.2}
 }};
 return g;
}
class Face{
 constructor(parent,c){ // c: eyeR, eyes:[v3,v3], brows:[v3,v3], browLen, browR, browTilt, mouth:v3, mouthTilt, mw, mh, lidMat, lipMat, kind
  this.c=c;this.eyes=[];this.brows=[];
  for(let s=0;s<2;s++){const e=makeEye(c.eyeR,c.lidMat);e.position.copy(c.eyes[s]);parent.add(e);this.eyes.push(e);
   const bg=new THREE.CapsuleGeometry(c.browR,c.browLen,6,12);bg.rotateZ(Math.PI/2);
   const b=new THREE.Mesh(bg,M.brow);b.position.copy(c.brows[s]);b.userData.base=c.brows[s].clone();b.castShadow=false;parent.add(b);this.brows.push(b)}
  this.mouth=makeMouth(c.mw,c.mh,c.lipMat,c.kind);this.mouth.position.copy(c.mouth);this.mouth.rotation.x=c.mouthTilt||0;parent.add(this.mouth);
 }
 // open: apertura palpebra (rad), slant: >0 arrabbiato, <0 triste; brow: angolo (>0 arrabbiato), browY: spostamento; gx,gy sguardo; mo bocca; grit; blink 0..1
 set({open=1,low=1.25,slant=0,brow=0,browY=0,gx=0,gy=0,mo=0,grit=0,blink=0}){
  for(let s=0;s<2;s++){const sg=s===0?-1:1,u=this.eyes[s].userData;
   u.lidU.rotation.set(-lerp(open,-0.22,blink),0,sg*slant);
   u.lidL.rotation.set(lerp(low,1.05,blink),0,-sg*slant*0.3);
   u.gaze.rotation.set(-gy,gx,0);
   const b=this.brows[s];b.rotation.z=sg*brow;b.position.y=b.userData.base.y+browY-(blink*0.01);b.rotation.y=sg*(this.c.browTilt||0);
  }
  this.mouth.userData.set(mo,grit);
 }
}
// ------------------------------------------------------------------ braccia
function makeArm(parent,{r1,r2,l1,l2,mat,hand,bicep}){
 const up=new THREE.Mesh(capsuleY(r1,l1),mat),fo=new THREE.Mesh(capsuleY(r2,l2),mat),hd=new THREE.Group();
 if(bicep){const b=new THREE.Mesh(new THREE.SphereGeometry(1,20,14),mat);b.scale.set(r1*1.32,l1*0.42,r1*1.32);b.position.y=l1*0.52;up.add(b)}
 hd.add(hand);parent.add(up,fo,hd);
 [up,fo].forEach(m=>{m.castShadow=true;m.receiveShadow=true});hd.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});
 const a={handPos:new THREE.Vector3(),set(S,d1,d2,tw=0){d1.normalize();d2.normalize();up.position.copy(S);up.quaternion.setFromUnitVectors(Y,d1);
  const E=S.clone().addScaledVector(d1,l1);fo.position.copy(E);fo.quaternion.setFromUnitVectors(Y,d2);
  a.handPos.copy(E).addScaledVector(d2,l2);hd.position.copy(a.handPos);hd.quaternion.setFromUnitVectors(Y,d2);if(tw)hd.rotateY(tw)}};
 return a;
}
function fist(sg){const g=new THREE.Group();const m=M.glove;
 const p=new THREE.Mesh(new THREE.SphereGeometry(0.165,24,18),m);p.scale.set(1,0.9,1.02);p.position.y=0.11;g.add(p);
 for(let i=0;i<4;i++){const k=new THREE.Mesh(new THREE.SphereGeometry(0.062,14,10),m);k.position.set((i-1.5)*0.078,0.2,0.105-Math.abs(i-1.5)*0.012);g.add(k)}
 const th=new THREE.Mesh(new THREE.SphereGeometry(0.07,14,10),m);th.scale.set(1,1.25,1);th.position.set(-sg*0.13,0.1,0.11);g.add(th);
 const cuff=new THREE.Mesh(new THREE.TorusGeometry(0.115,0.04,10,24),m);cuff.rotation.x=Math.PI/2;cuff.position.y=-0.03;g.add(cuff);
 return g}

// ------------------------------------------------------------------ SACCO (il prepotente)
function prof(v){const P=[[0,0.90],[0.18,1.0],[0.55,0.965],[0.85,0.93],[1,0.895]];
 for(let i=0;i<P.length-1;i++)if(v<=P[i+1][0]){const t=(v-P[i][0])/(P[i+1][0]-P[i][0]);return lerp(P[i][1],P[i+1][1],t*t*(3-2*t))}return P[P.length-1][1]}
function dims(S,v){const p=prof(v);return{a:S.W*p,b:S.D*p*(1+0.10*Math.exp(-(((v-0.3)/0.28)**2))),n:lerp(3.8,3.0,v)}}
function surfZ(S,x,v){const{a,b,n}=dims(S,v);const q=Math.min(0.999,Math.abs(x/a));return b*Math.pow(1-Math.pow(q,n),1/n)}
function wrinkle(u,v,seed){const front=Math.exp(-(((u-0.5)/0.17)**2))*sstep(0.36,0.5,v);
 let d=0.034*(fbm(u*9+seed,v*5,seed*1.3,3)-0.5)*(1-0.88*front);
 d+=0.013*Math.sin(u*Math.PI*2*9+seed)*sstep(0.30,0.0,v);d+=0.012*Math.sin(u*Math.PI*2*11+2*seed)*sstep(0.84,1.0,v);return d}
function ring(a,b,n,NU){const Mn=1024,px=new Float64Array(Mn+1),pz=new Float64Array(Mn+1),cs=new Float64Array(Mn+1);
 for(let i=0;i<=Mn;i++){const ps=-Math.PI+2*Math.PI*i/Mn,sx=Math.sin(ps),cz=Math.cos(ps),r=Math.pow(Math.pow(Math.abs(sx/a),n)+Math.pow(Math.abs(cz/b),n),-1/n);px[i]=r*sx;pz[i]=r*cz;if(i)cs[i]=cs[i-1]+Math.hypot(px[i]-px[i-1],pz[i]-pz[i-1])}
 const out=[];let j=0;for(let k=0;k<=NU;k++){const s=k/NU*cs[Mn];while(j<Mn-1&&cs[j+1]<s)j++;const t=(s-cs[j])/Math.max(1e-9,cs[j+1]-cs[j]);out.push([lerp(px[j],px[j+1],t),lerp(pz[j],pz[j+1],t)])}
 return{pts:out,len:cs[Mn]}}
function sackGeo(S,seed){const NU=168,NV=84,rows=[];
 for(const[s,yo]of[[0,-0.125],[0.3,-0.12],[0.58,-0.105],[0.8,-0.08],[0.93,-0.05],[0.985,-0.022]])rows.push({v:0,s,y:yo,body:false});
 for(let j=0;j<=NV;j++)rows.push({v:j/NV,s:1,y:j/NV*S.H,body:true});
 for(const[s,yo]of[[0.94,0.0],[0.6,0.015],[0.25,0.02],[0,0.02]])rows.push({v:1,s,y:S.H+yo,body:false});
 const pos=[],uv=[];
 for(const r of rows){const{a,b,n}=dims(S,r.v);
  const rg=ring(Math.max(1e-4,a*r.s),Math.max(1e-4,b*r.s),n,NU).pts;
  for(let i=0;i<=NU;i++){const u=i/NU;let[x,z]=rg[i];
   if(r.body){const d=wrinkle(u,r.v,seed),rad=Math.hypot(x,z)||1;x*=1+d/rad;z*=1+d/rad}
   pos.push(x,S.y0+r.y,z);uv.push(u,r.body?clamp(r.v,0.002,0.998):(r.v<0.5?0.002:0.998))}}
 return makeGeo(pos,uv,gridIndex(rows.length,NU+1))}
function rimGeo(S,rt){const NU=140,NP=14,pos=[],uv=[];const{a,b,n}=dims(S,1);const rg=ring(a*1.01,b*1.01,n,NU).pts;
 for(let i=0;i<=NU;i++){const th=i/NU*2*Math.PI;const[x,z]=rg[i];const L=Math.hypot(x,z),ox=x/L,oz=z/L;const rr=rt*(1+0.18*Math.sin(th*7)+0.1*Math.sin(th*13+1));
  for(let j=0;j<=NP;j++){const ph=j/NP*2*Math.PI;pos.push(x+ox*rr*Math.cos(ph),S.y0+S.H+rr*0.85*Math.sin(ph)-0.01,z+oz*rr*Math.cos(ph));uv.push(i/NU*10,j/NP)}}
 return makeGeo(pos,uv,gridIndex(NU+1,NP+1))}
function sackTexture(k){const e=EL[k];const light=lum(e.c)>0.45;
 return canvasTex(4096,2048,(g,w,h)=>{const r=rng(k.charCodeAt(0)*31+7);
  const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,mix(e.c,e.l,0.18));gr.addColorStop(0.55,e.c);gr.addColorStop(1,mix(e.c,e.d,0.22));g.fillStyle=gr;g.fillRect(0,0,w,h);
  for(let i=0;i<900;i++){g.globalAlpha=0.04+r()*0.05;g.fillStyle=r()>.5?e.l:e.d;const s=20+r()*90;g.beginPath();g.ellipse(r()*w,r()*h,s*2,s,r()*3,0,7);g.fill()}
  g.globalAlpha=0.10;g.fillStyle='#000';for(let y=0;y<h;y+=9)g.fillRect(0,y,w,2);g.fillStyle='#fff';for(let x=0;x<w;x+=9)g.fillRect(x,0,2,h);
  g.globalAlpha=1;
  // cucitura laterale e fasce
  g.fillStyle=mix(e.c,e.d,0.55);g.fillRect(0,h*0.955,w,h*0.012);g.fillRect(0,h*0.03,w,h*0.012);
  g.strokeStyle=mix(e.c,'#ffffff',0.6);g.lineWidth=5;g.setLineDash([22,16]);g.beginPath();g.moveTo(0,h*0.94);g.lineTo(w,h*0.94);g.moveTo(0,h*0.055);g.lineTo(w,h*0.055);g.stroke();g.setLineDash([]);
  // lettera e nome
  const S0={W:0.74,D:0.45,H:1.70,y0:0.24},dd=dims(S0,0.25),sx=2*S0.H/ring(dd.a,dd.b,dd.n,64).len,cx=w/2;
  g.save();g.translate(cx,h*(1-0.268));g.scale(sx,1);g.textAlign='center';g.textBaseline='alphabetic';g.lineJoin='round';
  const desc=/[gjpqy]/.test(k),fs=k.length>1?(desc?620:660):760,by=desc?98:fs*0.36,ny=(k.length>1?660:760)*0.36+128;g.font=`700 ${fs}px P`;
  g.lineWidth=70;g.strokeStyle=light?'#ffffff':e.d;g.strokeText(k,0,by);g.fillStyle=light?e.d:'#ffffff';g.fillText(k,0,by);
  const ns=e.name[0].length>10?84:118;g.font=`700 ${ns}px P`;g.fillStyle=light?e.d:'#ffffff';
  g.letterSpacing='12px';
  e.name.forEach((t,i)=>g.fillText(t,6,ny+i*(ns*1.08)));g.letterSpacing='0px';
  g.restore();
 });
}
export function buildSack(k,seed=3){shared();const e=EL[k],S={W:0.74,D:0.45,H:1.70,y0:0.24};
 const root=new THREE.Group(),body=new THREE.Group();root.add(body);
 const mat=std({map:sackTexture(k),bumpMap:weave,bumpScale:2.2,roughness:0.74});
 const mesh=new THREE.Mesh(sackGeo(S,seed),mat);mesh.castShadow=mesh.receiveShadow=true;body.add(mesh);
 const rimMat=std({color:mix(e.c,'#ffffff',0.72),bumpMap:weave,bumpScale:2.2,roughness:0.8});
 const rim=new THREE.Mesh(rimGeo(S,0.07),rimMat);rim.castShadow=rim.receiveShadow=true;body.add(rim);
 for(const sg of[-1,1]){const ear=new THREE.Mesh(new THREE.ConeGeometry(0.085,0.2,12),std({color:mix(e.c,e.d,0.12),bumpMap:weave,bumpScale:2.2,roughness:0.78}));ear.position.set(sg*(S.W*0.9+0.03),S.y0+0.005,0);ear.rotation.z=sg*(Math.PI/2+0.55);ear.scale.z=0.6;ear.castShadow=ear.receiveShadow=true;body.add(ear)}
 // granuli
 const top=S.y0+S.H,{a,b}=dims(S,1),r=rng(seed*91+5);
 const heap=new THREE.Mesh(new THREE.SphereGeometry(1,28,16),std({color:e.gran[1],roughness:0.8}));heap.scale.set(a*0.93,0.15,b*0.9);heap.position.y=top+0.0;heap.castShadow=true;body.add(heap);
 const NG=120,gm=new THREE.InstancedMesh(new THREE.SphereGeometry(0.058,12,9),std({roughness:0.5}),NG);const mx=new THREE.Matrix4(),col=new THREE.Color();
 for(let i=0;i<NG;i++){const rr=Math.sqrt(r())*0.9,th=r()*6.283;const x=a*rr*Math.cos(th)*0.92,z=b*rr*Math.sin(th)*0.9,y=top+0.03+(1-rr*rr)*0.15+r()*0.035;const s=0.75+r()*0.55;
  mx.compose(new THREE.Vector3(x,y,z),new THREE.Quaternion(),new THREE.Vector3(s,s*(0.85+r()*0.2),s));gm.setMatrixAt(i,mx);gm.setColorAt(i,col.set(e.gran[Math.floor(r()*e.gran.length)]))}
 gm.castShadow=gm.receiveShadow=true;body.add(gm);
 // faccia
 const vE=0.745,vM=0.535,yE=S.y0+vE*S.H,yM=S.y0+vM*S.H,eR=0.188,ex=0.232;
 const lipMat=std({color:mix(e.c,e.d,0.6),roughness:0.6});
 const face=new Face(body,{eyeR:eR,kind:'bully',lidMat:std({color:mix(e.c,e.d,0.12),roughness:0.7}),lipMat,
  eyes:[new THREE.Vector3(-ex,yE,surfZ(S,ex,vE)-0.105),new THREE.Vector3(ex,yE,surfZ(S,ex,vE)-0.105)],
  brows:[new THREE.Vector3(-ex-0.01,yE+0.215,surfZ(S,ex,vE)+0.06),new THREE.Vector3(ex+0.01,yE+0.215,surfZ(S,ex,vE)+0.06)],browLen:0.25,browR:0.048,browTilt:0,
  mouth:new THREE.Vector3(0,yM,surfZ(S,0,vM)+0.004),mw:0.29,mh:0.135});
 // braccia e gambe
 const arms=[-1,1].map(sg=>makeArm(body,{r1:0.115,r2:0.10,l1:0.36,l2:0.33,mat:M.glove,hand:fist(sg),bicep:true}));
 const legs=[-1,1].map(sg=>{const g=new THREE.Group();const l=new THREE.Mesh(new THREE.CylinderGeometry(0.085,0.08,0.2,16),M.glove);l.position.y=0.17;g.add(l);
  const sh=new THREE.Mesh(new THREE.SphereGeometry(1,20,14),M.shoe);sh.scale.set(0.17,0.105,0.26);sh.position.set(0,0.075,0.09);g.add(sh);g.position.x=sg*0.33;
  g.traverse(o=>{if(o.isMesh)o.castShadow=o.receiveShadow=true});root.add(g);return g});
 return{k,root,body,S,face,arms,legs,shoulder:sg=>new THREE.Vector3(sg*0.70,S.y0+0.60*S.H,0.0)};
}

// ------------------------------------------------------------------ PALLINA (il nutriente bloccato)
function ballTexture(k){const e=EL[k];const light=lum(e.c)>0.45;
 return canvasTex(4096,2048,(g,w,h)=>{const r=rng(k.charCodeAt(0)*17+k.length*5);
  const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,mix(e.c,e.l,0.35));gr.addColorStop(0.5,e.c);gr.addColorStop(1,mix(e.c,e.d,0.35));g.fillStyle=gr;g.fillRect(0,0,w,h);
  for(let i=0;i<700;i++){g.globalAlpha=0.05+r()*0.07;g.fillStyle=r()>.5?e.l:e.d;const s=14+r()*70;g.beginPath();g.ellipse(r()*w,r()*h,s*1.6,s,r()*3,0,7);g.fill()}
  if(e.rust)for(let i=0;i<2600;i++){g.globalAlpha=0.25+r()*0.35;g.fillStyle=['#7a2a14','#d0703a','#8f3a1c','#e39a5e'][Math.floor(r()*4)];const s=2+r()*9;g.beginPath();g.arc(r()*w,r()*h,s,0,7);g.fill()}
  g.globalAlpha=1;
  const el=-0.56,cx=w*0.25,cy=h*(0.5-el/Math.PI);g.save();g.translate(cx,cy);g.scale(1/Math.cos(el),1);g.textAlign='center';g.textBaseline='alphabetic';g.lineJoin='round';
  const fs=k.length>1?330:380;g.font=`700 ${fs}px P`;g.lineWidth=44;g.strokeStyle=light?'#ffffff':e.d;g.strokeText(k,0,fs*0.36);g.fillStyle=light?e.d:'#ffffff';g.fillText(k,0,fs*0.36);g.restore();
 });
}
export function buildBall(k,side){shared();const e=EL[k],R=0.37; // side: -1 a sinistra, +1 a destra del sacco
 const root=new THREE.Group(),body=new THREE.Group();body.position.y=R;root.add(body);
 const mat=new THREE.MeshPhysicalMaterial({map:ballTexture(k),roughness:e.rough??0.42,metalness:e.metal??0,clearcoat:0.55,clearcoatRoughness:0.25,bumpMap:fleck,bumpScale:e.rust?1.6:0.5});
 const sg=new THREE.SphereGeometry(R,72,48);
 const sp=new THREE.Mesh(sg,mat);sp.castShadow=sp.receiveShadow=true;body.add(sp);
 const dir=(az,el,d)=>new THREE.Vector3(Math.sin(az)*Math.cos(el)*d,Math.sin(el)*d,Math.cos(az)*Math.cos(el)*d);
 const eR=0.108,az=0.37,elE=0.26;
 const face=new Face(body,{eyeR:eR,kind:'victim',lidMat:std({color:mix(e.c,e.d,0.1),roughness:0.5}),lipMat:std({color:mix(e.c,e.d,0.6),roughness:0.6}),
  eyes:[dir(-az,elE,R-0.05),dir(az,elE,R-0.05)],brows:[dir(-az*1.02,0.66,R+0.012),dir(az*1.02,0.66,R+0.012)],browLen:0.115,browR:0.024,browTilt:0.3,
  mouth:dir(0,-0.14,R-0.004),mouthTilt:0.14,mw:0.07,mh:0.06});
 face.brows.forEach(b=>b.rotation.x=-0.55);
 const armMat=std({color:mix(e.c,e.d,0.72),roughness:0.55});
 const mit=()=>{const g=new THREE.Group();const m=new THREE.Mesh(new THREE.SphereGeometry(0.062,16,12),armMat);m.position.y=0.04;g.add(m);const t=new THREE.Mesh(new THREE.SphereGeometry(0.03,10,8),armMat);t.position.set(0.045,0.05,0.03);g.add(t);return g};
 const arms=[-1,1].map(()=>makeArm(body,{r1:0.036,r2:0.033,l1:0.17,l2:0.16,mat:armMat,hand:mit()}));
 // anello per la catena, verso il sacco
 const ringDir=dir(-side*0.75,0.95,1).normalize();
 const ring=new THREE.Group();const base=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.045,0.03,14),M.gold);ring.add(base);
 const tor=new THREE.Mesh(new THREE.TorusGeometry(0.05,0.016,10,22),M.gold);tor.position.y=0.055;tor.rotation.y=side*0.6;ring.add(tor);
 ring.position.copy(ringDir).multiplyScalar(R-0.004);ring.quaternion.setFromUnitVectors(Y,ringDir);ring.traverse(o=>{if(o.isMesh)o.castShadow=true});body.add(ring);
 const anchor=new THREE.Object3D();anchor.position.copy(ringDir).multiplyScalar(R+0.085);body.add(anchor);
 return{k,root,body,R,face,arms,anchor,side,shoulder:s=>dir(s*1.32,-0.08,R-0.01)};
}
// sfera: SphereGeometry ha u=0.25 verso +z? (x=-cos(phi)sin(theta), z=sin(phi)sin(theta), phi=u*2pi) -> u=0.25: x=0,z=+1. Quindi nessuna rotazione serve.
