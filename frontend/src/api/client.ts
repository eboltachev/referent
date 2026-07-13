import type { JobResults, JobStatus } from '../types';

export async function uploadFile(file: File, recording = false): Promise<{ job_id: string; status: string }> {
  const fd = new FormData();
  fd.append('file', file);
  const response = await fetch(recording ? '/api/recordings' : '/api/uploads', { method: 'POST', body: fd });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function getJob(id: string): Promise<JobStatus> {
  const response = await fetch(`/api/jobs/${id}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function getResults(id: string): Promise<JobResults> {
  const response = await fetch(`/api/jobs/${id}/results`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function cancelJob(id: string): Promise<{ status: string }> {
  const response = await fetch(`/api/jobs/${id}/cancel`, { method: 'POST' });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function patchSpeaker(id: string, label: string, name: string): Promise<void> {
  const response = await fetch(`/api/jobs/${id}/speakers/${label}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ speaker_name: name }),
  });
  if (!response.ok) throw new Error(await response.text());
}
