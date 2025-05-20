import subprocess, sys, json, re
from pathlib import Path

def get_video_info(url):
    r = subprocess.run(["yt-dlp", "--print-json", "--skip-download", url], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip().startswith("{")]
    if not lines: print("❌ No metadata found."); sys.exit(1)
    info = json.loads(lines[0])
    return info["title"], info["uploader"], info["webpage_url"], info.get("subtitles", {}), info.get("automatic_captions", {})

def download_subs(url, lang, auto):
    print(f"📥 Downloading {'auto-' if auto else ''}subtitles: {lang}...")
    subprocess.run(["yt-dlp", "--sub-lang", lang, "--write-auto-sub" if auto else "--write-sub", "--skip-download", "--output", "video", url], check=True)

def clean_timing_tags(text):
    text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", text)
    text = re.sub(r"</?c>", "", text)
    return text

def vtt_to_md(vtt: Path, md: Path, author: str, link: str, lang: str):
    with vtt.open(encoding="utf-8") as f: raw = f.read()
    cleaned = clean_timing_tags(raw)
    lines = [l.strip() for l in cleaned.splitlines() if "-->" not in l and not l.startswith("WEBVTT") and l.strip()]
    content = " ".join(lines)
    md.write_text(f"# Language: {lang}\n**Author:** {author}\n**Link:** {link}\n\n{content}", encoding="utf-8")
    print(f"✅ Markdown saved to {md.resolve()}")
    vtt.unlink()

def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube_subtitles_to_md.py <YouTube_URL> [language_code]"); sys.exit(1)
    url = sys.argv[1]; lang_arg = sys.argv[2].lower() if len(sys.argv) > 2 else None
    title, uploader, link, subs, auto = get_video_info(url)
    opts = [(l, False) for l in subs] + [(l, True) for l in auto]
    if not opts: print("❌ No subtitles."); sys.exit(1)
    if lang_arg:
        match = [o for o in opts if o[0] == lang_arg]
        if not match: print(f"❌ '{lang_arg}' not found."); sys.exit(1)
        lang, is_auto = sorted(match, key=lambda x: x[1])[0]
    else:
        print("\nAvailable subtitle languages:")
        for l, a in sorted(set(opts)): print(f"- {l} ({'auto' if a else 'manual'})")
        code = input("\nEnter language code: ").strip().lower()
        match = [o for o in opts if o[0] == code]
        if not match: print(f"❌ '{code}' not found."); sys.exit(1)
        lang, is_auto = sorted(match, key=lambda x: x[1])[0]
    download_subs(url, lang, is_auto)
    files = list(Path(".").glob(f"*.{lang}.vtt")) + list(Path(".").glob(f"*.{lang}.auto.vtt"))
    if not files: print("❌ Subtitle file not found."); sys.exit(1)
    safe_name = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
    vtt_to_md(files[0], Path(f"{safe_name}.md"), uploader, link, lang)

if __name__ == "__main__": main()
