import yt_dlp
from embed_thumbnail import merge_thumbnails_with_audio_files

DOWNLOAD_FOLDER = "downloads/WTWTLW"
URLS = ['https://www.youtube.com/watch?v=1mH2r6Zct0s&list=PLeivzRdz7xcm2NargAnk6PJ3G5Ten4RYU']


ydl_opts = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'embedthumbnail': True,
    'writethumbnail': True,
    'addmetadata': True,
}


def main():
    """Main entry point for the ultimate media manager."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(URLS)

    merge_thumbnails_with_audio_files(DOWNLOAD_FOLDER)


if __name__ == "__main__":
    main()
