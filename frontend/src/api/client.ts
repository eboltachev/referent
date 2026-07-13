export type JobStatus={id:string,status:string,progress_percent:number,current_step?:string,error_message?:string};
export async function uploadFile(file:File, recording=false){const fd=new FormData(); fd.append('file',file); const r=await fetch(recording?'/api/recordings':'/api/uploads',{method:'POST',body:fd}); return r.json();}
export async function getJob(id:string):Promise<JobStatus>{return (await fetch(`/api/jobs/${id}`)).json()}
export async function getResults(id:string){return (await fetch(`/api/jobs/${id}/results`)).json()}
export async function cancelJob(id:string){return (await fetch(`/api/jobs/${id}/cancel`,{method:'POST'})).json()}
export async function patchSpeaker(id:string,label:string,name:string){return (await fetch(`/api/jobs/${id}/speakers/${label}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({speaker_name:name})})).json()}
