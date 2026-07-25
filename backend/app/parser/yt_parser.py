import re
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_youtube_video_id(url_or_id: str) -> Optional[str]:
    """
    Extracts the 11-character YouTube video ID from various URL formats or raw ID string.
    Examples:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ
        - https://www.youtube.com/embed/dQw4w9WgXcQ
        - dQw4w9WgXcQ
    """
    url_or_id = url_or_id.strip()
    if len(url_or_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    regex_patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?\/].*)?$',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/embed\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/watch\?.*v=([0-9A-Za-z_-]{11})'
    ]

    for pattern in regex_patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None


def fetch_youtube_transcript(url_or_id: str, languages: List[str] = ["en"]) -> Dict[str, Any]:
    """
    Fetches time-coded transcript cues for a YouTube video.

    Returns:
        Dict containing:
            - video_id: str
            - cues: List[Dict] with 'text', 'start_sec', 'duration_sec', 'end_sec', 'start_time_str', 'end_time_str'
    """
    video_id = extract_youtube_video_id(url_or_id)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL or Video ID: '{url_or_id}'")

    transcript_data = None
    
    try:
        api = YouTubeTranscriptApi()
        # Try direct fetch first
        if hasattr(api, "fetch"):
            transcript_data = api.fetch(video_id, languages=languages)
        elif hasattr(YouTubeTranscriptApi, "get_transcript"):
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except Exception as primary_err:
        try:
            api = YouTubeTranscriptApi()
            if hasattr(api, "list"):
                t_list = api.list(video_id)
            elif hasattr(YouTubeTranscriptApi, "list_transcripts"):
                t_list = YouTubeTranscriptApi.list_transcripts(video_id)
            else:
                raise primary_err

            try:
                transcript_obj = t_list.find_transcript(languages)
            except Exception:
                transcript_obj = next(iter(t_list))
                
            transcript_data = transcript_obj.fetch()
        except Exception as fallback_err:
            raise RuntimeError(f"Could not retrieve transcript for YouTube video '{video_id}': {str(primary_err)}")

    if not transcript_data:
        raise RuntimeError(f"No transcript content found for video: {video_id}")


    cues = []
    for idx, item in enumerate(transcript_data, start=1):
        # Handle dict or object attributes
        if isinstance(item, dict):
            text = item.get("text", "").replace("\n", " ").strip()
            start_sec = float(item.get("start", 0.0))
            duration_sec = float(item.get("duration", 0.0))
        else:
            text = getattr(item, "text", "").replace("\n", " ").strip()
            start_sec = float(getattr(item, "start", 0.0))
            duration_sec = float(getattr(item, "duration", 0.0))

        if not text:
            continue

        end_sec = start_sec + duration_sec

        def sec_to_str(s: float) -> str:
            hrs = int(s // 3600)
            mins = int((s % 3600) // 60)
            secs = int(s % 60)
            if hrs > 0:
                return f"{hrs:02d}:{mins:02d}:{secs:02d}"
            return f"{mins:02d}:{secs:02d}"

        cues.append({
            "index": idx,
            "text": text,
            "start_sec": start_sec,
            "duration_sec": duration_sec,
            "end_sec": end_sec,
            "start_time_str": sec_to_str(start_sec),
            "end_time_str": sec_to_str(end_sec),
            "video_id": video_id
        })

    return {
        "video_id": video_id,
        "cue_count": len(cues),
        "cues": cues
    }


def get_youtube_video_info(url_or_id: str, languages: List[str] = ["en"]) -> Dict[str, Any]:
    """
    Retrieves complete YouTube video metadata and time-coded transcript cues.

    Args:
        url_or_id (str): YouTube URL or 11-character Video ID string.
        languages (List[str]): Preferred subtitle languages (defaults to ['en']).

    Returns:
        Dict[str, Any]: Dictionary containing video_id, URLs, duration, cue count, and transcript cues.
    """
    video_id = extract_youtube_video_id(url_or_id)
    if not video_id:
        raise ValueError(f"Invalid YouTube URL or Video ID: '{url_or_id}'")

    transcript_res = fetch_youtube_transcript(video_id, languages=languages)
    cues = transcript_res["cues"]

    total_sec = cues[-1]["end_sec"] if cues else 0.0
    hrs = int(total_sec // 3600)
    mins = int((total_sec % 3600) // 60)
    secs = int(total_sec % 60)
    duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"

    return {
        "video_id": video_id,
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        "total_duration_sec": total_sec,
        "total_duration_str": duration_str,
        "cue_count": len(cues),
        "cues": cues
    }


