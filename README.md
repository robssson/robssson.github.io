# n01 Darts Parser

This project fetches and processes match data for two dart leagues (I Liga and II Liga) and for standalone tournaments (Szerszeń Cup, Superpuchar Klubu, Openy). It calculates various statistics from the matches and stores the results in JSON files, organized per season.

## Project Structure

```
n01-parser
├── output
│   ├── seasons.json          # manifest listing all seasons (id, label, active flag, tournament ids)
│   └── seasons
│       ├── jesien2026         # id must match seasons.json entry
│       │   ├── liga1
│       │   │   ├── liga1_fast_legs.json
│       │   │   ├── liga1_high_finishes.json
│       │   │   ├── liga1_max.json
│       │   │   └── liga1_high_scores.json
│       │   ├── liga2
│       │   │   ├── liga2_fast_legs.json
│       │   │   ├── liga2_high_finishes.json
│       │   │   ├── liga2_max.json
│       │   │   └── liga2_high_scores.json
│       │   └── tournaments
│       │       ├── tournaments_fast_legs.json
│       │       ├── tournaments_high_finishes.json
│       │       ├── tournaments_max.json
│       │       └── tournaments_high_scores.json
│       └── wiosna2026         # archived past season, same file layout
│           ├── liga1/...
│           ├── liga2/...
│           └── tournaments/...
├── n01_parser.py               # scrapes I/II Liga into the active season
├── n01_parsers_tournaments.py   # scrapes standalone tournaments into the active season
├── turnieje_archiwum_<season_id>.html  # static snapshot of a finished season's tournament cards
├── requirements.txt
└── README.md
```

## Seasons (`output/seasons.json`)

Each season is one entry in this manifest:

```json
{ "id": "jesien2026", "label": "Jesień 2026", "active": true, "liga1_tid": "t_XXXX", "liga2_tid": "t_YYYY" }
```

- Exactly one season must have `"active": true` — that's the season `n01_parser.py` / `n01_parsers_tournaments.py` scrape into, and the one `liga.html` / `statystyki_turniejow.html` / `index.html` show by default.
- `liga1_tid` / `liga2_tid` are the Nakka tournament IDs (from the tournament URL) for that season's leagues. Set them once the new season's tournament pages exist.
- The standalone tournament list (Szerszeń Cup, Superpuchar Klubu, Openy) is **not** in `seasons.json` — it lives in `TOURNAMENTS_BY_SEASON` inside `n01_parsers_tournaments.py`, keyed by the same season `id`. Add each new tournament's `tournament_id` there as it's created.
- Starting a new season:
  1. Add a new entry to `seasons.json` with `active: true`, flip the previous season's `active` to `false`, and fill in its `liga1_tid`/`liga2_tid` once known.
  2. Add the new season's tournaments to `TOURNAMENTS_BY_SEASON` in `n01_parsers_tournaments.py` as they're created.
  3. Run `python n01_parser.py` and `python n01_parsers_tournaments.py`.
  4. Old seasons keep their data untouched under `output/seasons/<old_id>/` and remain browsable via the season dropdown on the Liga / Statystyki Turniejowe pages.
  5. For `turnieje.html` (hand-written tournament cards, not JSON-driven): copy the finished season's cards into a new static `turnieje_archiwum_<old_id>.html` page, then clear `turnieje.html`'s "Nadchodzące"/"Archiwum" sections for the new season and link to the archive page (see `turnieje_archiwum_wiosna2026.html` as an example).

## Output Files

For the active season's `liga1`/`liga2` folders under `output/seasons/<season_id>/`:

- **liga1_fast_legs.json**: Results of fast legs (≤18 darts) for matches in the I Liga.
- **liga1_high_finishes.json**: High finishes (100+ points) for matches in the I Liga.
- **liga1_max.json**: Maximum scores (180) achieved by players in the I Liga.
- **liga1_high_scores.json**: Scores between 170 and 179 (excluding 180) for matches in the I Liga.
- (same four files, `liga2_*`, for the II Liga)

## Requirements

To run this project, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

## Running the Project

To fetch league match data and generate the league output files, run:

```
python n01_parser.py
```

To fetch standalone tournament match data (Szerszeń Cup, Superpuchar Klubu, Openy), run:

```
python n01_parsers_tournaments.py
```

Both scripts read the active season from `output/seasons.json` and write into `output/seasons/<active_id>/`.


## License

This project is open-source and available for use and modification.