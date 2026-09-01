# Verso — pour les développeurs

> Statut : **brouillon**

---

## Accroche

**Contexte technique prêt en 10 secondes.**  
Stack, conventions, bugs connus, décisions d'archi — ton IA les connaît avant la première ligne de code.

---

## Le problème dev

À chaque session Cursor, Claude ou Copilot, tu réexpliques ton repo, tes patterns, ce qui a planté la dernière fois. **5 à 10 minutes perdues** avant de vraiment coder.

---

## Les Facettes techniques

Un projet par base de code. Mémoire organisée par thème :

| Facette | Contenu |
|---------|---------|
| **Contexte IA** | Stack, conventions, règles de collaboration |
| **Décisions archi** | Pourquoi ce choix plutôt qu'un autre |
| **Bugs & solutions** | Ce qui a cassé, comment c'était résolu |
| **Accès & config** | Ports, variables, commandes utiles |

**Workflow :** Facettes → **Copier le contexte** → coller en tête de session → tu codes.

---

## Contextes IA réutilisables

Des « paquets » prêts selon le type de session :

- *Backend* → BDD + API + bugs connus
- *Déploiement* → VPS + Docker + pièges infra
- *Front* → composants + patterns UI

Zéro réexplication.

---

## MCP natif (Cursor / VS Code)

Branche DockSky en **MCP** : ton IA lit et écrit dans tes projets, facettes et tâches — **sans copier-coller**.

- Token IA dans Paramètres → Accès IA
- URL : `api.docksky.fr/tda/mcp`
- Contexte chargé automatiquement à chaque session

---

## Journal alimenté par Git *(optionnel)*

Chaque commit peut s'enregistrer dans le **Journal de bord**.  
Trace technique automatique de tes décisions — sans effort manuel.

---

## Pilotage IA / Synapse *(plan Pro)*

Exécuter sur ton infra **sans coller de mot de passe dans le chat.**

- Secrets dans un coffre personnel (`{{DB_PASS}}`, etc.)
- Machines et conteneurs déclarés
- L'IA appelle `synapse_exec` via MCP — secrets injectés côté serveur
- Journal consultable de tout ce qui a été exécuté

---

## Stack technique (bandeau discret)

```
Desktop : Avalonia / .NET 8  —  Linux, Windows · macOS bientôt
API     : FastAPI / Python   —  api.docksky.fr
Téléchargement : docksky.fr/telecharger
```

---

## Bas de page

```
Documentation dev : docs.docksky.fr/integration-ia
GitHub : github.com/DockSky
```

---

## Captures prévues (verso)

| Fichier | Usage |
|---------|-------|
| `04-facettes.png` *(partagé recto)* | Facettes + bouton **Copier JSON** |
| `01-contextes-ia.png` | **Contextes IA** — paquets de session, export JSON, profil IA |
| `02-acces-ia-mcp.png` | **Accès IA / MCP** — token, limites, coffre Pilotage IA |
| *(à fournir)* | Journal Git ou Pilotage IA / Synapse |
