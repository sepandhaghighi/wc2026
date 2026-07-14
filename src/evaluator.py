import json
from pathlib import Path
import pandas as pd
from metrics import evaluate_prediction


PREDICTIONS_DIR = Path("data/predictions")
MATCHES_PATH = Path("data/matches.json")
EVALUATION_DIR = Path("data/evaluation")


def load_ground_truth() -> dict:
    """
    Loads the official World Cup match results.

    :return: Dictionary indexed by match ID.
    """
    with open(MATCHES_PATH, encoding="utf-8") as file:
        matches = json.load(file)

    ground_truth = {}

    for match_id, match_data in matches.items():

        ground_truth[match_id] = {
            "phase": match_data["phase"],
            "score": match_data["score"]
        }

    return ground_truth


def aggregate_metrics(metric_rows: list) -> dict:
    """
    Aggregates match-level metrics into model-level benchmark statistics.

    :param metric_rows: List of evaluated match metrics.
    :return: Dictionary containing averaged benchmark metrics.
    """
    frame = pd.DataFrame(metric_rows)

    return {
        "matches": len(frame),
        "exact_score_accuracy": frame["exact_score_accuracy"].mean(),
        "goal_mae": frame["goal_mae"].mean(),
        "goal_difference_mae": frame["goal_difference_mae"].mean(),
        "outcome_accuracy": frame["outcome_accuracy"].mean(),
        "brier_score": frame["brier_score"].mean(),
        "log_loss": frame["log_loss"].mean(),
    }


def create_leaderboard(metrics: dict) -> str:
    """
    Creates a markdown leaderboard summarizing model performance.

    :param metrics: Aggregated model metrics.
    :return: Markdown leaderboard.
    """
    rows = []

    for model, values in metrics.items():

        rows.append(
            (
                model,
                values["outcome_accuracy"],
                values["exact_score_accuracy"],
                values["goal_mae"],
                values["goal_difference_mae"],
                values["brier_score"],
                values["log_loss"],
            )
        )

    rows.sort(
        key=lambda item: (
            -item[1],
            -item[2],
            item[3],
            item[4],
            item[5],
            item[6],
        )
    )

    markdown = []

    markdown.append("# World Cup 2026 Benchmark Results")
    markdown.append("")
    markdown.append("| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |")
    markdown.append("|-------|----------:|--------:|-----------:|----------:|---------:|----------:|")

    for row in rows:

        markdown.append(
            "| {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.4f} | {:.4f} |".format(
                *row
            )
        )

    return "\n".join(markdown)


if __name__ == "__main__":

    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    ground_truth = load_ground_truth()

    per_match_rows = []

    model_results = {}

    prediction_files = sorted(PREDICTIONS_DIR.rglob("*.json"))

    if len(prediction_files) == 0:
        raise RuntimeError("No prediction files found.")

    for prediction_file in prediction_files:

        with open(prediction_file, encoding="utf-8") as file:
            prediction = json.load(file)

        match_id = prediction["match_id"]

        if match_id not in ground_truth:
            print(f"[WARNING] Match '{match_id}' missing from official results.")
            continue

        official = ground_truth[match_id]

        model = prediction["simulation_env"]["model"]

        metrics = evaluate_prediction(
            phase=official["phase"],
            true_score=official["score"],
            predicted_score=prediction["prediction"]["predicted_score"],
            probabilities=prediction["prediction"]["probabilities"],
        )

        metrics["match_id"] = match_id
        metrics["model"] = model

        per_match_rows.append(metrics)

        model_results.setdefault(model, []).append(metrics)

    aggregated = {}

    for model, rows in model_results.items():

        aggregated[model] = aggregate_metrics(rows)

    with open(EVALUATION_DIR / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(aggregated, file, indent=4, ensure_ascii=False)

    pd.DataFrame(per_match_rows).to_csv(EVALUATION_DIR / "per_match.csv", index=False)

    leaderboard = create_leaderboard(aggregated)

    with open(EVALUATION_DIR / "leaderboard.md", "w", encoding="utf-8") as file:
        file.write(leaderboard)

    print(f"[SUCCESS] Evaluation completed for {len(model_results)} models.")