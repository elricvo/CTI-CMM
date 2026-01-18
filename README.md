# CTI-CMM Mini App

Mini web-app Python + SQLite pour evaluer la maturite CTI/Risk.

## Statut

MVP en cours (v0.1). L'app demarre en Mode A.

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

## Demarrer (Mode A)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

Ouvrir: http://127.0.0.1:9999/

## Donnees de test

Pour lancer avec un jeu de donnees riche:

```bash
./scripts/run.sh --test-data
```

## Langue

Selecteur de langue dans l'UI (EN/FR). Le defaut serveur se regle via
`APP_DEFAULT_LANG` (valeurs: `en` ou `fr`).

## Documentation utilisateur

Voir `docs/user-guide.md`.

## Roadmap courte

Voir `.codex/TODO.md` pour l'ordre recommande.
