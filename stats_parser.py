import json
from tabulate import tabulate

# ---- KONFIGURACJA ----
INPUT_FILE = "tournament_fast_legs.json"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    fast_legs_total = {}
    fast_legs_numbers = {}

    for match in data:
        for player, legs in match.get("fast_legs", {}).items():
            if not legs:
                continue  # pomijamy graczy bez szybkich lotek
            if player not in fast_legs_total:
                fast_legs_total[player] = 0
                fast_legs_numbers[player] = []
            fast_legs_total[player] += len(legs)
            fast_legs_numbers[player].extend(legs)

    # Przygotowanie danych do tabeli
    table_data = []
    for player in sorted(fast_legs_total.keys(), key=lambda x: fast_legs_total[x], reverse=True):
        legs_sorted = sorted(fast_legs_numbers[player])
        table_data.append([player, fast_legs_total[player], ", ".join(map(str, legs_sorted))])

    # Wypisanie w tabeli
    print("\n📊 Podsumowanie szybkich lotek per gracz:\n")
    print(tabulate(
        table_data,
        headers=["Zawodnik", "Liczba szybkich lotek", "Szybkie legi (lotki)"],
        tablefmt="fancy_grid",
        stralign="center",
    ))

if __name__ == "__main__":
    main()
