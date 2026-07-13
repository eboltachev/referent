import type { TranscriptSegment } from '../types';

const mm = (seconds: number) =>
  `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;

type Props = { segments: TranscriptSegment[] };

export default function TranscriptPanel({ segments }: Props) {
  return (
    <div className="panel">
      <h3>Стенограмма</h3>
      {segments.length === 0 && <p>Речь не найдена.</p>}
      {segments.map((segment) => (
        <div className="seg" key={segment.id}>
          <b>{segment.speaker_name || segment.speaker_label}</b>
          <small>{mm(segment.start_seconds)}–{mm(segment.end_seconds)}</small>
          <p>{segment.text}</p>
        </div>
      ))}
    </div>
  );
}
