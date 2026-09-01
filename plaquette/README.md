# Plaquette DockSky (FR)

Matériel recto-verso pour présenter DockSky.

| Face | Public | Statut |
|------|--------|--------|
| **Recto** | Usage général (non dev) | Textes brouillon — à valider |
| **Verso** | Développeurs | Textes brouillon — à valider |

## Workflow

1. **Textes** — valider `textes/recto.md` et `textes/verso.md`
2. **Captures** — déposer dans `assets/screenshots/recto/` ou `verso/`, mettre à jour `assets/screenshots/MANIFEST.md`
3. **Mise en forme** — export final dans `output/` (PDF A4)

## Arborescence

```
plaquette/
├── README.md                 ← ce fichier
├── textes/
│   ├── recto.md              ← contenu face grand public
│   └── verso.md              ← contenu face développeurs
├── assets/
│   ├── branding/             ← logo, couleurs (à fournir)
│   └── screenshots/
│       ├── MANIFEST.md       ← inventaire des captures + usage prévu
│       ├── recto/
│       └── verso/
├── demo/
│   ├── projet-demo.md          ← scénario « Boutique Lumière »
│   ├── common.css
│   └── *.html                  ← maquettes recto (rendues en PNG)
├── scripts/
│   ├── prepare_assets.py       ← traitement captures réelles (verso)
│   ├── render_demo.py          ← génère assets/processed/demo/
│   └── build_pdf.sh
```

## Format cible

- **A4 recto-verso** (210 × 297 mm)
- Langue : **français** (version EN plus tard si besoin)

## Captures

Déposer les PNG dans `assets/screenshots/recto/` ou `verso/`, puis regénérer le PDF (voir ci-dessous).

Le **recto** utilise les vraies captures de l'app (projet démo Boutique Lumière).
Le **verso** garde les captures dev.

## Générer le contenu dans DockSky

```bash
python3 scripts/seed_projet_demo.py
```

Crée les 4 projets du scénario Marie (freelance) dans ton compte DockSky via MCP.
Projet actif après seed : **Boutique Lumière**.

| Projet | ID (juil. 2026) |
|--------|-----------------|
| Boutique Lumière | 607 |
| Les Éditions du Vent | 608 |
| Audit RH — Dupont & Fils | 609 |
| Roman — Les Brumes | 610 |

## Générer le PDF

Depuis le dossier `docksky-release/plaquette` :

```bash
python3 scripts/prepare_assets.py
bash scripts/build_pdf.sh
```

→ `output/plaquette-docksky-a4.pdf`

**Si `bash scripts/build_pdf.sh` échoue** (droits, CRLF Windows…) :

```bash
cd /home/bob/projets/docksky-release/plaquette
python3 scripts/prepare_assets.py
chromium --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf=output/plaquette-docksky-a4.pdf --no-pdf-header-footer \
  "file://$(pwd)/plaquette.html"
```

Ou ouvrir `plaquette.html` dans Firefox/Chrome → Imprimer → PDF, format A4.

## Points en suspens

- [ ] Choisir l'accroche recto (A / B / C dans `textes/recto.md`)
- [ ] Tutoiement ou vouvoiement
- [ ] Mention TDA sur le recto ?
- [ ] Badge « Accès anticipé » en bas de page ?
- [ ] Captures manquantes (voir MANIFEST)
