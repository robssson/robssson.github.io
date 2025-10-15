import json
from collections import defaultdict
from tabulate import tabulate

INPUT_FILE = "tournament_high_finishes.json"

def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Nie znaleziono pliku {INPUT_FILE}. Uruchom najpierw skrypt z analizą turnieju.")
        return

    player_finishes = defaultdict(list)

    # Przetwarzamy każdy mecz
    for match in data:
        for player, finishes in match.get("high_finishes", {}).items():
            if finishes:
                player_finishes[player].extend(finishes)

    if not player_finishes:
        print("Brak danych o wysokich zakończeniach w pliku.")
        return

    # Sortowanie po liczbie high finish (malejąco), a potem alfabetycznie
    sorted_players = sorted(
        player_finishes.items(),
        key=lambda x: (-len(x[1]), x[0])
    )

    # Tworzymy dane do tabeli
    table_data = []
    for player, finishes in sorted_players:
        finishes_sorted = sorted(finishes)
        table_data.append([
            player,
            len(finishes_sorted),
            ", ".join(map(str, finishes_sorted))
        ])

    # Wypisanie ładnej tabeli
    print("\n🎯 ZESTAWIENIE WYSOKICH ZAKOŃCZEŃ 🎯\n")
    print(tabulate(
        table_data,
        headers=["Zawodnik", "Liczba wysokich zakończeń", "Wartości zakończeń (≥100)"],
        tablefmt="fancy_grid",
        stralign="center",
    ))

    print("\n✅ Gotowe!")

if __name__ == "__main__":
    main()
