import re
from pathlib import Path
from typing import List, Dict, Any
from app.parser.srt_parser import timestamp_to_seconds, seconds_to_timestamp, extract_metadata_from_path


def parse_vtt(file_path: str) -> List[Dict[str, Any]]:
    """
    Parses a WebVTT file into a list of cue dictionaries.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"VTT file not found: {file_path}")

    content = path.read_text(encoding="utf-8", errors="ignore")
    metadata = extract_metadata_from_path(file_path)
    
    # Remove WEBVTT header and metadata comments
    lines = content.splitlines()
    clean_lines = []
    in_header = True
    
    for line in lines:
        if in_header:
            if line.startswith("WEBVTT") or line.startswith("NOTE") or not line.strip():
                continue
            else:
                in_header = False
        clean_lines.append(line)
        
    clean_content = "\n".join(clean_lines)
    
    pattern = re.compile(
        r'(?:(\d+)\s*\n)?'
        r'(\d{2}:\d{2}:\d{2}[,\.]\d{3}|\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3}|\d{2}:\d{2}[,\.]\d{3})[^\n]*\n'
        r'((?:(?!\d{2}:).)+)',
        re.DOTALL
    )
    
    cues = []
    matches = pattern.findall(clean_content)
    
    for idx, match in enumerate(matches, start=1):
        cue_idx = int(match[0]) if match[0] else idx
        start_ts = match[1].strip()
        end_ts = match[2].strip()
        text = " ".join(line.strip() for line in match[3].strip().splitlines() if line.strip())
        
        if not text:
            continue

        # Strip html tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        start_sec = timestamp_to_seconds(start_ts)
        end_sec = timestamp_to_seconds(end_ts)
        
        cues.append({
            "index": cue_idx,
            "start_time_str": seconds_to_timestamp(start_sec),
            "end_time_str": seconds_to_timestamp(end_sec),
            "start_sec": start_sec,
            "end_sec": end_sec,
            "text": text,
            "module_name": metadata["module_name"],
            "lesson_name": metadata["lesson_name"],
            "source_file": metadata["file_name"]
        })
        
    return cues
