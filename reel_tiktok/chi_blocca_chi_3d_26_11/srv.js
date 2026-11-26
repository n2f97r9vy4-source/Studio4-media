const http=require('http'),fs=require('fs'),path=require('path');
const MIME={'.html':'text/html','.js':'text/javascript','.json':'application/json','.png':'image/png','.ttf':'font/ttf','.wav':'audio/wav','.jpg':'image/jpeg'};
exports.start=(root,port=0)=>new Promise(res=>{const s=http.createServer((q,r)=>{let p=path.join(root,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>{if(e){r.writeHead(404);r.end();return}r.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});r.end(d)})});s.listen(port,'127.0.0.1',()=>res(s))});
