import { patchSpeaker } from '../api/client';
import type { Speaker } from '../types';

type Props = { jobId: string; speakers: Speaker[]; onUpdate: () => void };

export default function SpeakersPanel({ jobId, speakers, onUpdate }: Props) {
  return (
    <div className="panel">
      <h3>Спикеры</h3>
      {speakers.map((speaker) => (
        <div className="speaker" key={speaker.speaker_label}>
          <b>{speaker.speaker_label}</b>
          <input
            defaultValue={speaker.speaker_name || ''}
            onBlur={async (event) => {
              await patchSpeaker(jobId, speaker.speaker_label, event.currentTarget.value);
              onUpdate();
            }}
            placeholder="Имя спикера"
          />
        </div>
      ))}
    </div>
  );
}
