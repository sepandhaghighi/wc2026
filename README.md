# World Cup 2026 Match Prediction Benchmark: Evaluating Large Language Models

This project benchmarks Large Language Models (LLMs) on FIFA World Cup 2026 match prediction tasks.

Each model receives the same information, including recent international results, FIFA rankings, confederation data, tournament stage, and host country. Predictions are generated through [Cloudflare Workers AI](https://www.cloudflare.com/products/workers-ai/) and stored together with their complete inference sessions for reproducibility and later analysis.

## Getting Started

### Requirements

- Python 3.10+
- A [Cloudflare Workers AI](https://www.cloudflare.com/products/workers-ai/) account

### Installation

```bash
git clone https://github.com/sepandhaghighi/wc2026.git
cd wc2026
pip install -r requirements.txt
```

### Configuration

Set your Cloudflare credentials:

```bash
export CLOUDFLARE_ACCOUNT_ID="your_account_id"
export CLOUDFLARE_API_KEY="your_api_token"
```

## Supported Models

The benchmark currently evaluates the following models:

- `openai/gpt-oss-20b`
- `openai/gpt-oss-120b`
- `qwen/qwen3-30b-a3b-fp8`
- `aisingapore/gemma-sea-lion-v4-27b-it`
- `mistralai/mistral-small-3.1-24b-instruct`
- `meta/llama-3.1-8b-instruct-fast`
- `meta/llama-4-scout-17b-16e-instruct`
- `meta/llama-3.2-3b-instruct`

Additional Workers AI models can be added by extending `MODEL_LIST` in `params.py`.

## Features

This project plays out one match at a time, asking a handful of language models to predict each result. Every model sees the same prompt and the same data, so their predictions line up cleanly for comparison. To keep that reasoning grounded, each team's recent form is drawn from real international match history and paired with its FIFA ranking and confederation. The models' answers are saved alongside the full conversation that produced them, so every prediction stays easy to analyze and trace back.

- ⚽ Supports both group-stage and knockout-stage matches
- 🤖 Evaluates multiple LLMs under identical conditions
- 📈 Uses recent international match history to estimate team form
- 🏆 Incorporates FIFA rankings and confederation information
- 🌎 Includes host-country context
- 🧾 Produces structured JSON predictions
- 💾 Stores complete Memor sessions for reproducibility
- 🔁 Allows repeated experiments with different models and matches

## Prediction Schema

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

## Running a Benchmark

Configure the match in `main.py`.

```python
current_phase = Phase.GROUP.value

country_a = Team.CZECH_REPUBLIC.value
country_b = Team.MEXICO.value

match_host = Host.MEXICO.value

raw_match_id = "WC2026-M54"
```

Run the benchmark:

```bash
python main.py
```

The script downloads historical international results, computes team form statistics, queries each configured model, and saves both predictions and inference sessions.


## Project Structure

The main file is `main.py`, with the team list in a JSON file and all results collected under `data/`.

When you run the benchmark, it fills in `data/`. Results are grouped first by model and then by match, so it's easy to find a single prediction or compare the same match across models:

```text
.
├── main.py                       # the script that runs the benchmark
├── params.py                     # constants, enums, global paths
├── utils.py                      # functions
├── data/                         # data
│   ├── wc_2026_teams.json        # team names, FIFA rankings, and confederations
│   ├── predictions/
│   │   └── <model_name>/
│   │       └── <match_id>.json   # what the model predicted
│   └── sessions/
│       └── <model_name>/
│           └── <match_id>.json   # the prompt and reply that produced it
└── README.md
```

## Disclaimer

This project is intended for benchmarking and experimentation purposes.

LLMs do not possess predictive knowledge of future sporting events, and generated forecasts should not be interpreted as betting advice or as statistically validated outcome probabilities.


## References

1. [FIFA Men's World Ranking](https://inside.fifa.com/fifa-world-ranking/men?dateId=FRS_Male_Football_20260401)
2. [International Football Results](https://github.com/martj42/international_results)
3. [FIFA WC2026 Simulation](https://github.com/zvizdo/fifa-wc-2026-simulation)