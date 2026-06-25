# World Cup 2026 Match Prediction Benchmark: Evaluating Large Language Models

This project benchmarks Large Language Models (LLMs) on FIFA World Cup 2026 match prediction tasks.

Each model receives the same information, including recent international results, FIFA rankings, confederation data, tournament stage, and host country. Predictions are generated through Cloudflare Workers AI and stored together with their complete inference sessions for reproducibility and later analysis.

## Getting Started

You'll need Python 3.10+ and a [Cloudflare Workers AI](https://www.cloudflare.com/products/workers-ai/) account.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then add your Cloudflare credentials to the environment:

```bash
export CLOUDFLARE_ACCOUNT_ID="your_account_id"
export CLOUDFLARE_API_KEY="your_api_token"
```

## Supported Models

- OpenAI GPT-OSS 20B
- OpenAI GPT-OSS 120B
- Qwen 3 30B A3B
- Gemma SEA-Lion V4 27B
- Mistral Small 3.1 24B
- Llama 3.1 8B
- Llama 3.2 3B
- Llama 4 Scout 17B

## Features

This project plays out one match at a time, asking a handful of language models to predict each result. Every model sees the same prompt and the same data, so their predictions line up cleanly for comparison. To keep that reasoning grounded, each team's recent form is drawn from real international match history and paired with its FIFA ranking and confederation. The models' answers are saved alongside the full conversation that produced them, so every prediction stays easy to analyze and trace back.

In short, it:

- ⚽ Covers both the group stage and the knockout rounds
- 🤖 Benchmarks several models on equal footing
- 📈 Grounds each prediction in real form, rankings, and confederation data
- 🧾 Returns clean JSON and keeps the session that created it

Every model is asked to answer in the same JSON shape, which is what ends up in each prediction file. The fields differ slightly between the two stages: group-stage matches can end in a draw, while knockout matches always resolve to a single team advancing.

### Group Stage

```json
{
  "probabilities": {
    "team_a_win": 0.0,
    "draw": 0.0,
    "team_b_win": 0.0
  },
  "predicted_score": "2-1",
  "predicted_winner": "Team A",
  "knockout_resolution": {
    "ended_in_extra_time": false,
    "ended_in_penalties": false,
    "penalty_shootout_score": null
  },
  "confidence": 0.0
}
```

### Knockout Stage

```json
{
  "probabilities": {
    "team_a_advance": 0.0,
    "team_b_advance": 0.0
  },
  "predicted_score": "1-1",
  "predicted_winner": "Team A",
  "knockout_resolution": {
    "ended_in_extra_time": true,
    "ended_in_penalties": false,
    "penalty_shootout_score": null
  },
  "confidence": 0.0
}
```

Each run saves two files: a **prediction** file with the match metadata, model, hyperparameters, prediction JSON, and timestamp; and a **session** file holding the full prompt history and response as a reproducible Memor session.

## Project Structure

The main file is `main.py`, with the team list in a JSON file and all results collected under `data/`:

```text
.
├── main.py               # the script that runs the benchmark
├── params.py             # constants, enums, global paths
├── utils.py              # functions
├── wc_2026_teams.json    # team names, FIFA rankings, and confederations
├── data/                 # everything the runs produce (created automatically)
└── README.md
```

When you run the benchmark, it fills in `data/`. Results are grouped first by model and then by match, so it's easy to find a single prediction or compare the same match across models:

```text
data/
├── predictions/
│   └── <model_name>/
│       └── <match_id>.json    # what the model predicted
└── sessions/
    └── <model_name>/
        └── <match_id>.json    # the prompt and reply that produced it
```

## References

1. [FIFA Men's World Ranking](https://inside.fifa.com/fifa-world-ranking/men?dateId=FRS_Male_Football_20260401)
2. [International Football Results](https://github.com/martj42/international_results)
3. [FIFA WC2026 Simulation](https://github.com/zvizdo/fifa-wc-2026-simulation)