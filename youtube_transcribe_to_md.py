import subprocess, sys, json
from pathlib import Path

def download_audio(url, out="input.mp3"):
    print("📥 Downloading audio..."); subprocess.run(["yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "-o", out, url], check=True)

def run_whisper(audio, lang="en"):
    print("🧠 Transcribing..."); subprocess.run(["whisper", audio, "--language", lang, "--output_format", "txt", "--output_dir", "."], check=True)

def get_video_info(url):
    r = subprocess.run(["yt-dlp", "--print-json", "--skip-download", url], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip().startswith("{")]
    if not lines: print("❌ No metadata found."); sys.exit(1)
    info = json.loads(lines[0])
    return info["title"], info["uploader"], info["webpage_url"]

def txt_to_md(txt: Path, md: Path, author: str, link: str, lang: str):
    content = txt.read_text(encoding="utf-8").strip()
    md.write_text(f"# Language: {lang}\n**Author:** {author}\n**Link:** {link}\n\n{content}", encoding="utf-8")
    print(f"✅ Markdown saved to {md.resolve()}")
    txt.unlink()

def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcribe_to_md.py <YouTube_URL>"); sys.exit(1)
    url = sys.argv[1]; audio = Path("input.mp3")
    title, author, link = get_video_info(url)
    safe_name = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
    txt_file = Path(f"{safe_name}.txt"); md_file = Path(f"{safe_name}.md")
    download_audio(url, str(audio)); run_whisper(str(audio)); txt_to_md(txt_file, md_file, author, link, "en")
    audio.unlink(missing_ok=True)

if __name__ == "__main__": main()
