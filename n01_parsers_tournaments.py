import requests
import json
import time
import os

SEASONS_MANIFEST_PATH = os.path.join("output", "seasons.json")

def load_active_season():
    """Wczytuje output/seasons.json i zwraca sezon oznaczony jako active: true."""
    with open(SEASONS_MANIFEST_PATH, "r", encoding="utf-8") as f:
        seasons = json.load(f)
    active = next((s for s in seasons if s.get("active")), None)
    if active is None:
        raise RuntimeError("Brak aktywnego sezonu w output/seasons.json (active: true).")
    return active

# ============================================================
# KONFIGURACJA TURNIEJÓW — per sezon
# Dodawaj kolejne tournament_id do listy aktywnego sezonu.
# Klucz słownika musi odpowiadać "id" sezonu z output/seasons.json.
# ============================================================

TOURNAMENTS_BY_SEASON = {
    "jesien2026": [
        # ← wpisz tournament_id, gdy turniej zostanie utworzony na Nakce, i odkomentuj.
        # {"name": "Szerszeń Cup 1/4 — Jesień 2026", "tournament_id": "t_XXXX", "category": "szerszen_cup"},
        # {"name": "Open 1/10 — Jesień 2026", "tournament_id": "t_XXXX", "category": "open"},
        # {"name": "Superpuchar Klubu 1/4 — Jesień 2026", "tournament_id": "t_XXXX", "category": "superpuchar"},
    ],

    "wiosna2026": [
    # --- Szerszeń Cup ---
    {
        "name": "Szerszeń Cup I",
        "tournament_id": "t_FTyH_3564",  # ← wpisz ID
        "category": "szerszen_cup"
    },
    {
        "name": "Szerszeń Cup II",
        "tournament_id": "t_DX9M_1537",  # ← wpisz ID
        "category": "szerszen_cup"
    },
    {
        "name": "Szerszeń Cup III",
        "tournament_id": "t_CXq3_9322",  # ← wpisz ID
        "category": "szerszen_cup"
    },
    {
        "name": "Szerszeń Cup IV",
        "tournament_id": "t_2azU_9341",  # ← wpisz ID
        "category": "szerszen_cup"
    },

    # --- Superpuchar Ligi ---
    {
        "name": "Superpuchar Klubu 1z4",
        "tournament_id": "t_4EpK_9361",  # ← wpisz ID
        "category": "superpuchar"
    },
    {
        "name": "Superpuchar Klubu 2z4",
        "tournament_id": "t_8uAR_5330",  # ← wpisz ID
        "category": "superpuchar"
    },
    {
        "name": "Superpuchar Klubu 3z4",
        "tournament_id": "t_IbiD_4721",  # ← wpisz ID
        "category": "superpuchar"
    },
    {
        "name": "Superpuchar Klubu 4z4",
        "tournament_id": "t_PDmW_9784",  # ← wpisz ID
        "category": "superpuchar"
    },

    # --- Openy ---
    {
        "name": "Tomi Dart Club Wiosna 2026 Open 1/10",
        "tournament_id": "t_PSFN_4943",  # ← wpisz ID
        "category": "open"
    },
    {
        "name": "Tomi Dart Club Wiosna 2026 Open 2/10",
        "tournament_id": "t_ujic_7221",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 3/10",
        "tournament_id": "t_8hWQ_8394",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 4/10",
        "tournament_id": "t_luHh_3897",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 5/10",
        "tournament_id": "t_prnH_1222",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 6/10",
        "tournament_id": "t_L6Ik_7953",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 7/10",
        "tournament_id": "t_XAuN_1412",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 8/10",
        "tournament_id": "t_F9Q3_1584",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 9/10",
        "tournament_id": "t_Nnv2_8584",  # ← wpisz ID
        "category": "open"
    },
     {
        "name": "Tomi Dart Club Wiosna 2026 Open 10/10",
        "tournament_id": "t_5t8S_7944",  # ← wpisz ID
        "category": "open"
    },
    ],
}

MATCHES_PER_REQUEST = 30

EXCLUDED_MATCHES = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_MATCH_LIST_URL = "https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_history.php"
BASE_MATCH_VIEW_URL = "https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_user_t.php?cmd=match_view&sid="


# ============================================================
# POBIERANIE DANYCH
# ============================================================

def get_matches(tournament_id, skip=0):
    params = {
        "cmd": "get_t_list",
        "tdid": tournament_id,
        "skip": skip,
        "count": MATCHES_PER_REQUEST,
        "name": ""
    }
    r = requests.get(BASE_MATCH_LIST_URL, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()["list"]

def get_match_detail(tmid):
    data = {"tmid": tmid}
    r = requests.post(BASE_MATCH_VIEW_URL, headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()


# ============================================================
# KALKULACJE — identyczne jak w n01_parser.py
# ============================================================

def calculate_fast_legs(match_detail):
    players_fast_legs = {match_detail["statsData"][0]["name"]: [],
                         match_detail["statsData"][1]["name"]: []}

    for idx, leg in enumerate(match_detail["legData"], start=1):
        winner_index = leg["winner"]
        winner_name = match_detail["statsData"][winner_index]["name"]
        winner_rzuty = leg["playerData"][winner_index]
        rzuty_bez_startu = winner_rzuty[1:]

        total_lotki = 0
        for rz in rzuty_bez_startu:
            if rz["score"] < 0:
                total_lotki += -rz["score"]
                break
            else:
                total_lotki += 3
            if rz["left"] == 0:
                break

        if total_lotki <= 18:
            players_fast_legs[winner_name].append(total_lotki)

    return players_fast_legs

def calculate_high_finishes(match_detail):
    player_names = [p["name"] for p in match_detail["statsData"]]
    players_high_finishes = {name: [] for name in player_names}

    for leg in match_detail["legData"]:
        winner_index = leg["winner"]
        winner_name = match_detail["statsData"][winner_index]["name"]
        winner_rzuty = leg["playerData"][winner_index]

        for j, rz in enumerate(winner_rzuty):
            if rz["left"] == 0 and rz["score"] < 0:
                if j > 0:
                    finish_value = winner_rzuty[j - 1]["left"]
                    if finish_value >= 100:
                        players_high_finishes[winner_name].append(finish_value)
                break

    return players_high_finishes

def calculate_maxes(match_detail):
    players_max = {p["name"]: [] for p in match_detail["statsData"]}

    for leg in match_detail["legData"]:
        for p_index, p_data in enumerate(leg["playerData"]):
            player_name = match_detail["statsData"][p_index]["name"]
            for rz in p_data:
                if rz["score"] == 180:
                    players_max[player_name].append(180)

    return players_max

def calculate_high_scores(match_detail):
    player_names = [p["name"] for p in match_detail["statsData"]]
    players_scores = {name: [] for name in player_names}

    for leg in match_detail["legData"]:
        for p_index, p_data in enumerate(leg["playerData"]):
            player_name = match_detail["statsData"][p_index]["name"]
            for rz in p_data:
                if 170 <= rz["score"] < 180:
                    players_scores[player_name].append(rz["score"])

    return players_scores


# ============================================================
# PRZETWARZANIE JEDNEGO TURNIEJU
# ============================================================

def process_tournament(tournament):
    tournament_id = tournament["tournament_id"]
    tournament_name = tournament["name"]
    category = tournament["category"]

    print(f"\n{'='*60}")
    print(f"🏆 Turniej: {tournament_name} (ID: {tournament_id})")
    print(f"📂 Kategoria: {category}")
    print(f"{'='*60}")

    # Pobierz wszystkie mecze turnieju
    matches = []
    skip = 0
    while True:
        batch = get_matches(tournament_id, skip)
        if not batch:
            break
        matches.extend(batch)
        skip += MATCHES_PER_REQUEST

    print(f"Znaleziono {len(matches)} meczów")

    fast_results = []
    high_results = []
    max_results = []
    scores_results = []

    for idx, match in enumerate(matches, start=1):
        tmid = match["tmid"]

        if tmid in EXCLUDED_MATCHES:
            print(f"⏭️  Pomijam wykluczony mecz: {tmid}")
            continue

        try:
            match_detail = get_match_detail(tmid)
        except Exception as e:
            print(f"❌ Błąd przy meczu {tmid}: {e}")
            continue

        player1 = match_detail["statsData"][0]["name"]
        player2 = match_detail["statsData"][1]["name"]
        score = f"{match['p1winLegs']}:{match['p2winLegs']}"

        avg1 = match_detail["statsData"][0]["allScore"] * 3 / match_detail["statsData"][0]["allDarts"]
        avg2 = match_detail["statsData"][1]["allScore"] * 3 / match_detail["statsData"][1]["allDarts"]

        players_fast   = calculate_fast_legs(match_detail)
        players_high   = calculate_high_finishes(match_detail)
        players_max    = calculate_maxes(match_detail)
        players_scores = calculate_high_scores(match_detail)

        print(f"\nMecz {idx}/{len(matches)}: {player1} vs {player2} — wynik {score} (śr. {avg1:.2f} – {avg2:.2f})")
        for player, vals in players_fast.items():
            if vals:
                print(f"  ⚡ {player} — szybkie lotki: {sorted(vals)} ({len(vals)})")
        for player, vals in players_high.items():
            if vals:
                print(f"  🎯 {player} — wysokie zakończenia: {sorted(vals)} ({len(vals)})")
        for player, vals in players_max.items():
            if vals:
                print(f"  💥 {player} — maksymalne rzuty (180): {len(vals)}")
        for player, vals in players_scores.items():
            if vals:
                print(f"  🔥 {player} — rzuty 170–179: {sorted(vals)} ({len(vals)})")
        print("-" * 60)

        # Wspólne pola dla każdego wpisu — dodajemy tournament_name i category
        base = {
            "tmid": tmid,
            "tournament": tournament_name,   # ← skąd pochodzi mecz
            "category": category,            # ← kategoria turnieju
            "title": match["title"],
            "player1": player1,
            "player2": player2,
            "score": score,
        }

        fast_results.append({
            **base,
            "fast_legs_count": {player1: len(players_fast[player1]), player2: len(players_fast[player2])},
            "fast_legs": {player1: sorted(players_fast[player1]), player2: sorted(players_fast[player2])},
            "average": {player1: round(avg1, 2), player2: round(avg2, 2)}
        })
        high_results.append({
            **base,
            "high_finishes_count": {player1: len(players_high[player1]), player2: len(players_high[player2])},
            "high_finishes": {player1: sorted(players_high[player1]), player2: sorted(players_high[player2])}
        })
        max_results.append({
            **base,
            "max_count": {player1: len(players_max[player1]), player2: len(players_max[player2])},
            "maxes": {player1: players_max[player1], player2: players_max[player2]}
        })
        scores_results.append({
            **base,
            "scores_count": {player1: len(players_scores[player1]), player2: len(players_scores[player2])},
            "scores": {player1: sorted(players_scores[player1]), player2: sorted(players_scores[player2])}
        })

    return fast_results, high_results, max_results, scores_results


# ============================================================
# ZAPIS DO PLIKÓW
# ============================================================

def save_results(season_id, all_fast, all_high, all_max, all_scores):
    output_dir = os.path.join("output", "seasons", season_id, "tournaments")
    os.makedirs(output_dir, exist_ok=True)

    files = {
        "tournaments_fast_legs.json": all_fast,
        "tournaments_high_finishes.json": all_high,
        "tournaments_max.json": all_max,
        "tournaments_high_scores.json": all_scores,
    }

    for filename, data in files.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Zapisano {len(data)} rekordów → {path}")


# ============================================================
# MAIN
# ============================================================

def main():
    active_season = load_active_season()
    season_id = active_season["id"]
    print(f"🗓️  Aktywny sezon: {active_season['label']} ({season_id})")

    tournaments = TOURNAMENTS_BY_SEASON.get(season_id, [])
    if not tournaments:
        raise RuntimeError(
            f"Brak turniejów zdefiniowanych dla sezonu '{season_id}' w TOURNAMENTS_BY_SEASON. "
            f"Dopisz je w n01_parsers_tournaments.py."
        )

    all_fast   = []
    all_high   = []
    all_max    = []
    all_scores = []

    for tournament in tournaments:
        fast, high, max_, scores = process_tournament(tournament)
        all_fast.extend(fast)
        all_high.extend(high)
        all_max.extend(max_)
        all_scores.extend(scores)

    print(f"\n{'='*60}")
    print(f"📊 Łącznie przetworzono meczów: {len(all_fast)}")
    print(f"{'='*60}")

    save_results(season_id, all_fast, all_high, all_max, all_scores)

    print("\n🏆 Wszystkie turnieje przetworzone!")

if __name__ == "__main__":
    main()