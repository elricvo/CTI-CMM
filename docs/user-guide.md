# CTI-CMM Mini - User Guide

## Overview

CTI-CMM Mini is a lightweight web app for CTI/Risk maturity assessments.
It lets you create assessments, score practices, link assets, and view
an aggregated dashboard and backlog.

## CTI-CMM basics

CTI-CMM stands for:

- Cyber Threat Intelligence Capability Maturity Model
- En francais : Modèle de maturité des capacités en Cyber Threat Intelligence.

Definitions:

- Cyber Threat Intelligence (CTI): the discipline of collecting, analyzing, and using threat information (attackers, techniques, campaigns) to improve protection and decisions.
- Capability: the concrete abilities of a CTI team (what it can actually do).
- Maturity Model: a model to place your level on a scale and see how to improve.

CTI-CMM is a framework that describes CTI practices and helps you assess
CTI maturity across multiple domains (the CTI-CMM site mentions 11 domains).

## CTI0 -> CTI3 scale

The assessment uses a 4-level scale:

- CTI0: no capability / not in place
- CTI1: partially in place
- CTI2: largely in place
- CTI3: fully in place (fully operational)

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

## Start with test data

Use the `--test-data` flag to launch with a rich dataset. This uses
`data-test/` so it does not overwrite your primary data folder.

```bash
./scripts/run.sh --test-data
```

Windows PowerShell:

```powershell
.\scripts\run.ps1 --test-data
```

Windows CMD:

```bat
scripts\run.bat --test-data
```

## Language selection

Use the Language selector in the header to switch between English and French.
The choice is stored in your browser (localStorage).

Server default language:

- Set `APP_DEFAULT_LANG` to `en` or `fr` before starting the app.

Example:

```bash
APP_DEFAULT_LANG=fr ./scripts/run.sh
```

## Quit the app

Use the **Quit** button in the header. It triggers a safe shutdown so you
do not need to press Ctrl+C in the terminal.

Note: for security, shutdown is allowed only from localhost. To allow it
from another host, set `APP_ALLOW_QUIT=1`.

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

## Evolution dashboard

The **Evolution** panel provides:

- Assessment trends (average score and completion by assessment).
- Change history (daily counts of created/updated items).
- Recent changes (last 15 updates and creations).

## Data persistence

All data is stored in `data/app.db` (SQLite).
To move storage, set `APP_DATA_DIR` to another folder.

## Troubleshooting

- Port already in use: edit `scripts/run.*` or stop the other service.
- Missing modules: ensure you installed dependencies in `.venv`.
- Database reset: delete `data/app.db` to recreate the schema.
