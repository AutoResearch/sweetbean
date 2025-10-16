def timeline_from_csv(path, columns):
    import pandas as pd

    df = pd.read_csv(path)
    if columns:
        df = df[columns]
    timeline = df.to_dict(orient="records")
    return timeline
