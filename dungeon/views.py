import hashlib
import json
import random
import re

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import DungeonZone, RumorMonster, PlayerSession, LeaderboardEntry
from .utils.serp_verifier import verify_claim_with_serpapi

SEED = [
    ("Whisper Woods", "Forwarded-message folklore drifts between the trees.", 1, "🌲", [
        ("Hot-Water Goblin", "Drinking hot water every 15 minutes cures COVID-19", "Goblin", 1),
        ("Darkness Goblin", "NASA confirmed India will have 6 days of total darkness", "Goblin", 1)]),
    ("Forwarded Fortress", "A castle built from chain messages and screenshots.", 2, "🏰", [
        ("Tower Phantom", "5G towers spread coronavirus", "Phantom", 2),
        ("Fee Phantom", "WhatsApp will start charging users a monthly fee", "Phantom", 2)]),
    ("Deepfake Depths", "The deepest vault, where dragons breathe viral lies.", 3, "🌋", [
        ("Magnet Dragon", "COVID vaccines contain magnetic microchips", "Dragon", 3),
        ("Garlic Dragon", "Eating garlic prevents all viral infections", "Dragon", 3)]),
]
ACTIONS = ("probe", "crossref", "datecheck")


def ensure_seed():
    if DungeonZone.objects.exists():
        return
    for name, desc, danger, icon, monsters in SEED:
        z = DungeonZone.objects.create(name=name, description=desc, danger_level=danger, badge_icon=icon)
        for mn, claim, mt, diff in monsters:
            RumorMonster.objects.create(zone=z, name=mn, claim_text=claim, monster_type=mt, difficulty=diff)


def get_player(request):
    pid = request.session.get("player_id")
    p = PlayerSession.objects.filter(pk=pid).first() if pid else None
    if not p:
        p = PlayerSession.objects.create(player_name="Rookie")
        request.session["player_id"] = p.id
    return p


def player_dict(p):
    return {"name": p.player_name, "hp": p.hp, "xp": p.xp, "level": p.level,
            "cleared": p.dungeons_cleared, "xp_pct": p.xp % 100}


def save_score(p):
    LeaderboardEntry.objects.update_or_create(
        player_name=p.player_name, defaults={"score": p.xp * 10 + p.dungeons_cleared * 50})


def get_evidence(claim):
    key = "ev:" + hashlib.md5(re.sub(r"\s+", " ", claim.strip().lower()).encode()).hexdigest()
    ev = cache.get(key)
    if ev is None:
        ev = verify_claim_with_serpapi(claim)
        if ev["success"]:
            cache.set(key, ev, 3600)
    return ev


def verdict(score):
    if score <= 35:
        return "LIKELY FALSE: debunking signals found"
    if score <= 65:
        return "UNVERIFIED: mixed or thin evidence"
    return "LIKELY TRUE: no debunking signals found"


def years_in(ev):
    text = " ".join(ev["snippets"] + ev["titles"])
    return sorted(set(re.findall(r"\b(?:19|20)\d\d\b", text)))


def compute_damage(action, ev):
    if not ev["success"]:
        return 8
    if action == "probe":
        return 12 + 6 * len([s for s in ev["sources"] if s])
    if action == "crossref":
        return 14 + abs(50 - ev["truth_score"]) // 2
    return 10 + 6 * min(len(years_in(ev)), 4)


def action_payload(action, ev):
    if action == "probe":
        return {"kind": "probe", "items": [{"title": t, "link": l} for t, l in zip(ev["titles"], ev["sources"])]}
    if action == "crossref":
        return {"kind": "crossref", "truth_score": ev["truth_score"], "verdict": verdict(ev["truth_score"]),
                "snippets": ev["snippets"]}
    return {"kind": "datecheck", "years": years_in(ev), "snippets": ev["snippets"]}


def world_map(request):
    ensure_seed()
    zones = DungeonZone.objects.prefetch_related("monsters").order_by("danger_level")
    return render(request, "map.html", {"zones": zones})


def battle(request, monster_id):
    m = get_object_or_404(RumorMonster, pk=monster_id)
    request.session[f"mhp_{m.id}"] = 100
    return render(request, "battle.html", {"monster": m})


@require_POST
def battle_action(request, monster_id):
    m = get_object_or_404(RumorMonster, pk=monster_id)
    p = get_player(request)
    try:
        action = json.loads(request.body).get("action")
    except ValueError:
        action = None
    if action not in ACTIONS:
        return JsonResponse({"error": "Unknown action"}, status=400)

    ev = get_evidence(m.claim_text)
    dmg = compute_damage(action, ev)
    key = f"mhp_{m.id}"
    mhp = max(0, request.session.get(key, 100) - dmg)
    counter = 0 if mhp == 0 else random.randint(3, 6) * m.difficulty
    if dmg >= 25:
        counter //= 2
    p.hp = max(0, p.hp - counter)
    state, xp_gain = "ongoing", 0
    if mhp == 0:
        state = "win"
        xp_gain = 20 * m.difficulty + (10 if ev["truth_score"] < 50 else 0)
        p.xp += xp_gain
        p.level = 1 + p.xp // 100
        p.dungeons_cleared += 1
        save_score(p)
    elif p.hp == 0:
        state = "lose"
        p.xp = max(0, p.xp - 10)
        p.level = 1 + p.xp // 100
        p.hp = 100
        mhp = 100
        save_score(p)
    request.session[key] = mhp
    p.save()
    return JsonResponse({
        "action": action, "damage": dmg, "counter": counter, "monster_hp": mhp, "state": state,
        "xp_gain": xp_gain, "player": player_dict(p), "api_ok": ev["success"], "api_error": ev.get("error", ""),
        "evidence": action_payload(action, ev),
    })


def custom_arena(request):
    return render(request, "custom_arena.html")


@require_POST
def custom_scan(request):
    try:
        claim = json.loads(request.body).get("claim", "").strip()
    except ValueError:
        claim = ""
    if len(claim) < 5:
        return JsonResponse({"error": "Enter a headline, claim or URL (5+ characters)."}, status=400)
    claim = claim[:300]
    p = get_player(request)
    ev = get_evidence(claim)
    score = ev["truth_score"]
    mtype = "Dragon" if score <= 35 else "Phantom" if score <= 65 else "Goblin"
    icon = {"Goblin": "👺", "Dragon": "🐉", "Phantom": "👻"}[mtype]
    hp, rounds = 100, []
    for i in range(6):
        act = ACTIONS[i % 3]
        d = compute_damage(act, ev)
        hp = max(0, hp - d)
        rounds.append({"action": act, "damage": d, "monster_hp": hp})
        if hp == 0:
            break
    won = hp == 0
    xp_gain = 10 if ev["success"] else 0
    if xp_gain:
        p.xp += xp_gain
        p.level = 1 + p.xp // 100
        if won:
            p.dungeons_cleared += 1
        p.save()
        save_score(p)
    return JsonResponse({
        "monster": {"name": f"Spawned {mtype}", "type": mtype, "icon": icon, "claim": claim},
        "truth_score": score, "verdict": verdict(score), "rounds": rounds, "won": won,
        "xp_gain": xp_gain, "player": player_dict(p), "api_ok": ev["success"], "api_error": ev.get("error", ""),
        "sources": [{"title": t, "link": l, "snippet": s} for t, l, s in zip(ev["titles"], ev["sources"], ev["snippets"])],
    })


def leaderboard(request):
    return render(request, "leaderboard.html", {"entries": LeaderboardEntry.objects.all()[:20]})


@require_POST
def rename(request):
    try:
        name = json.loads(request.body).get("name", "").strip()[:40]
    except ValueError:
        name = ""
    if not name:
        return JsonResponse({"error": "Name required"}, status=400)
    p = get_player(request)
    LeaderboardEntry.objects.filter(player_name=p.player_name).update(player_name=name)
    p.player_name = name
    p.save()
    return JsonResponse({"player": player_dict(p)})
