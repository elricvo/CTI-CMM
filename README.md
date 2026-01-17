# CTI-CMM Mini App

Mini web-app Python + SQLite pour evaluer la maturite CTI/Risk.

## Statut

Bootstrap en cours (v0.1). L'app n'est pas encore executable.

## Modes cibles

- Mode A : Python + venv, localhost only (127.0.0.1)
- Mode B : binaire Windows via PyInstaller (buildable)
- Mode C : Docker, 0.0.0.0 dans le conteneur, volume `./data`

## Structure

- `app/` : backend Python (API + services + DB)
- `web/index.html` : UI monofichier (HTML/CSS/JS integres)
- `seed/` : referentiel initial (JSON)
- `data/` : persistance SQLite (`app.db`)
- `docker/` : Dockerfile + compose
- `scripts/` : scripts de run/build
- `tests/` : tests minimaux

## Roadmap courte

Voir `.codex/TODO.md` pour l'ordre recommande.
