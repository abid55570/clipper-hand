export interface Video {
  id: string;
  filename: string;
  original_name: string;
  file_size_bytes: number;
  duration_secs: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  codec: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Clip {
  id: string;
  video_id: string;
  label: string | null;
  start_time: number;
  end_time: number;
  duration_secs: number | null;
  file_size_bytes: number | null;
  status: string;
  parent_clip_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  celery_task_id: string | null;
  job_type: string;
  status: string;
  progress_pct: number;
  result_json: Record<string, unknown> | null;
  error_message: string | null;
  retry_count: number;
  video_id: string | null;
  clip_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClipTimestamp {
  start: number;
  end: number;
  label: string;
}

export interface CaptionSegment {
  id: string;
  segment_index: number;
  start_time: number;
  end_time: number;
  text: string;
  words: WordTimestamp[] | null;
}

export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
  probability: number | null;
}

export interface Caption {
  id: string;
  video_id: string;
  model_size: string;
  language: string | null;
  full_text: string | null;
  status: string;
  segments: CaptionSegment[];
  created_at: string;
}

export interface CaptionStyle {
  font_family: string;
  font_size: number;
  primary_color: string;
  outline_color: string;
  highlight_color: string;
  highlight_words: string[];
  position: string;
  bold: boolean;
  animation_type: string;
}

export interface Highlight {
  id: string;
  start_time: number;
  end_time: number;
  score: number | null;
  reason: string | null;
  source: string | null;
}

export interface ExportConfig {
  aspect_ratio: string;
  platform?: string;
  effects?: {
    zoom: boolean;
    jump_cut: boolean;
    jump_cut_threshold_db?: number;
    jump_cut_min_silence?: number;
    text_animation?: string;
    text_content?: string;
  };
}

export interface Export {
  id: string;
  clip_id: string;
  job_id: string | null;
  aspect_ratio: string;
  platform: string | null;
  width: number | null;
  height: number | null;
  file_size_bytes: number | null;
  status: string;
  created_at: string;
}

export interface HookItem {
  text: string;
  style: string;
}

export interface ContentResult {
  title: string;
  description: string;
  hashtags: string[];
}
