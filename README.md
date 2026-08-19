# n01 Darts Parser

This project is a Python script that fetches and processes match data for two dart leagues: I Liga and II Liga. It calculates various statistics from the matches and stores the results in JSON files, organized per season.

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
│       │   └── liga2
│       │       ├── liga2_fast_legs.json
│       │       ├── liga2_high_finishes.json
│       │       ├── liga2_max.json
│       │       └── liga2_high_scores.json
│       └── wiosna2026         # archived past season, same file layout
│           ├── liga1/...
│           └── liga2/...
├── n01_parser.py
├── requirements.txt
└── README.md
```

## Seasons (`output/seasons.json`)

Each season is one entry in this manifest:

```json
{ "id": "jesien2026", "label": "Jesień 2026", "active": true, "liga1_tid": "t_XXXX", "liga2_tid": "t_YYYY" }
```

- Exactly one season must have `"active": true` — that's the season `n01_parser.py` scrapes into, and the one `liga.html`/`index.html` show by default.
- `liga1_tid` / `liga2_tid` are the Nakka tournament IDs (from the tournament URL) for that season's leagues. Set them once the new season's tournament pages exist.
- Starting a new season: add a new entry with `active: true`, flip the previous season's `active` to `false`, fill in its tournament IDs, then run the parser. Old seasons keep their data untouched under `output/seasons/<old_id>/` and remain browsable via the season dropdown on the Liga page.

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


To execute the script and generate the output files, run:

```
python n01_parser.py
```

This will fetch the match data, process it, and create the output files in the `output` directory.

## License

This project is open-source and available for use and modification.