# Snap DockSky (copie publique)

Copie publique de `snap/snapcraft.yaml` pour la revue Snap Store (forum Snapcraft, lien reviewable).

**Confinement :** `strict` (juillet 2026)

| Plug | Rôle |
|------|------|
| `home` | Accès aux dossiers projet (`~/Projects`, etc.) + file activity |
| `network` / `network-bind` | API DockSky + serveur MCP local (localhost) |
| `x11` / `wayland` / `desktop` / `opengl` | UI Avalonia + bandeau always-on-top |

**Config / données :** via variables d'environnement vers `$SNAP_USER_COMMON` (pas de `personal-files`).

**Source de build :** repo privé `DockSky/tda-assistant-ui` — binaire .NET self-contained, build via `installer/snap/build-snap.sh`.

Ce dossier ne sert pas à packager le snap ; il expose la définition pour les reviewers Canonical.

Forum : https://forum.snapcraft.io/t/classic-confinement-request-for-docksky/51993
