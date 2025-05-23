import subprocess, sys, json, importlib.util
from pathlib import Path

def ensure_module(module_name, install_cmd):
    if importlib.util.find_spec(module_name) is None:
        print(f"⚠️ Модуль '{module_name}' не найден. Устанавливаю...")
        subprocess.run([sys.executable, "-m", "pip"] + install_cmd, check=True)

def download_audio(url, out="input.mp3"):
    print("📥 Скачивание аудио...")
    subprocess.run([sys.executable, "-m", "yt_dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "-o", out, url], check=True)

def run_whisper(audio, lang="en"):
    print("🧠 Распознавание речи...")
    subprocess.run([sys.executable, "-m", "whisper", audio, "--language", lang, "--output_format", "txt", "--output_dir", "."], check=True)

def get_video_info(url):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--print-json", "--skip-download", url], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip().startswith("{")]
    if not lines:
        print("❌ Метаданные не найдены.")
        sys.exit(1)
    info = json.loads(lines[0])
    return info["title"], info["uploader"], info["webpage_url"]

def txt_to_md(txt: Path, md: Path, author: str, link: str, lang: str):
    content = txt.read_text(encoding="utf-8").strip()
    md.write_text(f"# Language: {lang}\n**Author:** {author}\n**Link:** {link}\n\n{content}", encoding="utf-8")
    print(f"✅ Markdown сохранён в {md.resolve()}")
    txt.unlink()

def main():
    ensure_module("yt_dlp", ["install", "-U", "yt-dlp"])
    ensure_module("whisper", ["install", "git+https://github.com/openai/whisper.git"])
    ensure_module("ffmpeg", ["install", "ffmpeg-python"])

    if len(sys.argv) < 2:
        print("Использование: python youtube_transcribe_to_md.py <YouTube_URL>")
        sys.exit(1)

    url = sys.argv[1]
    audio = Path("input.mp3")

    title, author, link = get_video_info(url)
    safe_name = "".join(c for c in title if c.isalnum() or c in " -_").rstrip()
    txt_file = Path(f"{safe_name}.txt")
    md_file = Path(f"{safe_name}.md")

    download_audio(url, str(audio))
    run_whisper(str(audio))
    txt_to_md(txt_file, md_file, author, link, "en")

    audio.unlink(missing_ok=True)

if __name__ == "__main__":
    main()