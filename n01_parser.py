import requests
import json
import time
import os

LEAGUES = [
    {
        "name": "I Liga",
        "tournament_id": "t_L01x_7216",  
        "prefix": "liga1"
    },
    {
        "name": "II Liga",
        "tournament_id": "t_2y14_1402", 
        "prefix": "liga2"
    }
]

MATCHES_PER_REQUEST = 30

# Mecze do pominięcia (np. niedokończone) — podaj tmid
EXCLUDED_MATCHES = {
    "t_2y14_1402_lg_0_al5c_LPSX_tJLk",  # niedokończony
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_MATCH_LIST_URL = "https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_history.php"
BASE_MATCH_VIEW_URL = "https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_user_t.php?cmd=match_view&sid="

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

def calculate_fast_legs(match_detail):
    player_names = [player["name"] for player in match_detail["statsData"]]

    players_fast_legs = {match_detail["statsData"][0]["name"]: [],
                         match_detail["statsData"][1]["name"]: []}
    leg_results = []

    for idx, leg in enumerate(match_detail["legData"], start=1):
        leg_summary = {"leg": idx, "winner": None, "fast_legs": {}}

        winner_index = leg["winner"]
        winner_name = match_detail["statsData"][winner_index]["name"]
        leg_summary["winner"] = winner_name

        order = [0, 1] if leg["first"] == 0 else [1, 0]

        for i, player_index in enumerate(order):
            if player_index == winner_index:
                winner_rzuty = leg["playerData"][winner_index]
                break

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
            leg_summary["fast_legs"][winner_name] = total_lotki

        leg_results.append(leg_summary)

    return players_fast_legs, leg_results

def calculate_high_finishes(match_detail):
    player_names = [p["name"] for p in match_detail["statsData"]]

    players_high_finishes = {name: [] for name in player_names}
    leg_results = []

    for idx, leg in enumerate(match_detail["legData"], start=1):
        leg_summary = {"leg": idx, "winner": None, "high_finish": {}}

        winner_index = leg["winner"]
        winner_name = match_detail["statsData"][winner_index]["name"]
        leg_summary["winner"] = winner_name

        order = [0, 1] if leg["first"] == 0 else [1, 0]

        for i, player_index in enumerate(order):
            if player_index == winner_index:
                winner_rzuty = leg["playerData"][winner_index]
                break

        for j, rz in enumerate(winner_rzuty):
            if rz["left"] == 0 and rz["score"] < 0:
                if j > 0:
                    previous = winner_rzuty[j - 1]
                    finish_value = previous["left"]
                    if finish_value >= 100:
                        players_high_finishes[winner_name].append(finish_value)
                        leg_summary["high_finish"][winner_name] = finish_value
                break

        leg_results.append(leg_summary)

    return players_high_finishes, leg_results

def calculate_maxes(match_detail):
    player_names = [p["name"] for p in match_detail["statsData"]]

    players_max = {p["name"]: [] for p in match_detail["statsData"]}
    leg_results = []

    for idx, leg in enumerate(match_detail["legData"], start=1):
        leg_summary = {"leg": idx, "maxes": {}}
        for p_index, p_data in enumerate(leg["playerData"]):
            player_name = match_detail["statsData"][p_index]["name"]
            for rz in p_data:
                if rz["score"] == 180:
                    players_max[player_name].append(180)
                    leg_summary["maxes"].setdefault(player_name, 0)
                    leg_summary["maxes"][player_name] += 1
        leg_results.append(leg_summary)

    return players_max, leg_results

def calculate_high_scores(match_detail):
    player_names = [p["name"] for p in match_detail["statsData"]]

    players_scores = {name: [] for name in player_names}

    for idx, leg in enumerate(match_detail["legData"], start=1):
        for p_index, p_data in enumerate(leg["playerData"]):
            player_name = match_detail["statsData"][p_index]["name"]
            for rz in p_data:
                if 170 <= rz["score"] < 180:
                    players_scores[player_name].append(rz["score"])

    return players_scores, []

def process_league(league):
    tournament_id = league["tournament_id"]
    prefix = league["prefix"]
    league_name = league["name"]
    
    print(f"\n{'='*60}")
    print(f"📋 Przetwarzanie: {league_name} (ID: {tournament_id})")
    print(f"{'='*60}")
    
    all_fast_results = []
    all_high_results = []
    all_max_results = []
    all_scores_results = []
    skip = 0
    matches = []

    while True:
        batch = get_matches(tournament_id, skip)
        if not batch:
            break
        matches.extend(batch)
        skip += MATCHES_PER_REQUEST

    print(f"Znaleziono {len(matches)} meczów w {league_name}")

    for idx, match in enumerate(matches, start=1):
        tmid = match["tmid"]
        if tmid in EXCLUDED_MATCHES:
            print(f"⏭️  Pomijam wykluczony mecz: {tmid}")
            continue
        try:
            match_detail = get_match_detail(tmid)
        except Exception as e:
            print(f"Błąd przy meczu {tmid}: {e}")
            continue
        
        player1 = match_detail["statsData"][0]["name"]
        player2 = match_detail["statsData"][1]["name"]
        
        players_fast_legs, _ = calculate_fast_legs(match_detail)
        players_high_finishes, _ = calculate_high_finishes(match_detail)
        players_max, _ = calculate_maxes(match_detail)
        players_scores, _ = calculate_high_scores(match_detail)
  
        score = f"{match['p1winLegs']}:{match['p2winLegs']}"
        avg1 = match_detail["statsData"][0]["allScore"] * 3 / match_detail["statsData"][0]["allDarts"]
        avg2 = match_detail["statsData"][1]["allScore"] * 3 / match_detail["statsData"][1]["allDarts"]

        summary_fast = {
            "tmid": tmid, "title": match["title"],
            "player1": player1, "player2": player2, "score": score,
            "fast_legs_count": {player1: len(players_fast_legs[player1]), player2: len(players_fast_legs[player2])},
            "fast_legs": {player1: sorted(players_fast_legs[player1]), player2: sorted(players_fast_legs[player2])},
            "average": {player1: avg1, player2: avg2}
        }
        summary_high = {
            "tmid": tmid, "title": match["title"],
            "player1": player1, "player2": player2, "score": score,
            "high_finishes_count": {player1: len(players_high_finishes[player1]), player2: len(players_high_finishes[player2])},
            "high_finishes": {player1: sorted(players_high_finishes[player1]), player2: sorted(players_high_finishes[player2])}
        }
        summary_max = {
            "tmid": tmid, "title": match["title"],
            "player1": player1, "player2": player2, "score": score,
            "max_count": {player1: len(players_max[player1]), player2: len(players_max[player2])},
            "maxes": {player1: players_max[player1], player2: players_max[player2]}
        }
        summary_scores = {
            "tmid": tmid, "title": match["title"],
            "player1": player1, "player2": player2, "score": score,
            "scores_count": {player1: len(players_scores[player1]), player2: len(players_scores[player2])},
            "scores": {player1: sorted(players_scores[player1]), player2: sorted(players_scores[player2])}
        }

        all_fast_results.append(summary_fast)
        all_high_results.append(summary_high)
        all_max_results.append(summary_max)
        all_scores_results.append(summary_scores)

        print(f"\nMecz {idx}/{len(matches)}: {player1} vs {player2} — wynik {score} (śr. {avg1:.2f} – {avg2:.2f})")
        for player, vals in players_fast_legs.items():
            if vals:
                print(f"  ⚡ {player} — szybkie lotki: {sorted(vals)} ({len(vals)})")
        for player, vals in players_high_finishes.items():
            if vals:
                print(f"  🎯 {player} — wysokie zakończenia: {sorted(vals)} ({len(vals)})")
        for player, vals in players_max.items():
            if vals:
                print(f"  💥 {player} — maksymalne rzuty (180): {len(vals)}")
        for player, vals in players_scores.items():
            if vals:
                print(f"  🔥 {player} — rzuty 170–179: {sorted(vals)} ({len(vals)})")
        print("-" * 60)
        time.sleep(0.2)

    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    league_output_dir = os.path.join(output_dir, prefix)
    if not os.path.exists(league_output_dir):
        os.makedirs(league_output_dir)

    with open(os.path.join(league_output_dir, f"{prefix}_fast_legs.json"), "w", encoding="utf-8") as f:
        json.dump(all_fast_results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(league_output_dir, f"{prefix}_high_finishes.json"), "w", encoding="utf-8") as f:
        json.dump(all_high_results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(league_output_dir, f"{prefix}_max.json"), "w", encoding="utf-8") as f:
        json.dump(all_max_results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(league_output_dir, f"{prefix}_high_scores.json"), "w", encoding="utf-8") as f:
        json.dump(all_scores_results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {league_name} — przetwarzanie zakończone!")

def main():
    for league in LEAGUES:
        process_league(league)
    print("\n🏆 Wszystkie ligi przetworzone!")

if __name__ == "__main__":
    main()