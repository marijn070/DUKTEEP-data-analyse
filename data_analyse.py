import marimo

__generated_with = "0.21.1"
app = marimo.App(
    width="medium",
    layout_file="layouts/data_analyse.slides.json",
)


@app.cell
def _():
    import pickle
    import pandas as pd

    return pd, pickle


@app.cell(hide_code=True)
def _(pickle):
    with open("dfs.pkl", mode="rb") as f:
        dfs = pickle.load(f)

    marijn, angela, koen, mees = dfs
    return angela, koen, marijn, mees


@app.cell(hide_code=True)
def _(angela, koen, marijn, mees, pd):
    def process_df(df, name: str):
        # get date from video name
        df[['date_str', 'rest']] = df['img_name'].str.split(' - ', expand = True)
        # convert to date
        df['date'] = pd.to_datetime(df['date_str'], format='%Y%m%d').dt.date
        df[['video', 'timestamp_str']] = df['rest'].str.split('_', expand = True)
        df['timestamp'] = (
            df['timestamp_str']
            .str.replace('s', '', regex=False)
            .astype(float)
        )
        df['dukteeper'] = name

        return df[['date', 'video', 'timestamp', 'dukteeper']]

    df = pd.concat([
        process_df(marijn, 'marijn'),
        process_df(koen, 'koen'),
        process_df(angela, 'angela'),
        process_df(mees, 'mees')
    ])
    return (df,)


@app.cell(hide_code=True)
def _(df, pd):
    def fill_small_gaps(group):
        group = group.sort_values('timestamp').reset_index(drop=True)

        new_rows = []

        for i in range(1, len(group)):
            prev = group.loc[i - 1]
            curr = group.loc[i]

            if curr['timestamp'] - prev['timestamp'] == 2:
                new_row = prev.copy()
                new_row['timestamp'] = prev['timestamp'] + 1
                new_rows.append(new_row)

        if new_rows:
            group = pd.concat([group, pd.DataFrame(new_rows)], ignore_index=True)

        return group

    groups = []

    for (_, _), group in df.groupby(['video', 'dukteeper']):
        groups.append(fill_small_gaps(group))

    df_filled = pd.concat(groups, ignore_index=True)
    return (df_filled,)


@app.cell(hide_code=True)
def _():
    import altair as alt

    alt.renderers.enable('default')
    return (alt,)


@app.cell(hide_code=True)
def _(df_filled):
    total_seconds = (
        df_filled
        .groupby('dukteeper')['timestamp']
        .count()
        .reset_index(name='total_seconds')
    )

    total_videos = (
        df_filled
        .groupby('dukteeper')['video']
        .nunique()
        .reset_index(name='total_videos')
    )
    return total_seconds, total_videos


@app.cell(hide_code=True)
def _(df_filled):
    daily_counts = (
        df_filled.groupby(['dukteeper', 'date'])
                 .size()  # number of rows = frames
                 .reset_index(name='frames')
                 .sort_values(['dukteeper', 'date'])
    )

    unique_videos = df_filled[['dukteeper', 'video', 'date']].drop_duplicates()

    daily_video_counts = (
        unique_videos.groupby(['dukteeper', 'date'])
                 .size()  # number of rows = frames
                 .reset_index(name='new_videos')
                 .sort_values(['dukteeper', 'date'])
    )

    daily_total_video_counts = (
        df_filled[['video', 'date']].drop_duplicates().groupby('date').size().reset_index(name='new_videos').sort_values('date')

    )

    # Compute cumulative sum **per person**
    daily_counts['cumulative_frames'] = daily_counts.groupby('dukteeper')['frames'].cumsum()


    daily_video_counts['cumulative_videos'] = daily_video_counts.groupby('dukteeper')['new_videos'].cumsum()

    daily_total_video_counts['cumulative_videos'] = daily_video_counts['new_videos'].cumsum()
    return daily_counts, daily_video_counts


@app.cell(hide_code=True)
def _(alt, daily_counts, daily_video_counts, pd, total_seconds, total_videos):
    # Set widths/heights
    width_bar = 1000
    height_bar = 400
    width_line = 1000
    height_line = 500

    # -----------------------
    # 1️⃣ Total Seconds Bar Chart
    # -----------------------
    bars_seconds = alt.Chart(total_seconds).mark_bar().encode(
        x=alt.X('dukteeper:N', title='Dukteeper'),
        y=alt.Y('total_seconds:Q', title='Aantal Seconden'),
        color='dukteeper:N'
    ).properties(width=width_bar, height=height_bar, title='Aantal Seconden in Beeld')

    labels_seconds = bars_seconds.mark_text(
        dy=-5,  # shift text above bars
        align='center',
        color='black'
    ).encode(
        text=alt.Text('total_seconds', format='.1f')
 
    )

    chart_total_seconds = bars_seconds + labels_seconds

    # -----------------------
    # 2️⃣ Total Videos Bar Chart
    # -----------------------
    bars_videos = alt.Chart(total_videos).mark_bar().encode(
        x=alt.X('dukteeper:N', title='Dukteeper'),
        y=alt.Y('total_videos:Q', title='Antal Videos'),
        color='dukteeper:N'
    ).properties(width=width_bar, height=height_bar, title='Aantal videos verschenen')

    labels_videos = bars_videos.mark_text(
        dy=-5,
        align='center',
        color='black'
    ).encode(
        text='total_videos:Q'
    )

    chart_total_videos = bars_videos + labels_videos

    # -----------------------
    # 3️⃣ Running Total of Frames Line Chart
    # -----------------------
    chart_running_total_seconds = alt.Chart(daily_counts).mark_line(interpolate='step-after', point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('cumulative_frames:Q', title='Aantal Secondes'),
        color='dukteeper:N',
        tooltip=['dukteeper', 'date', 'cumulative_frames']
    ).properties(
        width=width_line,
        height=height_line,
        title='Running Total of Frames per Dukteeper'
    )

    # -----------------------
    # 4️⃣ Running Total of Videos Line Chart
    # -----------------------
    chart_running_total_videos = alt.Chart(daily_video_counts).mark_line(interpolate='step-after', point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('cumulative_videos:Q', title='Aantal Videos'),
        color='dukteeper:N',
        tooltip=['dukteeper', 'date', 'cumulative_videos']
    ).properties(
        width=width_line,
        height=height_line,
        title='Running Total of Videos per Dukteeper'
    )


    import base64
    from pathlib import Path

    # Path to your folder of known faces
    faces_folder = Path('known_faces')

    # Build a dataframe with Dukteeper names and image data
    avatars_list = []

    for img_path in faces_folder.iterdir():
        if img_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            # Assuming file name is the Dukteeper name: "Alice.png" -> "Alice"
            dukteeper_name = img_path.stem
            # Read image and encode as base64
            with open(img_path, "rb") as file:
                img_bytes = file.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                img_data = f"data:image/{img_path.suffix[1:]};base64,{img_b64}"
                avatars_list.append({"dukteeper": dukteeper_name, "img_url": img_data})

    avatars_df = pd.DataFrame(avatars_list)
    avatars_df


    avatars = alt.Chart(avatars_df).mark_image(width=150, height=150).encode(
        x='dukteeper:N',
        y=alt.value(-80),  # slightly below x-axis
        url='img_url:N'
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


if __name__ == "__main__":
    app.run()
