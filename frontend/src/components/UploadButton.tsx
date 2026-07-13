type Props = { onFile: (file: File) => void; status?: string };

export default function UploadButton({ onFile, status }: Props) {
  return (
    <label className="btn upload">
      {status || 'Загрузить'}
      <input
        hidden
        type="file"
        accept=".wav,.mp3,.m4a,.flac,.ogg,.webm,.mp4,.mov,.mkv,.avi,audio/*,video/*"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onFile(file);
          event.currentTarget.value = '';
        }}
      />
    </label>
  );
}
