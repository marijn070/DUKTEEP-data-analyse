import subprocess


def download_channel(url, output_dir):
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
            f"{output_dir}/%(upload_date)s__%(title)s.%(ext)s",
            url,
        ]
    )
