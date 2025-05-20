# YouTube to Markdown Transcript Tool (v8)

## Features
- Optional language code input for subtitle extraction
- Output Markdown file uses YouTube video title
- Metadata at top: language, author, and video link
- Transcript content is plain continuous text without any timing markers or segments

## Usage

### Subtitle-based:
```bash
python youtube_subtitles_to_md.py <YouTube_URL> [language_code]
```

### Whisper-based transcription:
```bash
python youtube_transcribe_to_md.py <YouTube_URL>
```

Markdown file will be saved with the name of the video and `.md` extension.
