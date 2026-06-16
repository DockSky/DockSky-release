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

**Secrets GitHub à configurer** (repo `DockSky/DockSky-release` → Settings → Secrets) :

| Secret | Valeur |
|--------|--------|
| `VPS_HOST` | IP ou hostname du VPS (ex. `141.95.162.159`) |
| `VPS_SSH_PRIVATE_KEY` | Clé privée SSH (deploy key) avec accès `debian@VPS` |
| `VPS_USER` | Optionnel, défaut `debian` |

Générer une clé dédiée (sur ta machine) :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/docksky-docs-deploy -N ""
ssh-copy-id -i ~/.ssh/docksky-docs-deploy.pub debian@<VPS>
# Coller le contenu de ~/.ssh/docksky-docs-deploy dans le secret VPS_SSH_PRIVATE_KEY
```

Workflow : `.github/workflows/deploy-docs.yml`

### Manuel (immédiat)

```bash
./deploy.sh                 # build local + rsync VPS
./deploy.sh --push-only     # push seulement → CI déploie
./deploy.sh --first-time    # premier clone sur VPS
```

### Infra VPS

| Élément | Valeur |
|---------|--------|
| Chemin | `/home/debian/docker/docksky-docs` |
| Conteneur | `docksky_docs` (nginx:alpine) |
| Volume | `./build` → `/usr/share/nginx/html` |
| Réseau | `infra_app-network` (Traefik) |

Le dossier `build/` reste versionné pour repli manuel (`git pull` sur le VPS), mais le déploiement CI utilise **rsync** sans rebuild sur le serveur.
