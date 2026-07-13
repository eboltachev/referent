export type JobStatus = {
  id: string;
  status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'ERROR' | 'CANCELLED' | string;
  progress_percent: number;
  current_step?: string | null;
  error_message?: string | null;
};

export type Speaker = {
  speaker_label: string;
  speaker_name: string | null;
};

export type TranscriptSegment = {
  id: string;
  speaker_label: string;
  speaker_name: string | null;
  start_seconds: number;
  end_seconds: number;
  language: string;
  text: string;
};

export type JobResults = {
  speakers: Speaker[];
  segments: TranscriptSegment[];
};
