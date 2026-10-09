# StudyFlow — Study Planner & Focus Tracker

A bilingual English/Arabic Streamlit app for organizing study tasks, logging focus sessions, and reviewing progress. Unlike the previous bank churn demo, this is a personal productivity tool; it does not require a dataset, machine-learning model, API key, or account.

## Features

- Create study tasks with subject, deadline, and priority.
- Track each task as Open, In progress, or Completed; delete tasks with a confirmation step.
- Log focus sessions with duration and optional notes.
- Dashboard metrics, weekly study-time chart, and time-by-subject chart.
- Export tasks and study sessions as CSV.
- Local SQLite storage; database location can be configured with `STUDYFLOW_DB_PATH`.
- English and Arabic UI labels.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. SQLite data is created automatically in `data/studyflow.db`.

## Data and deployment notes

- Your records stay in the local SQLite file; the app does not send them to an external service.
- Back up `data/studyflow.db` regularly if your task history matters.
- Many hosted app platforms use temporary filesystems, so local SQLite may reset after a redeploy or restart. For a hosted deployment with durable multi-user storage, configure persistent storage or replace SQLite with a managed database.
- Do not commit private notes or a personal database. `.gitignore` excludes `data/studyflow.db`.

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

GitHub Actions runs the tests on pushes and pull requests.
