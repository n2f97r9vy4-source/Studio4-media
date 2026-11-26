const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
(async()=>{const tl=JSON.parse(fs.readFileSync('timeline.json','utf8'));let h=fs.readFileSync('page.html','utf8').replace('__TL__',JSON.stringify(tl));fs.writeFileSync('page_r.html',h);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});await p.goto('file://'+process.cwd()+'/page_r.html');await p.waitForTimeout(500);
const N=Math.ceil(tl.total*30);
const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-i','-','-i','voce.wav','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart','video.mp4'],{stdio:['pipe','inherit','inherit']});
for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/30);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',N)})();
