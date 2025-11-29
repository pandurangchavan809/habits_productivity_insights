import pandas as pd
import numpy as np
from datetime import datetime
from database import fetch_logs
from typing import Tuple

def compute_productivity_score(row):

    # normalize study_hours to 0-10 scale (assume 0-12 hours)
    study = min(row.get("study_hours", 0), 12) / 12 * 10
    # normalize sleep: ideal ~7-8 hrs
    sleep = row.get("sleep_hours", 0)
    sleep_score = max(0, 10 - abs(7.5 - sleep) * 1.5)  # small penalty for deviating from 7.5h
    # mood bonus
    mood = row.get("mood", "")
    mood_score = 1.0 if mood and mood.lower() in ("good", "great", "happy", "energized") else 0.0
    # simple weighted sum
    score = 0.6 * study + 0.35 * sleep_score + 2.0 * mood_score
    return round(score, 2)

def get_dataframe():
    rows = fetch_logs()
    if not rows:
        return pd.DataFrame()
    cols = ["id", "date", "sleep_hours", "study_hours", "activities", "mood",
            "notes", "mode", "timestamp", "water_intake", "steps", "screen_time_minutes", "productivity_score"]
    df = pd.DataFrame(rows, columns=cols)
    df["date"] = pd.to_datetime(df["date"])

    # ensure numeric types where possible
    df["sleep_hours"] = pd.to_numeric(df["sleep_hours"], errors="coerce").fillna(0.0)
    df["study_hours"] = pd.to_numeric(df["study_hours"], errors="coerce").fillna(0.0)
    df["water_intake"] = pd.to_numeric(df["water_intake"], errors="coerce")
    df["steps"] = pd.to_numeric(df["steps"], errors="coerce")
    df["screen_time_minutes"] = pd.to_numeric(df["screen_time_minutes"], errors="coerce")

    # fill productivity_score if missing
    df["productivity_score"] = pd.to_numeric(df["productivity_score"], errors="coerce")
    missing_score = df["productivity_score"].isna()
    if missing_score.any():
        df.loc[missing_score, "productivity_score"] = df[missing_score].apply(compute_productivity_score, axis=1)
    return df

def weekly_summary(df):
    if df.empty:
        return pd.DataFrame()
    df2 = df.set_index("date").resample("W").agg({
        "sleep_hours": "mean",
        "study_hours": "sum",
        "productivity_score": "mean"
    }).round(2)
    return df2

def monthly_summary(df):
    if df.empty:
        return pd.DataFrame()
    df2 = df.set_index("date").resample("M").agg({
        "sleep_hours": "mean",
        "study_hours": "sum",
        "productivity_score": "mean"
    }).round(2)
    return df2

def activity_heatmap_data(df):
    # produce counts of activities per weekday
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["weekday"] = df["date"].dt.day_name()

    # split activities by separators and count occurrences per weekday
    rows = []
    for _, r in df.iterrows():
        acts = str(r.get("activities", "")).replace(";", ",").split(",")
        for a in acts:
            a_clean = a.strip().lower()
            if a_clean:
                rows.append({"weekday": r["weekday"], "activity": a_clean})
    hf = pd.DataFrame(rows)
    if hf.empty:
        return pd.DataFrame()
    pivot = hf.pivot_table(index="activity", columns="weekday", aggfunc=len, fill_value=0)
    
    # reorder weekdays
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    cols = [c for c in weekday_order if c in pivot.columns]
    pivot = pivot[cols]
    return pivot
