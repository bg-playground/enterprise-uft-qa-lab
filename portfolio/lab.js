'use strict';
const el=id=>document.getElementById(id);
let classified=false, held=false, disposed=false;
function audit(event){const li=document.createElement('li');li.textContent=event;el('audit').append(li);}
function render(){el('state').textContent=disposed?'Disposed':'Archived';el('retain').textContent=classified?'2026-01-31':'Not classified';el('hold-state').textContent=held?'Active':'Inactive';}
function result(message){el('record-result').textContent=message;render();}
function action(name){
 const role=el('role').value;
 if(role!==(name==='dispose'?'disposition':'manager'))return result('403 — Simulated role denied');
 if(disposed)return result('400 — Record already disposed');
 if(name==='classify'){if(classified)return result('409 — Already classified');classified=true;audit('Classified');return result('200 — Retention assigned');}
 if(!classified)return result('400 — Classification required');
 if(name==='dispose'){
  const date=el('when').value;
  if(!date)return result('400 — Date required');
  if(held||date<'2026-01-31')return result('409 — Retention or legal hold prevents disposition');
  disposed=true;audit('Disposed');return result('200 — Logical disposition complete');
 }
 const next=name==='hold';if(held!==next){held=next;audit(held?'Hold set':'Hold released');}
 return result('200 — Hold state updated');
}
for(const name of ['classify','hold','release','dispose'])el(name).addEventListener('click',()=>action(name));
el('reset').addEventListener('click',()=>{classified=held=disposed=false;el('role').value='viewer';el('when').value='2026-01-31';el('audit').replaceChildren();audit('Archived');result('Exercise reset');});
el('mutation').addEventListener('change',()=>{el('observed').textContent=el('mutation').checked?'Incorrect template title':'Invoice';el('defect-result').textContent='No comparison performed.';});
el('check').addEventListener('click',()=>{el('defect-result').textContent=el('observed').textContent==='Invoice'?'PASS — Content matches':'FAIL — Body title mismatch';});
audit('Archived');render();
