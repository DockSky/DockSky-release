#!/usr/bin/env python3
"""Crée le projet démo « Boutique Lumière » et satellites dans DockSky via MCP."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MCP_URL = "https://api.docksky.fr/tda/mcp"
MCP_JSON = Path("/home/bob/projets/docksky-api/.vscode/mcp.json")


def load_token() -> str:
    data = json.loads(MCP_JSON.read_text())
    return data["mcpServers"]["tda-assistant-api"]["headers"]["X-AI-Token"]


def mcp(token: str, tool: str, arguments: dict | None = None) -> str:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments or {}},
    }
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "X-AI-Token": token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"MCP HTTP {e.code}: {e.read().decode()}") from e

    if "error" in body:
        raise SystemExit(f"MCP error: {body['error']}")

    result = body.get("result", {})
    content = result.get("content", [])
    if content and content[0].get("type") == "text":
        return content[0].get("text", "")
    return json.dumps(result)


def parse_project_id(text: str) -> int:
    m = re.search(r"\[(\d+)\]", text)
    if not m:
        raise ValueError(f"ID projet introuvable dans: {text!r}")
    return int(m.group(1))


def parse_facet_id(text: str) -> int:
    return parse_project_id(text)


def parse_step_id(text: str) -> int:
    data = json.loads(text)
    return int(data["id"])


def list_projects(token: str) -> dict[str, int]:
    raw = mcp(token, "list_projects")
    projects: dict[str, int] = {}
    for line in raw.splitlines():
        m = re.match(r".*\[(\d+)\]\s+(.+?)\s+—", line)
        if m:
            projects[m.group(2).strip()] = int(m.group(1))
    return projects


def ensure_project(
    token: str,
    existing: dict[str, int],
    title: str,
    *,
    description: str,
    emoji: str,
    status: str,
    color: str,
    hours: float,
    ai_access: str = "WRITE",
) -> int:
    if title in existing:
        pid = existing[title]
        print(f"  existe déjà [{pid}] {title}")
    else:
        text = mcp(
            token,
            "create_project",
            {
                "title": title,
                "description": description,
                "emoji": emoji,
                "ai_access": ai_access,
            },
        )
        pid = parse_project_id(text)
        print(f"  créé [{pid}] {title}")

    mcp(
        token,
        "update_project",
        {
            "project_id": pid,
            "fields": {
                "description": description,
                "status": status,
                "emoji": emoji,
                "color": color,
                "estimated_total_hours": hours,
                "ai_access": ai_access,
            },
        },
    )
    return pid


def ensure_facet(
    token: str, project_id: int, facets: dict[str, int], spec: dict
) -> int:
    name = spec["name"]
    if name in facets:
        return facets[name]

    text = mcp(token, "create_facet", {"project_id": project_id, **spec})
    fid = parse_facet_id(text)
    facets[name] = fid
    print(f"    facette [{fid}] {name}")
    return fid


def add_entry(token: str, facet_id: int, entry: dict) -> None:
    mcp(token, "add_facet_entry", {"facet_id": facet_id, **entry})


def add_step(
    token: str, project_id: int, *, title: str, order: int, group: str
) -> int:
    text = mcp(
        token,
        "create_step",
        {
            "project_id": project_id,
            "title": title,
            "display_order": order,
            "status": "IN_PROGRESS" if order == 1 else "TODO",
        },
    )
    sid = parse_step_id(text)
    mcp(token, "update_step", {"step_id": sid, "fields": {"group_label": group}})
    return sid


def add_action(
    token: str,
    step_id: int,
    *,
    title: str,
    order: int,
    status: str,
    minutes: int,
) -> None:
    text = mcp(
        token,
        "create_action",
        {
            "step_id": step_id,
            "title": title,
            "display_order": order,
            "status": status,
        },
    )
    data = json.loads(text)
    mcp(
        token,
        "update_action",
        {
            "action_id": data["id"],
            "fields": {"estimated_minutes": minutes},
        },
    )


def seed_boutique_lumiere(token: str, pid: int) -> None:
    raw = mcp(token, "list_facets", {"project_id": pid})
    facets = {f["name"]: f["id"] for f in json.loads(raw)}

    facet_specs = [
        {
            "name": "Brief client",
            "slug": "brief-client",
            "domain_color": "orange",
            "domain_label": "Client",
            "icon": "📋",
            "sort_order": 1,
        },
        {
            "name": "Décisions validées",
            "slug": "decisions-validees",
            "domain_color": "green",
            "domain_label": "Décisions",
            "icon": "✅",
            "sort_order": 2,
        },
        {
            "name": "Pièges",
            "slug": "pieges",
            "domain_color": "red",
            "domain_label": "Attention",
            "icon": "⚠️",
            "sort_order": 3,
        },
        {
            "name": "Contacts & accès",
            "slug": "contacts-acces",
            "domain_color": "blue",
            "domain_label": "Contacts",
            "icon": "📞",
            "sort_order": 4,
        },
        {
            "name": "Planning",
            "slug": "planning",
            "domain_color": "purple",
            "domain_label": "Planning",
            "icon": "📅",
            "sort_order": 5,
        },
    ]

    for spec in facet_specs:
        ensure_facet(token, pid, facets, spec)

    entries = {
        "Brief client": [
            {
                "entry_type": "NOTE",
                "title": "Ton souhaité — chaleureux, artisanal",
                "content": "La cliente veut une ambiance « atelier » : photos naturelles, pas de stock photo. Couleurs terre & miel.",
            },
            {
                "entry_type": "NOTE",
                "title": "Cible & positionnement",
                "content": "Clientes 30-55 ans, amatrices de déco. Panier moyen visé : 45 €. Livraison France métropolitaine uniquement.",
            },
            {
                "entry_type": "TRAP",
                "title": "À éviter : look « marketplace »",
                "content": "Elle a dit non aux grilles type Amazon. Préfère des mises en scène par collection (bougies / céramiques).",
            },
        ],
        "Décisions validées": [
            {
                "entry_type": "DECISION",
                "title": "Paiement : Stripe + PayPal",
                "content": "Validé par email le 04/06. Pas de paiement en 3× pour l'instant.",
            },
            {
                "entry_type": "DECISION",
                "title": "Charte graphique — tons miel & lin",
                "content": "Palette validée en visio le 10/06. Typo titres : Playfair Display. Corps : Source Sans 3.",
            },
            {
                "entry_type": "DECISION",
                "title": "Hébergement OVH + nom de domaine",
                "content": "Domaine boutique-lumiere.fr déjà acheté par la cliente. Hébergement mutualisé suffisant pour le lancement.",
            },
        ],
        "Pièges": [
            {
                "entry_type": "TRAP",
                "title": "Photos produits — ne pas retoucher à l'excès",
                "content": "Retouches trop lourdes sur la céramique = refus client en mars sur un autre site. Garder le grain naturel.",
            },
            {
                "entry_type": "TRAP",
                "title": "Délais : éviter les promesses avant validation maquettes",
                "content": "La cliente change d'avis sur les couleurs. Toujours faire valider par écrit avant dev.",
            },
        ],
        "Contacts & accès": [
            {
                "entry_type": "NOTE",
                "title": "Claire Moreau — dirigeante",
                "content": "claire@boutique-lumiere-demo.fr · 06 12 34 56 78. Disponible mardi/jeudi après-midi.",
            },
            {
                "entry_type": "NOTE",
                "title": "Accès prestataires",
                "content": "Figma partagé · Google Drive « BL-Refonte-2026 » · PrestaShop admin (fourni fin juin).",
            },
        ],
        "Planning": [
            {
                "entry_type": "NOTE",
                "title": "Jalons clés",
                "content": "Maquettes validées : 20/06 · Contenu produits : 05/07 · Recette : 15/09 · Mise en ligne : 30/09.",
            },
        ],
    }

    for facet_name, facet_entries in entries.items():
        fid = facets[facet_name]
        for entry in facet_entries:
            add_entry(token, fid, entry)

    # Roadmap — viser ~58 % de progression (4 actions DONE sur 7)
    step1 = add_step(
        token, pid, title="Cadrage & maquettes", order=1, group="Phase 1"
    )
    step2 = add_step(
        token, pid, title="Contenu & mise en ligne", order=2, group="Phase 2"
    )

    phase1 = [
        ("Valider la charte graphique avec la cliente", "DONE", 120),
        ("Maquettes page d'accueil + catalogue produits", "DONE", 360),
        ("Recueillir les retours — email du 12/06", "DONE", 60),
        ("Valider maquettes mobile", "TODO", 180),
    ]
    phase2 = [
        ("Rédiger les fiches produits (12 références)", "TODO", 480),
        ("Configurer paiement & livraison", "TODO", 240),
        ("Tests commande + recette cliente", "TODO", 180),
    ]

    for i, (title, status, mins) in enumerate(phase1, 1):
        add_action(token, step1, title=title, order=i, status=status, minutes=mins)
    for i, (title, status, mins) in enumerate(phase2, 1):
        add_action(token, step2, title=title, order=i, status=status, minutes=mins)

    mcp(
        token,
        "update_project",
        {
            "project_id": pid,
            "fields": {
                "current_status": (
                    "## Boutique Lumière\n"
                    "Maquettes desktop validées. En attente validation mobile. "
                    "Prochaine étape : fiches produits."
                ),
            },
        },
    )


def seed_light_roadmap(token: str, pid: int, steps: list[tuple[str, str, int]]) -> None:
    """Roadmap minimale pour les projets satellites."""
    for order, (title, group, _) in enumerate(steps, 1):
        sid = add_step(token, pid, title=title, order=order, group=group)
        add_action(
            token,
            sid,
            title=f"Première action — {title.lower()}",
            order=1,
            status="TODO",
            minutes=120,
        )


def main() -> None:
    token = load_token()
    print("Connexion MCP…")
    existing = list_projects(token)
    print(f"Projets existants : {len(existing)}")

    boutique_id = ensure_project(
        token,
        existing,
        "Boutique Lumière",
        description="Refonte site e-commerce — cliente artisanale (bougies & céramique). Livraison prévue fin septembre.",
        emoji="🕯️",
        status="ACTIVE",
        color="#f59e0b",
        hours=80,
    )

    editions_id = ensure_project(
        token,
        existing,
        "Les Éditions du Vent",
        description="Maquettes site vitrine — maison d'édition indépendante (20 titres au catalogue).",
        emoji="📚",
        status="ACTIVE",
        color="#7c3aed",
        hours=40,
    )

    audit_id = ensure_project(
        token,
        existing,
        "Audit RH — Dupont & Fils",
        description="Mission conseil RH — audit processus recrutement. 3 jours estimés.",
        emoji="💼",
        status="DRAFT",
        color="#64748b",
        hours=24,
    )

    roman_id = ensure_project(
        token,
        existing,
        "Roman — Les Brumes",
        description="Projet perso — roman contemporain. Suivi chapitres, personnages et arcs narratifs.",
        emoji="✍️",
        status="DRAFT",
        color="#059669",
        hours=200,
    )

    print("\nContenu Boutique Lumière…")
    seed_boutique_lumiere(token, boutique_id)

    print("\nRoadmaps satellites…")
    seed_light_roadmap(
        token,
        editions_id,
        [
            ("Brief éditorial", "Phase 1", 1),
            ("Maquettes accueil", "Phase 2", 2),
        ],
    )
    # Marquer une action done pour ~22 % sur Éditions du Vent
    steps_raw = mcp(token, "list_steps", {"project_id": editions_id})
    steps = json.loads(steps_raw)
    if steps:
        actions_raw = mcp(token, "list_actions", {"step_id": steps[0]["id"]})
        actions = json.loads(actions_raw)
        if actions:
            mcp(
                token,
                "update_action",
                {"action_id": actions[0]["id"], "fields": {"status": "IN_PROGRESS"}},
            )

    mcp(token, "set_active_work_context", {"project_id": boutique_id})
    print(f"\n✅ Terminé — projet actif : Boutique Lumière [{boutique_id}]")
    print("\nCaptures suggérées :")
    print("  1. Bandeau — projet « Boutique Lumière » actif")
    print("  2. Gestion des projets — les 4 projets visibles")
    print("  3. Roadmap — Boutique Lumière sélectionné")
    print("  4. Facettes — Brief client ou Décisions validées")


if __name__ == "__main__":
    main()
