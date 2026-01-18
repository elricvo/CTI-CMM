# CTI-CMM Mini - User Guide

## Overview

CTI-CMM Mini is a lightweight web app for CTI/Risk maturity assessments.
It lets you create assessments, score practices, link assets, and view
an aggregated dashboard and backlog.

## Start the app (Mode A)

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\run.ps1
```

Windows CMD:

```bat
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
scripts\run.bat
```

Open the UI:

- http://127.0.0.1:9999/

## Language selection

Use the Language selector in the header to switch between English and French.
The choice is stored in your browser (localStorage).

Server default language:

- Set `APP_DEFAULT_LANG` to `en` or `fr` before starting the app.

Example:

```bash
APP_DEFAULT_LANG=fr ./scripts/run.sh
```

## Create an assessment

1) Enter a name, date, and notes (optional).
2) Click **Create assessment**.
3) The new assessment becomes active.

## Score practices

1) In the **Practices** table, click **Edit** on a practice.
2) Set Score (CTI0-CTI3 or N/A) and optional target/impact/effort/priority.
3) Click **Save**.

The dashboard and backlog refresh automatically after saving.

## Manage assets

1) Create an asset in the **Assets** section.
2) Link an asset to a practice using the link form.

## Dashboard and backlog

- **Dashboard** shows average score and completion per domain.
- **Backlog** lists practices where target score is higher than current score.

## Data persistence

All data is stored in `data/app.db` (SQLite).
To move storage, set `APP_DATA_DIR` to another folder.

## Troubleshooting

- Port already in use: edit `scripts/run.*` or stop the other service.
- Missing modules: ensure you installed dependencies in `.venv`.
- Database reset: delete `data/app.db` to recreate the schema.
