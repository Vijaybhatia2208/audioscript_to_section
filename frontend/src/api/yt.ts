import axios from 'axios';

export interface Cue {
  index: number;
  text: string;
  start_sec: number;

  duration_sec: number;
  end_sec: number;
  start_time_str: string;
  end_time_str: string;
  video_id: string;
}

export interface VideoInfoResponse {
  video_id: string;
  youtube_url: string;
  embed_url: string;
  thumbnail_url: string;
  total_duration_sec: number;
  total_duration_str: string;
  cue_count: number;
  cues: Cue[];
}

export interface SourceCitation {
  module_name?: string;
  lesson_name?: string;
  timestamp_range?: string;
  start_time_str?: string;
  end_time_str?: string;
  start_sec?: number;
  end_sec?: number;
  source_file?: string;
  score?: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceCitation[];
  model: string;
  video_id: string;
  query: string;
  retrieved_chunks_count: number;
}

export async function fetchYouTubeTranscript(url_or_id: string): Promise<VideoInfoResponse> {
  const response = await axios.post<VideoInfoResponse>('/api/yt/transcript', {
    url_or_id
  });
  return response.data;
}

export async function queryYouTubeVideo(url_or_id: string, query: string, limit = 5): Promise<QueryResponse> {
  const response = await axios.post<QueryResponse>('/api/yt/query', {
    url_or_id,
    query,
    limit
  });
  return response.data;
}
