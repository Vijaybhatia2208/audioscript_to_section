srt , vtt -> are the subtitle captions format files

SRT (SubRip Subtitle)

Example

```
1
00:00:01,500 --> 00:00:04,000
Welcome to the course.

2
00:00:04,500 --> 00:00:08,000
Today we'll learn about Retrieval Augmented Generation.
```

Structure:

Subtitle number
Start time → End time
Subtitle text

Notice that SRT uses:

, (comma) for milliseconds
Example: 00:00:04,500

2. VTT (WebVTT)

Full form: Web Video Text Tracks

It was developed for HTML5 video and is commonly used on the web.

Example:

WEBVTT

00:00:01.500 --> 00:00:04.000
Welcome to the course.

00:00:04.500 --> 00:00:08.000
Today we'll learn about Retrieval Augmented Generation.

Differences from SRT:

Starts with a WEBVTT header.
Uses . (period) instead of , for milliseconds.
Supports additional features like styling, positioning, speaker names, and metadata.
