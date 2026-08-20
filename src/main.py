import argparse
import subprocess
from pathlib import Path

import yt_dlp
from yt_dlp.postprocessor.metadataparser import MetadataFromFieldPP
from embed_thumbnail import merge_thumbnails_with_audio_files

DOWNLOAD_FOLDER = "downloads/WTWTLW"
DEFAULT_URL = "https://youtu.be/SGLi-LMQHI4?is=lppM79UQKbnfObc4"

ydl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'embedthumbnail': True,
    'writethumbnail': True,
    'addmetadata': True,
    # YouTube audio-only uploads carry no artist/album — map uploader -> artist
    'postprocessors': [
        {
            'key': 'MetadataParser',
            'actions': [MetadataFromFieldPP.to_action('%(uploader)s:%(artist)s')],
            'when': 'pre_process',
        },
        {'key': 'FFmpegMetadata'},  # write title/artist/album tags into the file
    ],
}


def convert_to_mp3(folder):
    """Transcode every m4a in the folder to a 192k MP3, keeping tags + cover."""
    for audio in Path(folder).rglob("*.m4a"):
        mp3 = audio.with_suffix(".mp3")
        cmd = [
            "ffmpeg", "-y", "-v", "quiet",
            "-i", str(audio), "-map", "0",
            "-c:a", "libmp3lame", "-b:a", "192k",
            "-c:v", "mjpeg", "-id3v2_version", "3",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
            str(mp3),
        ]
        r = subprocess.run(cmd)
        print(f"{'✓' if r.returncode == 0 else '✗'} MP3: {mp3.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Media Manager: download a link as tagged audio")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL,
                        help="YouTube URL to download")
    parser.add_argument("--mp3", action="store_true",
                        help="also transcode the result to MP3 (192 kbps, cover art)")
    args = parser.parse_args()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([args.url])
        if error_code:
            print(f"Download failed with code {error_code}")
            return error_code

    merge_thumbnails_with_audio_files(DOWNLOAD_FOLDER)

    if args.mp3:
        convert_to_mp3(DOWNLOAD_FOLDER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
