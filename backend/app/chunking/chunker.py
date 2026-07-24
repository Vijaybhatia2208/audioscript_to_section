from typing import List, Dict, Any
from app.parser.srt_parser import seconds_to_timestamp


def create_subtitle_chunks(
    cues: List[Dict[str, Any]],
    target_duration_sec: float = 45.0,
    overlap_duration_sec: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Groups subtitle cues into semantic time-window chunks.
    Each chunk tracks the combined text, start/end timestamps, and source metadata.
    """
    if not cues:
        return []

    chunks = []
    total_cues = len(cues)
    i = 0

    while i < total_cues:
        current_chunk_cues = []
        chunk_start_sec = cues[i]["start_sec"]
        chunk_end_sec = chunk_start_sec

        j = i
        while j < total_cues:
            cue = cues[j]
            current_chunk_cues.append(cue)
            chunk_end_sec = cue["end_sec"]
            
            # Check if chunk window has reached target duration
            if (chunk_end_sec - chunk_start_sec) >= target_duration_sec:
                break
            j += 1

        combined_text = " ".join(c["text"] for c in current_chunk_cues)
        first_cue = current_chunk_cues[0]

        chunk_data = {
            "text": combined_text,
            "start_sec": chunk_start_sec,
            "end_sec": chunk_end_sec,
            "start_time_str": seconds_to_timestamp(chunk_start_sec),
            "end_time_str": seconds_to_timestamp(chunk_end_sec),
            "timestamp_range": f"{seconds_to_timestamp(chunk_start_sec)} - {seconds_to_timestamp(chunk_end_sec)}",
            "module_name": first_cue["module_name"],
            "lesson_name": first_cue["lesson_name"],
            "source_file": first_cue["source_file"],
            "cue_count": len(current_chunk_cues)
        }

        chunks.append(chunk_data)

        # Advance pointer with overlap consideration
        if j >= total_cues - 1:
            break

        # Find next starting cue based on overlap_duration_sec
        next_i = i + 1
        overlap_target_sec = chunk_end_sec - overlap_duration_sec
        while next_i < j and cues[next_i]["start_sec"] < overlap_target_sec:
            next_i += 1
            
        i = max(i + 1, next_i)

    return chunks
