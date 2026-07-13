import type { JobResults } from '../types';
import QuestionPanel from './QuestionPanel';
import SpeakersPanel from './SpeakersPanel';
import TranscriptPanel from './TranscriptPanel';

type Props = { jobId: string; results: JobResults; reload: () => void };

export default function ResultsBlock({ jobId, results, reload }: Props) {
  return (
    <section className="results">
      <QuestionPanel jobId={jobId} />
      <div className="columns">
        <SpeakersPanel jobId={jobId} speakers={results.speakers} onUpdate={reload} />
        <TranscriptPanel segments={results.segments} />
      </div>
      <a className="download" href={`/api/jobs/${jobId}/download`}>Скачать</a>
    </section>
  );
}
