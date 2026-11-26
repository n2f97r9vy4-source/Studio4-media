import * as THREE from 'three';
export const lerp=(a,b,t)=>a+(b-a)*t;
export const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
export const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)};
export const ease=t=>{t=clamp(t);return t*t*t*(t*(6*t-15)+10)};
export function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function h3(x,y,z){let h=Math.imul(x,374761393)^Math.imul(y,668265263)^Math.imul(z,1274126177);h=Math.imul(h^(h>>>13),1103515245);return((h^(h>>>16))>>>0)/4294967296}
export function vnoise(x,y,z){const xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z),xf=x-xi,yf=y-yi,zf=z-zi;
 const s=t=>t*t*(3-2*t),u=s(xf),v=s(yf),w=s(zf);
 const c=(a,b,c2)=>h3(xi+a,yi+b,zi+c2);
 return lerp(lerp(lerp(c(0,0,0),c(1,0,0),u),lerp(c(0,1,0),c(1,1,0),u),v),lerp(lerp(c(0,0,1),c(1,0,1),u),lerp(c(0,1,1),c(1,1,1),u),v),w)}
export function fbm(x,y,z,oct=4){let a=.5,f=1,s=0,n=0;for(let i=0;i<oct;i++){s+=a*vnoise(x*f,y*f,z*f);n+=a;a*=.5;f*=2.03}return s/n}
export function canvasTex(w,h,draw,{srgb=true,repeat=null}={}){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);
 const t=new THREE.CanvasTexture(c);if(srgb)t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;
 if(repeat){t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeat[0],repeat[1])}return t}
export function gridIndex(nr,nc){const idx=[];for(let r=0;r<nr-1;r++)for(let i=0;i<nc-1;i++){const a=r*nc+i,b=a+1,c=a+nc,d=c+1;idx.push(a,b,c,b,d,c)}return idx}
// orienta le facce verso l'esterno (volume con segno positivo)
export function orient(geo){const p=geo.attributes.position,ix=geo.index.array;let vol=0;const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
 const ctr=new THREE.Vector3();geo.computeBoundingBox();geo.boundingBox.getCenter(ctr);
 for(let i=0;i<ix.length;i+=3){a.fromBufferAttribute(p,ix[i]).sub(ctr);b.fromBufferAttribute(p,ix[i+1]).sub(ctr);c.fromBufferAttribute(p,ix[i+2]).sub(ctr);vol+=a.dot(b.cross(c))}
 if(vol<0){for(let i=0;i<ix.length;i+=3){const t=ix[i+1];ix[i+1]=ix[i+2];ix[i+2]=t}geo.index.needsUpdate=true}
 geo.computeVertexNormals();return geo}
export function makeGeo(pos,uv,idx){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));if(uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);return orient(g)}
// tubo che si assottiglia lungo una curva
export function taperTube(points,r0,r1,radial=8,segPer=6){const curve=new THREE.CatmullRomCurve3(points,false,'catmullrom',0.5);const N=Math.max(8,points.length*segPer);
 const fr=curve.computeFrenetFrames(N,false);const pos=[],uv=[];
 for(let i=0;i<=N;i++){const u=i/N,p=curve.getPointAt(u),r=lerp(r0,r1,Math.pow(u,0.75));
  for(let j=0;j<=radial;j++){const a=j/radial*Math.PI*2,cs=Math.cos(a),sn=Math.sin(a);
   pos.push(p.x+r*(cs*fr.normals[i].x+sn*fr.binormals[i].x),p.y+r*(cs*fr.normals[i].y+sn*fr.binormals[i].y),p.z+r*(cs*fr.normals[i].z+sn*fr.binormals[i].z));uv.push(j/radial,u*N/4)}}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(gridIndex(N+1,radial+1));
 // orientamento: confronto la normale del primo triangolo con la direzione radiale
 g.computeVertexNormals();const n=new THREE.Vector3().fromBufferAttribute(g.attributes.normal,0),p0=new THREE.Vector3().fromBufferAttribute(g.attributes.position,0).sub(curve.getPointAt(0));
 if(n.dot(p0)<0){const ix=g.index.array;for(let i=0;i<ix.length;i+=3){const t=ix[i+1];ix[i+1]=ix[i+2];ix[i+2]=t}g.computeVertexNormals()}
 return g}
export function superXZ(th,a,b,n){const c=Math.cos(th),s=Math.sin(th),e=2/n;return [a*Math.sign(c)*Math.pow(Math.abs(c),e),b*Math.sign(s)*Math.pow(Math.abs(s),e)]}
export function capsuleY(r,len,seg=20){const g=new THREE.CapsuleGeometry(r,len,10,seg);g.translate(0,len/2,0);return g}
export const lum=hex=>{const c=new THREE.Color(hex);return 0.2126*c.r+0.7152*c.g+0.0722*c.b};
