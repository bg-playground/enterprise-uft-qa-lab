'use strict';
function validateSnapshot(d){
 const integer=n=>Number.isSafeInteger(n)&&n>=0;
 const sha=v=>typeof v==='string'&&/^[a-f0-9]{40}$/.test(v);
 const names=['Linux','Windows','macOS','Chromium'];
 if(!d||!integer(d.run)||!d.run||!sha(d.head)||!sha(d.checkout)||typeof d.note!=='string'||typeof d.url!=='string'||!/^https:\/\/github\.com\/bg-playground\/enterprise-uft-qa-lab\/actions\/runs\/[1-9]\d*$/.test(d.url)||!Array.isArray(d.jobs)||d.jobs.length!==4)throw Error('Invalid snapshot');
 if(new Set(d.jobs.map(j=>j?.name)).size!==4||new Set(d.jobs.map(j=>j?.artifact)).size!==4||d.jobs.some(j=>!j||!names.includes(j.name)||!integer(j.artifact)||!j.artifact||!['passed','failed','skipped'].every(k=>integer(j[k]))))throw Error('Invalid job data');
 for(const k of ['passed','failed','skipped'])if(!integer(d.jobs.reduce((sum,j)=>sum+j[k],0)))throw Error('Invalid totals');
}
async function load(){
 const response=await fetch('evidence.json');
 if(!response.ok)throw Error('Snapshot unavailable');
 const d=await response.json();validateSnapshot(d);
 const p=document.getElementById('provenance');
 p.textContent='Run #'+d.run+' · historical PR head '+d.head;
 const link=document.createElement('a');link.href=d.url;link.textContent=' View original CI run';p.append(link);
 const metrics=document.getElementById('metrics');
 for(const [label,key] of [['Passed','passed'],['Failed','failed'],['Skipped','skipped']]){
   const box=document.createElement('div');const n=document.createElement('strong');n.textContent=d.jobs.reduce((sum,j)=>sum+j[key],0);box.append(n,document.createTextNode(label+' method executions'));metrics.append(box);
 }
 for(const j of d.jobs){const row=document.createElement('tr');for(const value of [j.name,j.passed,j.failed,j.skipped]){const td=document.createElement('td');td.textContent=value;row.append(td);}const td=document.createElement('td');const a=document.createElement('a');a.href=d.url+'/artifacts/'+j.artifact;a.textContent='Archive';a.setAttribute('aria-label',j.name+' evidence archive');td.append(a);row.append(td);document.getElementById('jobs').append(row);}
 document.getElementById('note').textContent=d.note+' Artifact downloads may require GitHub sign-in and expire.';
}
load().catch(()=>{document.getElementById('metrics').replaceChildren();document.getElementById('jobs').replaceChildren();document.getElementById('note').textContent='';document.getElementById('provenance').textContent='Historical evidence unavailable; no results claimed.';});
