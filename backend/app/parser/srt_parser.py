import re
from pathlib import Path
from typing import List, Dict, Any


def timestamp_to_seconds(ts_str: str) -> float:
    """
    Converts timestamp string (HH:MM:SS,mmm or HH:MM:SS.mmm) to total seconds.
    """
    ts_str = ts_str.replace(',', '.')
    parts = ts_str.split(':')
    if len(parts) == 3:
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes = float(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    return 0.0


def seconds_to_timestamp(seconds: float) -> str:
    """
    Converts seconds float to formatted HH:MM:SS string.
    """
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def extract_metadata_from_path(file_path: str) -> Dict[str, str]:
    """
    Extracts module_name and lesson_name from the file path structure.
    Example: .../class-subtitle/module 1/01_what-is-mobile-development_epm/file.srt
    """
    path = Path(file_path)
    parts = path.parts
    
    module_name = "Unknown Module"
    lesson_name = path.stem
    
    for i, part in enumerate(parts):
        if part.lower().startswith("module"):
            module_name = part
            if i + 1 < len(parts) - 1:
                lesson_name = parts[i + 1]
            break

    return {
        "module_name": module_name,
        "lesson_name": lesson_name,
        "file_name": path.name,
        "source_path": str(path)
    }


def parse_srt(file_path: str) -> List[Dict[str, Any]]:
    """
    Parses an SRT file into a list of cue dictionaries.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"SRT file not found: {file_path}")

    content = path.read_text(encoding="utf-8", errors="ignore")
    metadata = extract_metadata_from_path(file_path)
    
    # Pattern to match SRT blocks: index, timestamp line, text block
    pattern = re.compile(
        r'(\d+)\s*\n'
        r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n'
        r'((?:(?!\d+\s*\n\d{2}:\d{2}:\d{2}).)+)',
        re.DOTALL
    )
    
    cues = []
    matches = pattern.findall(content)
    
    for match in matches:
        cue_index = int(match[0])
        start_ts = match[1].strip()
        end_ts = match[2].strip()
        text = " ".join(line.strip() for line in match[3].strip().splitlines() if line.strip())
        
        if not text:
            continue
            
        start_sec = timestamp_to_seconds(start_ts)
        end_sec = timestamp_to_seconds(end_ts)
        
        cues.append({
            "index": cue_index,
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
