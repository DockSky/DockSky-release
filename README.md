# DockSky — Documentation (Docusaurus)

Site public : **https://docs.docksky.fr**

## Développement local

```bash
npm ci
npm start          # http://localhost:3000
```

## Build

```bash
npm run build      # génère build/
```

## Déploiement

### Automatique (recommandé)

À chaque **push sur `main`** (fichiers docs/sources), GitHub Actions :

1. `npm ci && npm run build`
2. `rsync` du dossier `build/` vers le VPS (`docksky_docs` / nginx)

**Secrets GitHub** (repo `DockSky/DockSky-release` → Settings → Secrets) :

| Secret | Description |
|--------|-------------|
| `VPS_HOST` | Hostname ou IP du VPS — **ne jamais committer** |
| `VPS_SSH_PRIVATE_KEY` | Clé privée SSH (deploy key) avec accès `debian@VPS` |
| `VPS_USER` | Optionnel, défaut `debian` |

Configuration initiale (une fois, en local — remplace `<VPS_HOST>` par la vraie valeur) :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github_actions -N "" -C "github-actions@docksky"
ssh-copy-id -i ~/.ssh/id_ed25519_github_actions.pub debian@<VPS_HOST>

gh secret set VPS_SSH_PRIVATE_KEY -R DockSky/DockSky-release < ~/.ssh/id_ed25519_github_actions
gh secret set VPS_HOST -R DockSky/DockSky-release -b "<VPS_HOST>"
```

Workflow : `.github/workflows/deploy-docs.yml`

### Manuel (immédiat)

```bash
./deploy.sh                 # build local + rsync VPS (alias SSH local requis)
./deploy.sh --push-only     # push seulement → CI déploie
./deploy.sh --first-time    # premier clone sur le VPS
```

### Infra VPS

| Élément | Valeur |
|---------|--------|
| Chemin | `~/docker/docksky-docs` (sur le VPS) |
| Conteneur | `docksky_docs` (nginx:alpine) |
| Volume | `./build` → `/usr/share/nginx/html` |
| Réseau | réseau Docker Traefik partagé (`infra_app-network`) |

Le dossier `build/` reste versionné pour repli manuel (`git pull` sur le VPS), mais le déploiement CI utilise **rsync** sans rebuild sur le serveur.
