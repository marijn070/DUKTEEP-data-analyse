import subprocess


def download_channel(url):
    subprocess.run(
        [
            "yt-dlp",
            "-f",
            "best[height<=480]/best",
            "--download-archive",
            "downloaded.txt",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "nl-orig",
            "--sub-format",
            "srt",
            "-o",
            "videos/%(upload_date)s - %(title)s.%(ext)s",
            url,
        ]
    )
