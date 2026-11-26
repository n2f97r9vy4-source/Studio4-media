// node render.js <vid> <stage|overlay> [fps]
const {chromium}=require('playwright');const {start}=require('./srv.js');const {spawn}=require('child_process');
(async()=>{const [vid,mode,fpsArg]=process.argv.slice(2);const FPS=+(fpsArg||24);const s=await start(__dirname);const port=s.address().port;
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(`http://127.0.0.1:${port}/scene.html?vid=${vid}&mode=${mode}`);await p.waitForFunction('window.ready===true',{timeout:180000});
const total=await p.evaluate(()=>window.total),N=Math.ceil(total*FPS);
const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-c:v','mjpeg','-framerate',String(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','9','-pix_fmt','yuv444p',`${mode}_${vid}.mp4`],{stdio:['pipe','inherit','inherit']});
const t0=Date.now();
for(let i=0;i<N;i++){let buf;
 if(mode==='stage'){const d=await p.evaluate(t=>frameJPEG(t),i/FPS);buf=Buffer.from(d.slice(d.indexOf(',')+1),'base64')}
 else{await p.evaluate(t=>renderFrame(t),i/FPS);buf=await p.screenshot({type:'jpeg',quality:96})}
 if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if(i%24===0)console.log(vid,mode,i,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s')}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();s.close();console.log('DONE',vid,mode,N,((Date.now()-t0)/1000).toFixed(0)+'s')})();
