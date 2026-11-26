import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { VignetteShader } from 'three/addons/shaders/VignetteShader.js';
import * as BGU from 'three/addons/utils/BufferGeometryUtils.js';
import {lerp,clamp,sstep,ease,rng,fbm,vnoise,canvasTex,taperTube} from './util.js';
import {EL,M,buildSack,buildBall} from './chars.js';

const TOP=3.3;
const V3=(x,y,z)=>new THREE.Vector3(x,y,z);
export function wallZ(x,y){return -1.9+0.085*x*x-0.8*Math.exp(-((x/1.45)**2+((y-1.25)/1.3)**2))+0.42*(fbm(x*0.8+5,y*0.8,1.7,4)-0.47)+0.07*(fbm(x*4,y*4,9.1,3)-0.5)}
const SOIL=['#3f2613','#5c3a1d','#6f4726','#8a6038','#7a4a28'].map(c=>new THREE.Color(c));
function soilColor(x,y,z,out){const n1=fbm(x*0.7+2,y*0.7,z*0.7+3,4),n2=fbm(x*3.1,y*3.1+4,z*3.1+8,3),n3=fbm(x*9,y*9,z*9,2);
 out.copy(SOIL[1]).lerp(SOIL[2],sstep(0.3,0.7,n1));out.lerp(SOIL[3],sstep(0.52,0.78,n2)*0.75);out.lerp(SOIL[4],sstep(0.55,0.8,n1*n2*2)*0.5);out.lerp(SOIL[0],sstep(0.6,0.35,n2)*0.45+sstep(2.55,3.25,y)*0.55);
 out.multiplyScalar(0.86+0.28*n3);return out}

export function createStage(canvas,VID,{W=980,H=1040,aa='smaa',ao=true,gout=0,aos=0.5,sh=true,soft=false,lam=true}={}){
 const R=rng(VID.id.charCodeAt(0)*13+VID.id.length);
 const renderer=new THREE.WebGLRenderer({canvas,antialias:false,preserveDrawingBuffer:true,powerPreference:'high-performance'});
 renderer.setPixelRatio(1);renderer.setSize(W,H,false);
 renderer.shadowMap.enabled=sh;renderer.shadowMap.type=soft?THREE.PCFSoftShadowMap:THREE.PCFShadowMap;
 renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;
 const scene=new THREE.Scene();
 scene.background=new THREE.Color('#d9eef6');
 { const sky=new THREE.Mesh(new THREE.PlaneGeometry(60,24),new THREE.MeshBasicMaterial({map:canvasTex(8,256,(g,w,h)=>{const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#8fcdf3');gr.addColorStop(0.55,'#cfeaf7');gr.addColorStop(1,'#f3f6e6');g.fillStyle=gr;g.fillRect(0,0,w,h)}),fog:false}));sky.position.set(0,9.5,-16);scene.add(sky)}
 const pm=new THREE.PMREMGenerator(renderer);scene.environment=pm.fromScene(new RoomEnvironment(),0.04).texture;scene.environmentIntensity=0.42;
 const cam=new THREE.PerspectiveCamera(30,W/H,0.3,60);

 // ---------------------------------------------------------------- terreno
 const soilMap=canvasTex(512,512,(g,w)=>{const r=rng(5);g.fillStyle='#d9d2ca';g.fillRect(0,0,w,w);
  for(let i=0;i<9000;i++){const v=r();g.globalAlpha=0.25+r()*0.4;g.fillStyle=v<0.5?'#8f8478':v<0.9?'#f4efe8':'#6a5f55';const s=0.6+r()*r()*5;g.beginPath();g.arc(r()*w,r()*w,s,0,7);g.fill()}},{repeat:[9,4]});
 const grain=canvasTex(256,256,(g,w)=>{const r=rng(9);g.fillStyle='#808080';g.fillRect(0,0,w,w);
  for(let i=0;i<5200;i++){const v=Math.floor(40+r()*180);g.fillStyle=`rgb(${v},${v},${v})`;const s=0.8+r()*r()*5;g.beginPath();g.arc(r()*w,r()*w,s,0,7);g.fill()}},{srgb:false,repeat:[10,4]});
 const soilMat=lam?new THREE.MeshLambertMaterial({vertexColors:true,map:soilMap,bumpMap:grain,bumpScale:3.5}):new THREE.MeshStandardMaterial({vertexColors:true,map:soilMap,bumpMap:grain,bumpScale:3.5,roughness:0.96});
 const col=new THREE.Color();
 { // parete
  const g=new THREE.PlaneGeometry(11,4.1,230,96);g.translate(0,TOP-2.05,0);const p=g.attributes.position,c=[];
  for(let i=0;i<p.count;i++){const x=p.getX(i);let y=p.getY(i);y+=0.09*(fbm(x*2.2,3,5,3)-0.5)*sstep(3.0,3.3,y)*2;const z=wallZ(x,y);p.setXYZ(i,x,y,z);soilColor(x,y,z,col);c.push(col.r,col.g,col.b)}
  g.setAttribute('color',new THREE.Float32BufferAttribute(c,3));g.computeVertexNormals();const m=new THREE.Mesh(g,soilMat);m.receiveShadow=true;m.castShadow=false;scene.add(m);
 }
 const floorY=(x,z)=>0.035*(fbm(x*1.3+3,z*1.3,4.2,3)-0.5);
 { // pavimento
  const g=new THREE.PlaneGeometry(11,8.4,170,130);g.rotateX(-Math.PI/2);g.translate(0,0,1.0);const p=g.attributes.position,c=[];
  for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i),y=floorY(x,z);p.setY(i,y);soilColor(x,0.3,z,col);col.multiplyScalar(1.12);c.push(col.r,col.g,col.b)}
  g.setAttribute('color',new THREE.Float32BufferAttribute(c,3));g.computeVertexNormals();const m=new THREE.Mesh(g,soilMat);m.receiveShadow=true;scene.add(m);
 }
 // sassi e zolle
 const rock=(seed)=>{let g=new THREE.IcosahedronGeometry(1,2);g.deleteAttribute('normal');g.deleteAttribute('uv');g=BGU.mergeVertices(g);const p=g.attributes.position,v=new THREE.Vector3();
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);v.multiplyScalar(0.6+0.75*fbm(v.x*1.1+seed,v.y*1.1,v.z*1.1,3));p.setXYZ(i,v.x,v.y,v.z)}g.computeVertexNormals();return g};
 const mx=new THREE.Matrix4(),q=new THREE.Quaternion(),eu=new THREE.Euler();
 const inst=(geo,mat,list)=>{const m=new THREE.InstancedMesh(geo,mat,list.length);list.forEach((o,i)=>{eu.set(o.r[0],o.r[1],o.r[2]);q.setFromEuler(eu);mx.compose(o.p,q,o.s);m.setMatrixAt(i,mx);m.setColorAt(i,o.c)});m.castShadow=m.receiveShadow=true;scene.add(m);return m};
 const PEB=['#8a7560','#6e5a48','#a08a70','#5a4a3c','#9a6a44','#7d7166','#b09a7c'].map(c=>new THREE.Color(c));
 const keepOut=(x,z)=>(Math.abs(x)<1.0&&z>-0.9&&z<0.6)||(Math.abs(Math.abs(x)-1.07)<0.55&&z>0.3&&z<1.35);
 { const L=[];
  for(let i=0;i<230;i++){const x=(R()-0.5)*8.6,y=-0.2+R()*3.25,s=0.035+R()*R()*0.17;L.push({p:V3(x,y,wallZ(x,y)+s*(-0.25+R()*0.6)),r:[R()*6,R()*6,R()*6],s:V3(s*(0.8+R()*0.5),s*(0.6+R()*0.4),s*(0.7+R()*0.4)),c:PEB[Math.floor(R()*PEB.length)]})}
  for(let i=0;i<170;i++){const x=(R()-0.5)*7.4,z=-1.7+R()*5.2;if(keepOut(x,z))continue;const s=0.018+R()*R()*0.085;L.push({p:V3(x,floorY(x,z)+s*0.25,z),r:[R()*6,R()*6,R()*6],s:V3(s*(0.9+R()*0.5),s*(0.55+R()*0.35),s*(0.8+R()*0.4)),c:PEB[Math.floor(R()*PEB.length)]})}
  inst(rock(1),new THREE.MeshStandardMaterial({roughness:0.85}),L);
  const C=[];
  for(let i=0;i<70;i++){const x=(R()-0.5)*8.8,y=-0.3+R()*3.4,s=0.1+R()*0.2,z=wallZ(x,y)-s*(0.35+R()*0.3);soilColor(x,y,z,col);C.push({p:V3(x,y,z),r:[R()*6,R()*6,R()*6],s:V3(s*(1.1+R()*0.6),s*(0.6+R()*0.4),s*0.75),c:col.clone().multiplyScalar(1.0)})}
  for(let i=0;i<60;i++){const x=(R()-0.5)*7.6,z=-1.8+R()*5;if(keepOut(x,z))continue;const s=0.05+R()*0.12;soilColor(x,0.2,z,col);C.push({p:V3(x,floorY(x,z)-s*0.25,z),r:[R()*6,R()*6,R()*6],s:V3(s*1.2,s*0.6,s),c:col.clone().multiplyScalar(1.12)})}
  inst(rock(7),lam?new THREE.MeshLambertMaterial():new THREE.MeshStandardMaterial({roughness:1}),C);
 }
 // radici
 { const geos=[],base=V3(0,TOP+0.06,-1.72);const fix=(p,zmin)=>{const wz=wallZ(p.x,p.y);if(p.z<wz+0.045)p.z=wz+0.045+R()*0.04;if(Math.abs(p.x)<1.0&&p.y<2.45&&p.z>zmin)p.z=zmin-R()*0.15};
  const NPR=9;
  for(let k=0;k<NPR;k++){const spread=lerp(-1.3,1.3,k/(NPR-1))+(R()-0.5)*0.14;let p=base.clone().add(V3((R()-0.5)*0.1,0,(R()-0.5)*0.08));const pts=[p.clone()];let ang=spread;
   const zt=Math.abs(spread)>0.75?lerp(-0.8,0.25,R()):lerp(-1.55,-1.0,R());const steps=7+Math.floor(R()*4);
   for(let s=0;s<steps;s++){const len=0.36+R()*0.14;ang=ang*0.94+(R()-0.5)*0.5;p=p.clone();p.x+=Math.sin(ang)*len;p.y-=Math.cos(ang)*len*0.85;p.z=lerp(p.z,zt,0.35)+(R()-0.5)*0.12;fix(p,-0.9);if(p.y<0.12)break;pts.push(p)}
   if(pts.length<4)continue;geos.push(taperTube(pts,0.088-0.032*Math.abs(spread)/1.3,0.012,10));
   for(let j=2;j<pts.length-1;j++)if(R()<0.8){const qv=[pts[j].clone()];let a2=ang+(R()<0.5?-1:1)*(0.7+R()*0.6),pp=pts[j].clone();const n2=3+Math.floor(R()*4);
    for(let s=0;s<n2;s++){const len=0.2+R()*0.12;a2+=(R()-0.5)*0.5;pp=pp.clone();pp.x+=Math.sin(a2)*len;pp.y-=Math.cos(a2)*len*0.8;pp.z+=(R()-0.5)*0.16;fix(pp,-0.85);if(pp.y<0.1)break;qv.push(pp)}
    if(qv.length>=3)geos.push(taperTube(qv,0.03,0.006,6,5))}}
  for(const sg of[-1,1]){const pts=[base.clone(),V3(sg*0.55,2.95,-1.25),V3(sg*1.15,2.55,-0.55),V3(sg*1.52,2.05,0.1),V3(sg*1.62,1.6,0.45),V3(sg*1.5,1.28,0.6)];geos.push(taperTube(pts,0.06,0.014,10));
   geos.push(taperTube([pts[3].clone(),V3(sg*1.85,1.8,0.35),V3(sg*2.1,1.45,0.5),V3(sg*2.2,1.1,0.45)],0.026,0.006,6,5));
   geos.push(taperTube([pts[2].clone(),V3(sg*1.45,2.6,-0.9),V3(sg*1.9,2.4,-1.0),V3(sg*2.3,2.05,-0.9)],0.03,0.006,6,5))}
  const rootMat=new THREE.MeshStandardMaterial({color:'#dcb98c',roughness:0.72,bumpMap:grain,bumpScale:1.2});
  const m=new THREE.Mesh(BGU.mergeGeometries(geos),rootMat);m.castShadow=m.receiveShadow=true;scene.add(m);
  const crown=new THREE.Mesh(new THREE.SphereGeometry(0.2,20,14),rootMat);crown.scale.set(1,0.7,1);crown.position.copy(base);scene.add(crown);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(0.115,0.16,2.4,18),new THREE.MeshStandardMaterial({color:'#5aa53c',roughness:0.6}));stem.position.set(0,TOP+1.2,-1.72);scene.add(stem);
 }
 // erba
 { const g=new THREE.PlaneGeometry(0.06,0.36,1,5);g.translate(0,0.18,0);const p=g.attributes.position;for(let i=0;i<p.count;i++){const y=p.getY(i)/0.36;p.setX(i,p.getX(i)*(1-0.88*y));p.setZ(i,0.14*y*y)}g.computeVertexNormals();
  const N=620,m=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({roughness:0.7,side:THREE.DoubleSide}),N);const GC=['#5fae3f','#4c9a35','#78c04e','#3f8a30','#8ccf5a'].map(c=>new THREE.Color(c));
  for(let i=0;i<N;i++){const x=(R()-0.5)*9.6,z=wallZ(x,TOP)-0.02-R()*0.42,s=0.7+R()*1.1;eu.set((R()-0.5)*0.3,(R()-0.5)*1.8,(R()-0.5)*0.7);q.setFromEuler(eu);mx.compose(V3(x,TOP-0.06+0.05*(fbm(x*2.2,3,5,3)-0.5),z),q,V3(1+R()*0.6,s,1));m.setMatrixAt(i,mx);m.setColorAt(i,GC[Math.floor(R()*GC.length)])}
  scene.add(m);
 }
 // pulviscolo luminoso
 const acc=new THREE.Color(EL[VID.bully].l);
 const NPa=80,dust=new THREE.InstancedMesh(new THREE.SphereGeometry(1,8,6),new THREE.MeshBasicMaterial({color:new THREE.Color(3.2,2.0,0.8).lerp(new THREE.Color(acc.r*3,acc.g*3,acc.b*3),0.3)}),NPa);
 const dp=[];for(let i=0;i<NPa;i++)dp.push({x:(R()-0.5)*4.6,y:R()*3.1,z:-1.5+R()*2.6,s:0.008+R()*0.016,v:0.05+R()*0.09,ph:R()*6.3});scene.add(dust);

 // ---------------------------------------------------------------- luci
 scene.add(new THREE.HemisphereLight('#fff1dc','#5a3a22',0.55));
 const key=new THREE.DirectionalLight('#fff0dc',2.9);key.position.set(-3.4,6.8,5.6);key.target.position.set(0,1,0);key.castShadow=true;key.shadow.mapSize.set(2048,2048);
 Object.assign(key.shadow.camera,{left:-4.2,right:4.2,top:4.6,bottom:-2.2,near:1,far:24});key.shadow.bias=-0.0004;key.shadow.normalBias=0.03;scene.add(key,key.target);
 const rim=new THREE.DirectionalLight('#cfe2ff',1.5);rim.position.set(3.4,4.8,-3);rim.target.position.set(0,1.1,0);scene.add(rim,rim.target);
 const fill=new THREE.DirectionalLight('#ffe6cc',0.55);fill.position.set(4,2.2,6);fill.target.position.set(0,1,0);scene.add(fill,fill.target);
 const glow=new THREE.PointLight('#ff9a35',30,8,2);glow.position.set(0,1.25,-1.55);scene.add(glow);

 // ---------------------------------------------------------------- personaggi
 const single=VID.v.length===1;
 const bully=buildSack(VID.bully,VID.id.charCodeAt(0));bully.root.position.set(single?-0.22:0,0,-0.2);scene.add(bully.root);
 const victims=VID.v.map((k,i)=>{const side=single?1:(i===0?-1:1);const b=buildBall(k,side);b.home=V3(side*1.07,0,0.8);b.root.position.copy(b.home);scene.add(b.root);return b});
 const linkGeo=new THREE.TorusGeometry(0.042,0.0135,8,18);linkGeo.scale(1.45,1,1);
 const chains=victims.map(v=>{const m=new THREE.InstancedMesh(linkGeo,M.gold,48);m.castShadow=true;m.frustumCulled=false;scene.add(m);return{m,v,L:null}});
 let tags=null;
 if(VID.nh4){const tx=canvasTex(512,300,(g,w,h)=>{g.fillStyle='#1f66c4';g.beginPath();g.roundRect(0,0,w,h,70);g.fill();g.strokeStyle='#ffffff';g.lineWidth=16;g.beginPath();g.roundRect(14,14,w-28,h-28,58);g.stroke();
   g.fillStyle='#fff';g.textAlign='center';g.textBaseline='middle';g.font='700 170px P';g.fillText('NH',w/2-58,h/2+8);g.font='700 100px P';g.fillText('4',w/2+112,h/2+56);g.fillText('+',w/2+118,h/2-58)});
  tx.anisotropy=8;const mat=new THREE.MeshStandardMaterial({map:tx,roughness:0.4,transparent:true,emissive:'#123a78',emissiveIntensity:0.25});
  tags=[];const P=[[-0.62,2.35,0.55],[0.7,2.5,0.5],[-1.42,1.62,0.3],[1.46,1.5,0.35],[-0.52,0.15,1.55],[0.5,0.13,1.6],[-1.5,0.98,-0.2],[1.52,1.04,-0.15]];
  for(const p of P){const m=new THREE.Mesh(new THREE.PlaneGeometry(0.4,0.235),mat);m.userData.p=V3(...p);m.userData.ph=R()*6.3;m.castShadow=true;scene.add(m);tags.push(m)}}

 // ---------------------------------------------------------------- post
 const rt=new THREE.WebGLRenderTarget(W,H,{type:THREE.HalfFloatType,samples:aa==='msaa'?4:0});
 const composer=new EffectComposer(renderer,rt);composer.addPass(new RenderPass(scene,cam));
 let gtao=null;
 if(ao){gtao=new GTAOPass(scene,cam,W,H);const ss=gtao.setSize.bind(gtao);gtao.setSize=(w,h)=>ss(Math.round(w*aos),Math.round(h*aos));gtao.output=gout;gtao.setSize(W,H);
  gtao.updateGtaoMaterial({radius:0.32,distanceExponent:1.3,thickness:1.2,scale:1.25,samples:9,distanceFallOff:1,screenSpaceRadius:false});
  gtao.updatePdMaterial({lumaPhi:10,depthPhi:2,normalPhi:3,radius:5,radiusExponent:1,rings:2,samples:8});gtao.blendIntensity=1.0;composer.addPass(gtao)}
 const bloom=new UnrealBloomPass(new THREE.Vector2(W,H),0.32,0.55,1.25);composer.addPass(bloom);
 const vig=new ShaderPass(VignetteShader);vig.uniforms.offset.value=0.95;vig.uniforms.darkness.value=1.15;composer.addPass(vig);
 composer.addPass(new OutputPass());
 let smaa=null;if(aa==='smaa'){smaa=new SMAAPass(W,H);composer.addPass(smaa)}else if(aa==='fxaa'){const f=new ShaderPass(FXAAShader);f.uniforms.resolution.value.set(1/W,1/H);composer.addPass(f)}

 // ---------------------------------------------------------------- animazione
 const L=VID.tl.map(l=>{const e=l.env,s=e.map((v,i)=>((e[i-1]??v)+2*v+(e[i+1]??v))/4);return{...l,end:l.start+l.dur,sm:s}});
 const cta=L.find(l=>l.cta),tEnd=VID.total;
 const env=(l,t)=>{if(!l||t<l.start||t>=l.end)return 0;const f=(t-l.start)*30,i=Math.floor(f),a=l.sm[Math.min(i,l.sm.length-1)]||0,b=l.sm[Math.min(i+1,l.sm.length-1)]||0;return lerp(a,b,f-i)};
 const win=(l,t,a=0.12,b=0.22)=>l?sstep(l.start-a,l.start+0.1,t)*(1-sstep(l.end-0.02,l.end+b,t)):0;
 const blink=(t,seed)=>{const per=2.6+seed*0.9,ph=((t+seed*1.7)%per)/per*per;return ph<0.14?Math.sin(ph/0.14*Math.PI):0};
 // inquadrature
 const shots=[];const A={t0:0,pos:tt=>V3(lerp(-0.55,0.32,tt),lerp(1.86,1.6,tt),lerp(8.05,6.85,tt)),tgt:tt=>V3(0,lerp(1.6,1.48,tt),0)};shots.push(A);
 victims.forEach((v,i)=>{const l=L[i+1],sx=v.side;shots.push({t0:l.start-0.3,pos:tt=>V3(sx*lerp(0.35,0.5,tt),lerp(0.98,0.9,tt),lerp(4.35,4.0,tt)),tgt:()=>V3(sx*0.9,0.6,0.7)})});
 shots.push({t0:cta.start-0.25,pos:tt=>V3(lerp(0.2,-0.15,tt),lerp(1.74,1.8,tt),lerp(7.5,8.1,tt)),tgt:()=>V3(0,1.56,0)});
 shots.forEach((s,i)=>{s.t1=i<shots.length-1?shots[i+1].t0:tEnd});
 const camState=(s,t)=>{const tt=clamp((t-s.t0)/(s.t1-s.t0+0.7));const e=1-(1-tt)*(1-tt);return[s.pos(e),s.tgt(e)]};
 const tmpA=V3(0,0,0),tmpB=V3(0,0,0),Xa=V3(1,0,0),qx=new THREE.Quaternion().setFromAxisAngle(Xa,Math.PI/2),one=V3(1,1,1);
 function setChain(c,A,B){const d=A.distanceTo(B);if(c.L===null)c.L=d*1.07;const Lc=Math.max(c.L,d*1.005);const dip=Math.sqrt(Math.max(0,3*d*(Lc-d)/8));
  const mid=A.clone().add(B).multiplyScalar(0.5);mid.y-=dip*2;const cv=new THREE.QuadraticBezierCurve3(A,mid,B);const n=Math.min(48,Math.round(c.L/0.092));
  for(let i=0;i<n;i++){const u=(i+0.5)/n,p=cv.getPointAt(u),tg=cv.getTangentAt(u);q.setFromUnitVectors(Xa,tg);if(i%2)q.multiply(qx);mx.compose(p,q,one);c.m.setMatrixAt(i,mx)}
  c.m.count=n;c.m.instanceMatrix.needsUpdate=true}

 function update(t){
  const a0=win(L[0],t),e0=env(L[0],t),cw=win(cta,t,0.2,5);
  const av=victims.map((v,i)=>win(L[i+1],t)),ev=victims.map((v,i)=>env(L[i+1],t));
  const anyV=av.reduce((s,x)=>s+x,0);
  // --- sacco
  { const b=bully,br=Math.sin(t*2.4),st=Math.sin(t*8.6);
   const sy=1+0.012*br+0.04*e0*a0;b.body.scale.set(1-0.5*(sy-1),sy,1-0.5*(sy-1));
   let ry=0,gx=0.12*Math.sin(t*1.7),gy=-0.04;victims.forEach((v,i)=>{ry+=v.side*0.2*av[i];gx+=v.side*0.6*av[i];gy-=0.42*av[i]});
   b.body.rotation.set(0.07*a0+0.04*e0*a0+0.03*anyV,ry,0.028*Math.sin(t*3.1)*a0);
   b.body.position.y=0.03*Math.abs(st)*a0;
   b.legs[0].position.y=0.05*Math.max(0,st)*a0;b.legs[1].position.y=0.05*Math.max(0,-st)*a0;
   b.arms.forEach((arm,s)=>{const sg=s===0?-1:1,vi=victims.findIndex(v=>v.side===sg),tug=vi>=0?av[vi]:0,pump=Math.sin(t*8.6+s*1.3)*a0;
    const free=single&&sg===-1; // braccio senza catena: pugno sul fianco
    const d1=free?V3(sg*0.9,-0.38,0.2):V3(sg*0.92,0.22+0.2*e0*a0+0.1*pump+0.16*tug,0.3);
    const d2=free?V3(-sg*0.72,-0.25+0.1*e0*a0,0.55):V3(sg*(0.1-0.1*tug),0.95,0.28+0.16*pump);
    arm.set(b.shoulder(sg),d1,d2,sg*0.5)});
   b.face.set({open:0.66+0.1*e0*a0,slant:0.44,brow:0.5+0.12*e0*a0,browY:-0.028-0.012*a0,gx,gy,mo:a0>0.3?Math.max(e0,0.06):0.0,grit:a0>0.3?0:1,blink:blink(t,0.3)});
  }
  // --- palline
  victims.forEach((v,i)=>{const a=av[i],e=ev[i],l=L[i+1],fear=a0*(1-a),other=clamp(anyV-a),s=v.side;
   const hop=Math.abs(Math.sin((t-l.start)*7.4))*a*(0.35+0.65*e),jx=(vnoise(t*24,i*7.1,0.5)-0.5)*0.022*fear,jz=(vnoise(t*24,i*7.1,9.5)-0.5)*0.016*fear;
   v.root.position.set(v.home.x+jx-s*0.05*a,v.home.y+0.085*hop,v.home.z+jz+0.07*a);
   const sq=1+0.07*hop-0.035*fear*Math.abs(Math.sin(t*9+i))-0.02*Math.sin(t*2.1+i);v.body.scale.set(1-0.45*(sq-1),sq,1-0.45*(sq-1));v.body.position.y=v.R*sq;
   v.root.rotation.y=-s*(0.14+0.26*fear+0.22*other-0.08*a)+0.06*Math.sin(t*1.3+i)*a;
   v.body.rotation.z=s*0.07*fear+0.05*Math.sin(t*5.2+i)*a;v.body.rotation.x=-0.16-0.1*fear+0.05*a*Math.sin(t*3.7);
   const wR=clamp(1-a-fear),k=Math.sin(t*6.2+i*2),tau=clamp((t-l.start)/l.dur),pw=sstep(0.08,0.3,tau)*(1-sstep(0.62,0.85,tau));
   v.arms.forEach((arm,j)=>{const sg=j===0?-1:1,inner=sg===-s?pw:0;
    const sh1=V3(sg*0.85,-0.28+0.06*k,0.35).lerp(V3(sg*0.75,0.2,0.1),inner),sh2=V3(sg*0.78,0.48+0.1*k*sg,0.42).lerp(V3(sg*0.85,0.5+0.06*k,-0.1),inner);
    const d1=V3(sg*0.6,-0.75,0.22).multiplyScalar(wR).add(sh1.multiplyScalar(a)).add(V3(sg*0.5,-0.05,0.85).multiplyScalar(fear));
    const d2=V3(-sg*0.35,-0.62,0.7).multiplyScalar(wR).add(sh2.multiplyScalar(a)).add(V3(-sg*0.7,0.55+0.1*Math.sin(t*19+j),0.45).multiplyScalar(fear));
    arm.set(v.shoulder(sg),d1,d2)});
   v.face.set({open:0.98+0.2*fear+0.08*a,low:1.12,slant:-0.3,brow:-0.42-0.1*fear,browY:0.008+0.02*fear+0.012*a*e,
    gx:-s*(0.42*fear+0.45*other)*(1-cw),gy:0.36*fear+0.05*a,mo:a>0.3?Math.max(e,0.07):0,blink:blink(t,0.9+i*0.7)})});
  // --- catene
  scene.updateMatrixWorld(true);
  chains.forEach(c=>{const sg=c.v.side,arm=bully.arms[sg===-1?0:1];tmpA.copy(arm.handPos);tmpA.y-=0.02;bully.body.localToWorld(tmpA);c.v.anchor.getWorldPosition(tmpB);setChain(c,tmpA.clone(),tmpB.clone())});
  // --- NH4
  if(tags)tags.forEach((m,i)=>{const p=m.userData.p,ph=m.userData.ph;m.position.set(p.x+0.05*Math.sin(t*1.1+ph),p.y+0.07*Math.sin(t*1.7+ph),p.z);m.quaternion.copy(cam.quaternion);m.rotateZ(0.12*Math.sin(t*1.3+ph))});
  // --- pulviscolo
  dp.forEach((d,i)=>{const y=(d.y+t*d.v)%3.1,s=d.s*(0.7+0.3*Math.sin(t*3+d.ph));mx.compose(tmpA.set(d.x+0.08*Math.sin(t*0.7+d.ph),y,d.z),q.identity(),tmpB.set(s,s,s));dust.setMatrixAt(i,mx)});dust.instanceMatrix.needsUpdate=true;
  glow.intensity=30+4*Math.sin(t*5.3)+2.5*Math.sin(t*9.1)+10*e0*a0;
  // --- camera
  let k=0;for(let i=0;i<shots.length;i++)if(t>=shots[i].t0)k=i;
  let[p,g]=camState(shots[k],t);
  if(k>0){const w=ease((t-shots[k].t0)/0.75);if(w<1){const[p0,g0]=camState(shots[k-1],t);p=p0.lerp(p,w);g=g0.lerp(g,w)}}
  p.x+=0.03*Math.sin(t*0.9);p.y+=0.02*Math.sin(t*1.3+1);cam.position.copy(p);cam.lookAt(g);
 }
 function render(){composer.render();renderer.getContext().finish()}
 return{update,render,scene,cam,renderer,bully,victims,total:tEnd,gtao,composer};
}
