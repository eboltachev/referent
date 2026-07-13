import { useEffect, useState } from 'react';
import { cancelJob, getJob, getResults, uploadFile } from './api/client';
import CancelButton from './components/CancelButton';
import Header from './components/Header';
import RecordButton from './components/RecordButton';
import ResultsBlock from './components/ResultsBlock';
import UploadButton from './components/UploadButton';
import type { JobResults, JobStatus } from './types';

export default function App() {
  const [job, setJob] = useState<JobStatus | undefined>();
  const [results, setResults] = useState<JobResults | undefined>();
  const status = job ? `${job.progress_percent}% ${job.current_step || job.status}` : '';

  async function start(file: File, recording = false) {
    setResults(undefined);
    const created = await uploadFile(file, recording);
    setJob({ id: created.job_id, status: created.status, progress_percent: 0 });
  }

  async function reload() {
    if (job) setResults(await getResults(job.id));
  }

  useEffect(() => {
    if (!job?.id) return undefined;
    const timer = window.setInterval(() => {
      void (async () => {
        const latest = await getJob(job.id);
        setJob(latest);
        if (['SUCCESS', 'ERROR', 'CANCELLED'].includes(latest.status)) {
          window.clearInterval(timer);
          if (latest.status === 'SUCCESS') setResults(await getResults(job.id));
        }
      })();
    }, 1000);
    return () => window.clearInterval(timer);
  }, [job?.id]);

  const processing = job && ['PENDING', 'PROCESSING'].includes(job.status);

  return (
    <main>
      <Header />
      <div className="buttons">
        <UploadButton onFile={(file) => void start(file, false)} status={status} />
        <RecordButton onBlob={(file) => void start(file, true)} status={status} />
      </div>
      {processing && <CancelButton onCancel={() => void cancelJob(job.id)} />}
      {results && job && <ResultsBlock jobId={job.id} results={results} reload={() => void reload()} />}
    </main>
  );
}
