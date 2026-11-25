"""Local-only synthetic document lifecycle. No real printers or records."""
import sqlite3, json, html, hashlib, io, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from reportlab.pdfgen import canvas
DB=os.environ.get('DOCUMENTFLOW_DB','documentflow.sqlite')
def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.executescript('CREATE TABLE IF NOT EXISTS docs(id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL, pdf BLOB, digest TEXT); CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, id TEXT, event TEXT);')
    return c

def submit(c, id, title):
    if not id or not title: raise ValueError('id and title required')
    with c:
        c.execute('INSERT INTO docs(id,title,status) VALUES(?,?,?)',(id,title,'queued'))
        c.execute('INSERT INTO audit(id,event) VALUES(?,?)',(id,'submitted'))

def process(c,id):
    with c:
        d=c.execute('SELECT * FROM docs WHERE id=?',(id,)).fetchone()
        if d is None: raise KeyError(id)
        if d['status']=='archived': return
        b=io.BytesIO(); p=canvas.Canvas(b,invariant=1); p.drawString(72,720,'Synthetic document: '+id); p.drawString(72,690,d['title']); p.save(); pdf=b.getvalue()
        c.execute('UPDATE docs SET status=?,pdf=?,digest=? WHERE id=?',('archived',pdf,hashlib.sha256(pdf).hexdigest(),id))
        c.execute('INSERT INTO audit(id,event) VALUES(?,?)',(id,'archived'))

def records(c):
    return [dict(r) for r in c.execute('SELECT id,title,status,digest FROM docs ORDER BY id')]

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,body,kind='application/json'):
        if not isinstance(body,bytes): body=json.dumps(body).encode() if kind=='application/json' else body.encode()
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        with connect() as c:
            if self.path=='/api/records': return self.reply(200,records(c))
            if self.path=='/api/audit': return self.reply(200,[dict(r) for r in c.execute('SELECT * FROM audit ORDER BY seq')])
            if self.path.startswith('/api/pdf/'):
                d=c.execute('SELECT pdf FROM docs WHERE id=?',(self.path[9:],)).fetchone()
                return self.reply(200,d['pdf'],'application/pdf') if d and d['pdf'] else self.reply(404,{'error':'not archived'})
            if self.path!='/': return self.reply(404,{'error':'not found'})
            rows=''.join(f'<tr><td>{html.escape(r["id"])}</td><td>{html.escape(r["title"])}</td><td>{r["status"]}</td></tr>' for r in records(c))
            self.reply(200,'''<!doctype html><html><meta charset=utf-8><title>DocumentFlow QA Lab</title><style>body{font:16px system-ui;max-width:850px;margin:40px auto;padding:20px;color:#193553}button,input{padding:9px;margin:5px}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}</style><h1>DocumentFlow QA Lab</h1><p>Local synthetic print-to-archive workflow</p><label>Document ID <input id="doc-id"></label><label>Title <input id="title"></label><button id="submit">Submit</button><button id="process">Process</button><p id="message" role="status"></p><table><thead><tr><th>ID</th><th>Title</th><th>Status</th></tr></thead><tbody>'''+rows+'''</tbody></table><script>for(const action of ['submit','process'])document.getElementById(action).onclick=async()=>{const r=await fetch('/api/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:document.getElementById('doc-id').value,title:document.getElementById('title').value})});if(r.ok)location.reload();else document.getElementById('message').textContent=(await r.json()).error;};</script></html>''','text/html; charset=utf-8')
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length',0)); assert 0<n<=8192
            d=json.loads(self.rfile.read(n)); id=d['id']; title=d.get('title','')
            if not isinstance(id,str) or not isinstance(title,str) or not id.isalnum() or len(id)>40 or len(title)>120: raise ValueError('invalid input')
            with connect() as c:
                if self.path=='/api/submit': submit(c,id,title)
                elif self.path=='/api/process': process(c,id)
                else: return self.reply(404,{'error':'not found'})
            self.reply(200,{'ok':True})
        except sqlite3.IntegrityError: self.reply(409,{'error':'duplicate document'})
        except KeyError: self.reply(404,{'error':'missing document or input'})
        except (ValueError,AssertionError,TypeError): self.reply(400,{'error':'invalid input'})
if __name__=='__main__': ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
