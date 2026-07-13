import { useRef, useState } from 'react';

type Props = { onBlob: (file: File) => void; status?: string };

export default function RecordButton({ onBlob, status }: Props) {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const media = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const timer = useRef<number | undefined>();

  async function click() {
    if (!recording) {
      setSeconds(0);
      chunks.current = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      media.current = new MediaRecorder(stream);
      media.current.ondataavailable = (event: BlobEvent) => chunks.current.push(event.data);
      media.current.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        onBlob(new File([new Blob(chunks.current, { type: 'audio/webm' })], 'recording.webm'));
      };
      media.current.start();
      timer.current = window.setInterval(() => setSeconds((value) => value + 1), 1000);
      setRecording(true);
      return;
    }
    media.current?.stop();
    if (timer.current) window.clearInterval(timer.current);
    setRecording(false);
  }

  return (
    <button className="btn record" onClick={click}>
      {recording ? (
        <>
          <span className="dot" /> {String(Math.floor(seconds / 60)).padStart(2, '0')}:
          {String(seconds % 60).padStart(2, '0')}
        </>
      ) : (
        status || 'Записать'
      )}
    </button>
  );
}
