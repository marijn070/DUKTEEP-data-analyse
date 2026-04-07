import marimo

__generated_with = "0.22.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    from pathlib import Path
    import marimo as mo
    import altair as alt

    import base64

    return Path, alt, mo, pd


@app.cell(hide_code=True)
def _():
    import os
    import sqlalchemy

    _password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    DATABASE_URL = f"postgresql://postgres:{_password}@localhost:5555/dukteep"
    engine = sqlalchemy.create_engine(DATABASE_URL)
    return (engine,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DUKTEEP Data Analyse

    ## De data
    """)
    return


@app.cell(hide_code=True)
def _(engine, mo):
    _df = mo.sql(
        f"""
        SELECT
            img_name
        from
            embeddings_facenet_opencv_aligned_raw;
        """,
        engine=engine
    )
    return


@app.cell(hide_code=True)
def _(Path, pd):
    dir_path = Path("data")
    newest_file = max(dir_path.iterdir(), key=lambda f: f.stat().st_mtime)

    df = pd.read_parquet("data/old_dbs.parquet")
    # df = pd.read_parquet(newest_file, engine="pyarrow")

    df
    return (df,)


@app.cell(hide_code=True)
def _(df, mo):
    mo.md(f"""
    We hebben nu de dataset van {len(df)} frames van de gezichten van dukteepers.
    Even kijken hoe we die leuk kunnen visualiseren
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Grafieken - Detecties
    """)
    return


@app.cell(hide_code=True)
def _(df, mo):
    counts = df[['person_name','video']].drop_duplicates().groupby('person_name').size();
    totals = df[['person_name','video']].groupby('person_name').size();

    mo.md(f"""
    ## Wie komt er in de meeste filmpjes voor?
    """)
    return (totals,)


@app.cell(hide_code=True)
def _(alt, df):
    _chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(field='person_name', type='nominal', title='Dukteeper'),
            y=alt.Y(field='video', type='quantitative', title='Aantal Videos', aggregate='distinct'),
            color=alt.Color(field='person_name', type='nominal'),
            tooltip=[
                alt.Tooltip(field='person_name', title='Dukteeper'),
                alt.Tooltip(field='video', aggregate='distinct', title='Aantal Videos'),
                alt.Tooltip(field='person_name')
            ]
        )
        .properties(
            title='Wie heeft er het meeste Videos?',
            height=500,
            width='container',
            config={
                'axis': {
                    'grid': True
                }
            }
        )
    )
    _chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Aandeel aantal filmpjes per maand
    """)
    return


@app.cell(hide_code=True)
def _(alt, df):
    # replace _df with your data source
    _chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=30, outerRadius=100)
        .encode(
            color=alt.Color(field='person_name', type='nominal'),
            theta=alt.Theta(field='video', type='nominal', aggregate='distinct'),
            row=alt.Row(field='date', timeUnit='yearmonth', type='temporal', bin={
                'maxbins': 6
            }),
            tooltip=[
                alt.Tooltip(field='video', aggregate='distinct'),
                alt.Tooltip(field='person_name')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )
    _chart
    return


@app.cell(hide_code=True)
def _(mo, totals):
    mo.md(rf"""
    ## Wie is er het vaakst gedetecteerd?

    Mees komt wel in veel filmpjes voor, maar is veruit het minste door de gezichtsherkenning software herkend. Angela is wel {totals["angela"]} keer gedetecteerd en mees maar {totals["mees"]} keer gedetecteerd.

    Ik denk doordat
    """)
    return


@app.cell(hide_code=True)
def _(alt, df):
    # replace _df with your data source
    _chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(field='person_name', type='nominal', title='Dukteeper'),
            y=alt.Y(field='video', type='nominal', title='Aantal Frames', aggregate='count'),
            color=alt.Color(field='person_name', type='nominal'),
            tooltip=[
                alt.Tooltip(field='person_name', title='Dukteeper'),
                alt.Tooltip(field='video', aggregate='count', title='Aantal Frames'),
                alt.Tooltip(field='person_name')
            ]
        )
        .properties(
            title='Aantal frames Gedetecteerd',
            height=500,
            width='container',
            config={
                'axis': {
                    'grid': True
                }
            }
        )
    )
    _chart
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Ondertiteling

    We gaan srt files analyseren om te zien welke woorden er het vaakste worden gezegd
    """)
    return


@app.cell
def _():
    import srt
    import glob
    from wordcloud import WordCloud
    import nltk
    nltk.download("stopwords")

    from nltk.corpus import stopwords

    return WordCloud, glob, srt, stopwords


@app.cell
def _(glob, pd, srt):
    subtitles_files = glob.glob("videos/*.srt")

    video_subs = [srt.parse(open(file).read()) for file in subtitles_files]

    wc = {}

    for video in video_subs:
        for subtitle in video:
            for word in subtitle.content.split():
                word = word.lower().strip(',.!?";()[]"')
                wc[word] = wc.get(word, 0) + 1


    wc_df = pd.DataFrame(list(wc.items()), columns=["word", "count"])


    return (wc,)


@app.cell(hide_code=True)
def _(mo, wc):
    mo.md(f"""
    ## Hoevaak zeggen we wat?

    Er wordt vanalles gezegd in onze videos. We reviewen vette tech, en er is dan ook in totaal {wc["vet"]} keer vet gezegd en {wc["tech"]} keer tech gezegd.

    We hebben het ook over elkaar; {wc["angela"]} keer angela gezegd en {wc["mees"]} keer mees gezegd, {wc["koen"]} keer koen gezegd en {wc["marijn"]} keer marijn gezegd.

    Fiets zeggen we *{wc["fiets"]}* keer, en dat is best veel. We hebben het ook wel eens over eten, want eten zeggen we {wc["eten"]} keer. En drinken zeggen we {wc["drinken"]} keer.

    ### Schelden we veel?

    - shit: {wc.get("shit", 0)} keer
    - kut: {wc.get("kut", 0)} keer
    - fuck: {wc.get("fuck", 0)} keer
    - oeps: {wc.get("oeps", 0)} keer

    Robot zeggen we {wc["robot"]} keer en we hebben het {wc["clubhuis"]} keer over ons clubhuis.
    Bambitron wordt {wc["bambitron"]} keer genoemd, ouwe legend dat het is.

    **Software**
    - blender: {wc["blender"]}
    - computer: {wc["computer"]}
    - code: {wc["code"]}
    - cnc: {wc["cnc"]}
    - software: {wc["software"]}
    - fixen: {wc["fixen"]}
    - fix: {wc["fix"]}
    - mega: {wc["mega"]}
    """)
    return


@app.cell
def _(WordCloud, mo, stopwords, wc):
    dutch_stopwords = set(stopwords.words("dutch"))
    extra_words = {"we", "wel"}
    dutch_stopwords.update(extra_words)

    wordcloud = WordCloud(
        width = 1200,
        height = 600,
    )


    wordcloud.generate_from_frequencies({
        word: count
        for (word, count) in wc.items()
        if word not in dutch_stopwords
    })

    mo.image(wordcloud.to_array())
    return


if __name__ == "__main__":
    app.run()
