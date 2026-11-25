'use strict';
async function load(){
 const response=await fetch('evidence.json');
 if(!response.ok)throw Error('Snapshot unavailable');
 const d=await response.json();
 const p=document.getElementById('provenance');
 p.textContent='Run #'+d.run+' · historical PR head '+d.head;
 const link=document.createElement('a');link.href=d.url;link.textContent=' View original CI run';p.append(link);
 const metrics=document.getElementById('metrics');
 for(const [label,key] of [['Passed','passed'],['Failed','failed'],['Skipped','skipped']]){
   const box=document.createElement('div');const n=document.createElement('strong');n.textContent=d.jobs.reduce((sum,j)=>sum+j[key],0);box.append(n,document.createTextNode(label+' method executions'));metrics.append(box);
 }
 for(const j of d.jobs){const row=document.createElement('tr');for(const value of [j.name,j.passed,j.failed,j.skipped]){const td=document.createElement('td');td.textContent=value;row.append(td);}const td=document.createElement('td');const a=document.createElement('a');a.href=d.url+'/artifacts/'+j.artifact;a.textContent='Archive';td.append(a);row.append(td);document.getElementById('jobs').append(row);}
 document.getElementById('note').textContent=d.note+' Artifact downloads may require GitHub sign-in and expire.';
}
load().catch(()=>{document.getElementById('provenance').textContent='Historical evidence unavailable; no results claimed.';});
