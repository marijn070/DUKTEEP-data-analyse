import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Youtube filmpjes Downloaden

    Er bestaat dus blijkbaar een tool `yt-dlp`, die kan helpen om dingen van youtube af te downloaden.
    Dus die gaan we lekker gebruiken.

    Ik heb hem geinstalleerd met
    ```bash
    uv tool install yt-dlp
    ```
    """)
    return


@app.cell
def _():
    import subprocess

    def download_channel(url):
        subprocess.run([
            "yt-dlp",
            "-f", "best[height<=480]/best",
            "--download-archive", "downloaded.txt",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "nl-orig",
            "--sub-format", "srt",
            "-o", "videos/%(upload_date)s - %(title)s.%(ext)s",
            url
        ])

    return (download_channel,)


@app.cell
def _(download_channel):
    DUKTEEP_LINK: str = "https://www.youtube.com/@dukteep"

    download_channel(DUKTEEP_LINK)

    return


if __name__ == "__main__":
    app.run()
