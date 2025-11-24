# ml_utils.py
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def get_clusters(df):
    """
    Returns (clusters, km_model, error_message)
    clusters is an array aligned with df index when successful.
    """
    try:
        if df.shape[0] < 3:
            return None, None, "Not enough data to form clusters (need at least 3 logs)."
        X = df[["sleep_hours", "study_hours", "productivity_score"]].fillna(0).values
        k = min(4, max(2, df.shape[0] // 3))  # dynamic but small k
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        # Map cluster numbers into simple categories based on cluster centers
        centers = km.cluster_centers_
        # define descriptors using a heuristic: high study and high score => high-focus
        descriptors = {}
        for i, c in enumerate(centers):
            sleep_c, study_c, score_c = c[0], c[1], c[2]
            if study_c >= 6 and score_c >= 6:
                descriptors[i] = "high-focus"
            elif score_c < 4 and study_c < 3:
                descriptors[i] = "low-energy"
            elif score_c < 5 and study_c >= 3:
                descriptors[i] = "burnout-risk"
            else:
                descriptors[i] = "balanced"
        # Convert numeric labels to string labels
        str_labels = [descriptors[int(l)] for l in labels]
        return str_labels, km, None
    except Exception as e:
        return None, None, f"Clustering error: {e}"

def train_regression(df):
    """
    Trains a simple LinearRegression to predict study_hours and productivity_score.
    Returns (models_dict, error_message). models_dict contains keys:
      - 'study_model' : model to predict study_hours from sleep_hours and previous study
      - 'productivity_model' : model to predict productivity_score
    """
    try:
        if df.shape[0] < 2:
            return None, "Not enough data for regression (need at least 2 logs)."
        # Features: sleep_hours, study_hours (lag), water_intake can be added
        X = df[["sleep_hours", "study_hours", "water_intake"]].fillna(0).values
        y_study = df["study_hours"].fillna(0).values
        y_score = df["productivity_score"].fillna(0).values

        study_model = LinearRegression()
        study_model.fit(X, y_study)

        score_model = LinearRegression()
        score_model.fit(X, y_score)

        return {"study_model": study_model, "score_model": score_model}, None
    except Exception as e:
        return None, f"Regression training error: {e}"

def predict_next(models, sleep_hours: float, study_hours: float=0.0, water_intake: float=None):
    """
    Predict next-day study_hours and productivity_score using provided models dict.
    """
    try:
        if models is None:
            return None, None
        feat = np.array([[sleep_hours, study_hours, 0 if water_intake is None else water_intake]])
        study_pred = models["study_model"].predict(feat)[0]
        score_pred = models["score_model"].predict(feat)[0]
        return round(float(study_pred), 2), round(float(score_pred), 2)
    except Exception:
        return None, None
