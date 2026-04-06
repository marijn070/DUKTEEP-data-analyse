import marimo

__generated_with = "0.22.4"
app = marimo.App(
    width="medium",
    layout_file="layouts/data_analyse.slides.json",
)


@app.cell
def _():
    import pandas as pd
    from pathlib import Path

    import base64

    return Path, base64, pd


@app.cell
def _(Path, pd):
    dir_path = Path("data")

    newest_file = max(dir_path.iterdir(), key=lambda f: f.stat().st_mtime)

    df = pd.read_parquet(newest_file)

    print(df.columns)

    def fill_small_gaps(group):
        group = group.sort_values("timestamp").reset_index(drop=True)

        new_rows = []

        for i in range(1, len(group)):
            prev = group.loc[i - 1]
            curr = group.loc[i]

            if curr["timestamp"] - prev["timestamp"] == 2:
                new_row = prev.copy()
                new_row["timestamp"] = prev["timestamp"] + 1
                new_rows.append(new_row)

        if new_rows:
            group = pd.concat([group, pd.DataFrame(new_rows)], ignore_index=True)

        return group

    groups = []

    for (_, _), group in df.groupby(["video", "person_name"]):
        groups.append(fill_small_gaps(group))

    df_filled = pd.concat(groups, ignore_index=True)

    df_filled
    return (df_filled,)


@app.cell(hide_code=True)
def _():
    import altair as alt

    alt.renderers.enable("default")
    return (alt,)


@app.cell(hide_code=True)
def _(df_filled):
    total_seconds = (
        df_filled.groupby("person_name")["timestamp"].count().reset_index(name="total_seconds")
    )

    total_videos = (
        df_filled.groupby("person_name")["video"].nunique().reset_index(name="total_videos")
    )
    return total_seconds, total_videos


@app.cell(hide_code=True)
def _(df_filled):
    daily_counts = (
        df_filled.groupby(["person_name", "date"])
        .size()  # number of rows = frames
        .reset_index(name="frames")
        .sort_values(["person_name", "date"])
    )

    unique_videos = df_filled[["person_name", "video", "date"]].drop_duplicates()

    daily_video_counts = (
        unique_videos.groupby(["person_name", "date"])
        .size()  # number of rows = frames
        .reset_index(name="new_videos")
        .sort_values(["person_name", "date"])
    )

    daily_total_video_counts = (
        df_filled[["video", "date"]]
        .drop_duplicates()
        .groupby("date")
        .size()
        .reset_index(name="new_videos")
        .sort_values("date")
    )

    # Compute cumulative sum **per person**
    daily_counts["cumulative_frames"] = daily_counts.groupby("person_name")["frames"].cumsum()

    daily_video_counts["cumulative_videos"] = daily_video_counts.groupby("person_name")[
        "new_videos"
    ].cumsum()

    daily_total_video_counts["cumulative_videos"] = daily_video_counts["new_videos"].cumsum()
    return daily_counts, daily_video_counts


@app.cell(hide_code=True)
def _(
    Path,
    alt,
    base64,
    daily_counts,
    daily_video_counts,
    pd,
    total_seconds,
    total_videos,
):
    # Set widths/heights
    width_bar = 1000
    height_bar = 400
    width_line = 1000
    height_line = 500

    # -----------------------
    # 1️⃣ Total Seconds Bar Chart
    # -----------------------
    bars_seconds = (
        alt.Chart(total_seconds)
        .mark_bar()
        .encode(
            x=alt.X("person_name:N", title="person_name"),
            y=alt.Y("total_seconds:Q", title="Aantal Seconden"),
            color="person_name:N",
        )
        .properties(width=width_bar, height=height_bar, title="Aantal Seconden in Beeld")
    )

    labels_seconds = bars_seconds.mark_text(
        dy=-5,  # shift text above bars
        align="center",
        color="black",
    ).encode(text=alt.Text("total_seconds", format=".1f"))

    chart_total_seconds = bars_seconds + labels_seconds

    # -----------------------
    # 2️⃣ Total Videos Bar Chart
    # -----------------------
    bars_videos = (
        alt.Chart(total_videos)
        .mark_bar()
        .encode(
            x=alt.X("person_name:N", title="person_name"),
            y=alt.Y("total_videos:Q", title="Antal Videos"),
            color="person_name:N",
        )
        .properties(width=width_bar, height=height_bar, title="Aantal videos verschenen")
    )

    labels_videos = bars_videos.mark_text(dy=-5, align="center", color="black").encode(
        text="total_videos:Q"
    )

    chart_total_videos = bars_videos + labels_videos

    # -----------------------
    # 3️⃣ Running Total of Frames Line Chart
    # -----------------------
    chart_running_total_seconds = (
        alt.Chart(daily_counts)
        .mark_line(interpolate="step-after", point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("cumulative_frames:Q", title="Aantal Secondes"),
            color="person_name:N",
            tooltip=["person_name", "date", "cumulative_frames"],
        )
        .properties(
            width=width_line, height=height_line, title="Running Total of Frames per person_name"
        )
    )

    # -----------------------
    # 4️⃣ Running Total of Videos Line Chart
    # -----------------------
    chart_running_total_videos = (
        alt.Chart(daily_video_counts)
        .mark_line(interpolate="step-after", point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("cumulative_videos:Q", title="Aantal Videos"),
            color="person_name:N",
            tooltip=["person_name", "date", "cumulative_videos"],
        )
        .properties(
            width=width_line, height=height_line, title="Running Total of Videos per person_name"
        )
    )


    # Path to your folder of known faces
    faces_folder = Path("known_faces")

    # Build a dataframe with person_name names and image data
    avatars_list = []

    for img_path in faces_folder.iterdir():
        if img_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            # Assuming file name is the person_name name: "Alice.png" -> "Alice"
            person_name_name = img_path.stem
            # Read image and encode as base64
            with open(img_path, "rb") as file:
                img_bytes = file.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                img_data = f"data:image/{img_path.suffix[1:]};base64,{img_b64}"
                avatars_list.append({"person_name": person_name_name, "img_url": img_data})

    avatars_df = pd.DataFrame(avatars_list)
    avatars_df

    avatars = (
        alt.Chart(avatars_df)
        .mark_image(width=150, height=150)
        .encode(
            x="person_name:N",
            y=alt.value(-80),  # slightly below x-axis
            url="img_url:N",
        )
    )

    chart_total_seconds = chart_total_seconds + avatars
    chart_total_videos = chart_total_videos + avatars
    return (
        chart_running_total_seconds,
        chart_running_total_videos,
        chart_total_seconds,
        chart_total_videos,
    )


@app.cell
def _(
    alt,
    chart_running_total_seconds,
    chart_running_total_videos,
    chart_total_seconds,
    chart_total_videos,
):
    dashboard_seconds = alt.vconcat(chart_total_seconds, chart_running_total_seconds)
    dashboard_videos = alt.vconcat(chart_total_videos, chart_running_total_videos)
    return


@app.cell
def _(chart_total_videos):
    chart_total_videos
    return


@app.cell
def _(chart_running_total_videos):
    chart_running_total_videos
    return


@app.cell
def _(chart_total_seconds):
    chart_total_seconds
    return


@app.cell
def _(chart_running_total_seconds):
    chart_running_total_seconds
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
