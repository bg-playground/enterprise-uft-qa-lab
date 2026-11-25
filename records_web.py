"""Loopback-only synthetic role simulation, not production authentication."""
import json
import sqlite3
from datetime import date
from urllib.parse import urlsplit, parse_qs
import record_policy

ROLES={'viewer':{'list','search'},'manager':{'list','search','classify','hold'},'disposition':{'list','search','dispose'}}

def allowed(h,action):
    role=h.headers.get('X-Lab-Role','')
    if action not in ROLES.get(role,set()):
        h.reply(403,{'error':'simulated role denied'})
        return False
    return True

def handle_get(h,c):
    url=urlsplit(h.path)
    action=url.path.rsplit('/',1)[-1]
    if action not in ('list','search'): return h.reply(404,{'error':'not found'})
    if not allowed(h,action): return
    if action=='search':
        q=parse_qs(url.query).get('q',[''])[0]
        if len(q)>120: return h.reply(400,{'error':'invalid query'})
        return h.reply(200,record_policy.search(c,q))
    rows=c.execute("""SELECT d.id,d.title,d.status,p.retain_until,p.legal_hold,p.disposed
        FROM docs d LEFT JOIN record_policy p ON d.id=p.id ORDER BY d.id""")
    return h.reply(200,[dict(row) for row in rows])

def handle_post(h,c):
    action=h.path.rsplit('/',1)[-1]
    if action not in ('classify','hold','dispose'): return h.reply(404,{'error':'not found'})
    if not allowed(h,action): return
    try:
        if h.headers.get_content_type()!='application/json': return h.reply(415,{'error':'JSON required'})
        n=int(h.headers.get('Content-Length',0))
        if not 0<n<=8192: raise ValueError('invalid length')
        d=json.loads(h.rfile.read(n))
        if not isinstance(d,dict): raise ValueError('object required')
        id=d.get('id')
        if not isinstance(id,str) or not id.isalnum() or len(id)>40: raise ValueError('invalid id')
        # Dates deliberately supplied by the lab participant; never a production clock.
        if action=='classify':
            record_policy.classify(c,id,date.fromisoformat(d['archived_on']),d['retention_days'])
        elif action=='hold':
            record_policy.hold(c,id,d['enabled'])
        else:
            changed=record_policy.dispose(c,id,date.fromisoformat(d['today']))
            return h.reply(200,{'ok':True,'changed':changed})
        return h.reply(200,{'ok':True})
    except PermissionError:
        return h.reply(409,{'error':'retention or legal hold prevents disposition'})
    except sqlite3.IntegrityError:
        return h.reply(409,{'error':'record already classified'})
    except (ValueError,TypeError,KeyError,OverflowError):
        return h.reply(400,{'error':'invalid input or record state'})

PAGE="""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Records management | DocumentFlow</title>
<style>body{font:16px system-ui;color:#193553;max-width:1000px;margin:30px auto;padding:16px}fieldset{border:1px solid #b6c4d4;border-radius:8px;margin:16px 0;padding:16px}label{display:inline-block;margin:6px}input,select,button{font:inherit;padding:8px;margin:4px}button{cursor:pointer}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}.scroll{overflow:auto}#result{white-space:pre-wrap}</style>
<a href="/">DocumentFlow / Document processing</a><h1>Records management lab</h1><p><strong>Synthetic local exercise:</strong> roles are simulated, not authenticated identities. Dates are controlled test inputs. Never use real records.</p>
<label>Simulated role <select id="role"><option>viewer</option><option>manager</option><option>disposition</option></select></label>
<button id="refresh">Refresh records</button>
<fieldset><legend>Policy operations</legend><label>Document ID <input id="id"></label><label>Archive date <input id="archived-on" type="date" value="2026-01-01"></label><label>Retention days <input id="days" type="number" min="1" max="3650" value="30"></label><button id="classify">Classify</button><button id="hold">Set hold</button><button id="release">Release hold</button><label>Simulated disposition date <input id="today" type="date" value="2026-01-31"></label><button id="dispose">Dispose</button></fieldset>
<label>Title search <input id="query"></label><button id="search">Search archived records</button><p id="result" role="status"></p>
<div class="scroll"><table><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Retain until</th><th>Hold</th></tr></thead><tbody id="rows"></tbody></table></div>
<script>
const el=id=>document.getElementById(id);
async function request(action,data,query=''){
 const options={headers:{'X-Lab-Role':el('role').value}};
 if(data){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(data);}
 const r=await fetch('/api/policy/'+action+query,options);const body=await r.json();
 if(!r.ok)throw Error(r.status+' '+body.error);return body;
}
function render(rows){el('rows').replaceChildren();for(const row of rows){const tr=document.createElement('tr');for(const key of ['id','title','status','retain_until','legal_hold']){const td=document.createElement('td');td.textContent=row[key]??'—';tr.append(td);}el('rows').append(tr);}}
async function refresh(){render(await request('list'));}
async function perform(fn){try{await fn();el('result').textContent='Success';}catch(e){el('result').textContent=e.message;}}
el('refresh').onclick=()=>perform(refresh);el('role').onchange=()=>perform(refresh);
el('search').onclick=()=>perform(async()=>render(await request('search',null,'?q='+encodeURIComponent(el('query').value))));
for(const action of ['classify','hold','release','dispose'])el(action).onclick=()=>perform(async()=>{let data={id:el('id').value};if(action==='classify')Object.assign(data,{archived_on:el('archived-on').value,retention_days:Number(el('days').value)});if(action==='hold'||action==='release')data.enabled=action==='hold';if(action==='dispose')data.today=el('today').value;await request(action==='release'?'hold':action,data);await refresh();});
perform(refresh);
</script></html>"""
