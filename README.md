
# Smart Habit & Productivity Tracker

A professional Streamlit application to track daily habits, visualize progress, and get ML & AI-driven insights to improve productivity. This project helps users log sleep, study/work hours, activities and mood — then provides analytics, clustering, predictive models, and optional AI recommendations.

**Status:** Production-ready UI (Streamlit) with ML utilities and export features.

**Tech stack:** Python, Streamlit, Pandas, scikit-learn, Plotly, SQLite, ReportLab (PDF), Google Gemini (optional)

**Quick links:**
- **Run:** `streamlit run app.py`
- **Config:** `config.py`
- **Database:** `habits.db` (SQLite)

**Why this project?**
- Converts daily habit data into actionable insights.
- Combines simple, explainable ML (clustering + regression) with interactive visualizations.
- Optional AI-powered recommendations (Gemini) for personalized guidance.

**Key features**
- Log daily activities: sleep, study/work, activities, mood, water, steps, screen time.
- Interactive dashboard with KPIs, trend charts, moving averages, and activity heatmaps.
- Analytics: distributions, correlations, clustering (K-Means) and predictive regression models.
- AI recommendations via Google Gemini (configurable, optional).
- Export data to CSV and generate PDF reports.

**Getting started (local)**
Prerequisites: Python 3.9+ and a system with network access for optional AI features.

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Configure (optional):
- Edit `config.py` to set `DB_NAME`, `ENABLE_AI`, `GEMINI_API_KEY`, and `GEMINI_MODEL`.
- If you don't want AI features, set `ENABLE_AI = False`.

4. Run the app:

```powershell
streamlit run app.py
```

Open the URL printed by Streamlit (usually `http://localhost:8501`).

**Project layout & responsibilities**
- `app.py` : Streamlit front-end (pages: Dashboard, Log Activity, Edit Logs, Analytics, AI Insights, Export).
- `config.py` : App configuration (DB name, AI toggles, Gemini API key & model).
- `database.py` : SQLite helper functions (create tables, insert/update/fetch logs, export CSV).
- `data_processing.py` : Data transformation and summary utilities (dataframe creation, scoring, summaries, heatmap data).
- `ml_utils.py` : Simple ML helpers (K-Means clustering, linear regression training, predictions).
- `recommendations.py` : Wrapper for Google Gemini (AI) prompts and error handling.
- `export_utils.py` : PDF generation utilities using ReportLab.
- `requirements.txt` : Python dependencies.
- `habits.db` : Local SQLite database (auto-created on first run).

**Important configuration notes**
- The app stores user logs in the SQLite file referenced by `DB_NAME` in `config.py` (default: `habits.db`).
- For AI recommendations, obtain a Gemini API key and set `GEMINI_API_KEY` in `config.py`. The app includes helpful error messages when AI fails.
- `ENABLE_PDF_EXPORT` controls PDF generation availability. ReportLab is required for PDF export.

**Security & privacy**
- This app stores data locally in `habits.db`. If you deploy it, secure the host and database appropriately.
- Do not commit sensitive API keys to public repositories. Use environment variables or a secrets manager for deployments.

**Development & contribution**
- Formatting / linting: keep consistent style and avoid large unrelated refactors.
- To contribute: fork, create a feature branch, and open a pull request with a clear description and tests where appropriate.

**How recruiters can evaluate this project**
- Clear, interactive UI showing UX and data visualization skills.
- Use of ML for clustering and prediction demonstrates data science fundamentals and model integration.
- Clean separation between front-end, data-processing, database, ML, and export utilities indicates good architecture.

**License**
This project includes a `LICENSE` file — check it for license details.

**Contact / Author**
Project by Pandurang Chavan. For questions or collaboration, open an issue or contact via the GitHub profile.

