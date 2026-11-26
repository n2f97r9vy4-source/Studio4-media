// node still.js <vid> <t1> <t2> ...   [env: MODE=both|stage, Q=extra query]
const {chromium}=require('playwright');const {start}=require('./srv.js');const fs=require('fs');
(async()=>{const s=await start(__dirname);const port=s.address().port;const [vid,...ts]=process.argv.slice(2);const mode=process.env.MODE||'both';
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{const t=m.text();if(!t.includes('GPU stall'))console.log('PAGE',t)});
await p.goto(`http://127.0.0.1:${port}/scene.html?vid=${vid}&mode=${mode}${process.env.Q||''}`);await p.waitForFunction('window.ready===true',{timeout:120000});
for(const t of ts){const t0=Date.now();
 if(mode==='stage'){const d=await p.evaluate(t=>frameJPEG(t),+t);fs.writeFileSync(`st_${vid}_${t}.jpg`,Buffer.from(d.split(',')[1],'base64'))}
 else{await p.evaluate(t=>renderFrame(t),+t);await p.screenshot({path:`st_${vid}_${t}.png`})}
 console.log(vid,t,'ms',Date.now()-t0)}
await b.close();s.close()})();
