import sys
import json
from app.parser.yt_parser import get_youtube_video_info


def main():
    default_url = "https://www.youtube.com/watch?v=bMknfKXIFA8"  # React in 100 seconds
    url = sys.argv[1] if len(sys.argv) > 1 else default_url

    print("=== YouTube Video Information & Transcript Fetcher ===")
    print(f"Target URL: {url}\n")

    info = get_youtube_video_info(url)

    print("--- Video Metadata ---")
    print(f"Video ID: {info['video_id']}")
    print(f"YouTube URL: {info['youtube_url']}")
    print(f"Embed URL: {info['embed_url']}")
    print(f"Thumbnail URL: {info['thumbnail_url']}")
    print(f"Total Duration: {info['total_duration_str']} ({info['total_duration_sec']} seconds)")
    print(f"Total Cue Count: {info['cue_count']}")

    print("\n--- Sample First 3 Transcript Cues ---")
    print(json.dumps(info['cues'][:3], indent=2))


if __name__ == "__main__":
    main()
