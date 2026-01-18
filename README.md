# CTI-CMM Mini App

Mini web-app Python + SQLite pour evaluer la maturite CTI/Risk.

## CTI-CMM en bref

CTI-CMM signifie :

- Cyber Threat Intelligence Capability Maturity Model
- En francais : Modele de maturite des capacites en Cyber Threat Intelligence.

Definitions simples :

- Cyber Threat Intelligence (CTI) : discipline qui consiste a collecter, analyser et utiliser des informations sur les menaces (attaquants, techniques, campagnes) pour mieux se proteger et prendre de meilleures decisions.
- Capability : les capacites concretes d'une equipe CTI (ce qu'elle sait faire reellement).
- Maturity Model : un modele qui permet de situer ton niveau sur une echelle et de voir comment progresser.

CTI-CMM est donc un cadre (framework) qui decrit des pratiques CTI et permet
d'evaluer la maturite d'un programme CTI sur plusieurs domaines (le site
CTI-CMM parle de 11 domaines).

## Echelle CTI0 -> CTI3

Le tableur utilise une echelle en 4 niveaux :

- CTI0 : pas de capacite / pas en place
- CTI1 : partiellement en place
- CTI2 : largement en place
- CTI3 : totalement en place (pleinement operationnel)

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
