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


def build_leaderboard_table(
    title: str,
    data: dict,
    include_probability_metrics: bool = True
) -> list:
    """
    Builds a markdown table section for leaderboard output.

    :param title: Section title.
    :param data: Metrics grouped by model.
    :param include_probability_metrics: Whether to include Brier and LogLoss.
    :return: List of markdown lines.
    """

    rows = []

    for model, values in data.items():

        row = (
            model,
            values["outcome_accuracy"],
            values["exact_score_accuracy"],
            values["goal_mae"],
            values["goal_difference_mae"],
        )

        if include_probability_metrics:
            row += (values["brier_score"], values["log_loss"])
        rows.append(row)

    rows.sort(
        key=lambda item: (
            -item[1],
            -item[2],
            item[3],
            item[4],
        )
    )

    markdown = []

    markdown.append(f"## {title}")
    markdown.append("")

    if include_probability_metrics:

        markdown.append("| Model | Outcome | Exact | Goal MAE | GD MAE | Brier | LogLoss |")
        markdown.append("|-------|----------:|--------:|-----------:|----------:|---------:|----------:|")

        for row in rows:
            markdown.append("| {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.4f} | {:.4f} |".format(*row))

    else:

        markdown.append("| Model | Outcome | Exact | Goal MAE | GD MAE |")
        markdown.append("|-------|----------:|--------:|-----------:|----------:|")

        for row in rows:
            markdown.append("| {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} |".format(*row))

    markdown.append("")

    return markdown


def create_leaderboard(metrics: dict) -> str:
    """
    Creates markdown leaderboard separated by tournament stages.

    :param metrics: Aggregated metrics by stage.
    :return: Markdown leaderboard.
    """

    markdown = []

    markdown.append("# World Cup 2026 Benchmark Results")
    markdown.append("")

    markdown.extend(
        build_leaderboard_table(
            "1. Group Stage",
            metrics["group"],
            include_probability_metrics=True,
        )
    )

    markdown.extend(
        build_leaderboard_table(
            "2. Knockout Stage",
            metrics["knockout"],
            include_probability_metrics=True,
        )
    )

    markdown.extend(
        build_leaderboard_table(
            "3. Overall",
            metrics["overall"],
            include_probability_metrics=True,
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

        try:
            metrics = evaluate_prediction(
                phase=official["phase"],
                true_score=official["score"],
                predicted_score=prediction["prediction"]["predicted_score"],
                probabilities=prediction["prediction"]["probabilities"],
            )
        except Exception as exc:
            print(f"[WARNING] Failed to evaluate Match ID '{match_id}' for model '{model}'. Evaluation skipped. Reason: {exc}")
            continue

        metrics["match_id"] = match_id
        metrics["model"] = model

        per_match_rows.append(metrics)

        model_results.setdefault(model, []).append(metrics)

    aggregated = {
        "group": {},
        "knockout": {},
        "overall": {},
    }


    for model, rows in model_results.items():

        group_rows = [
            row for row in rows
            if row["match_id"] in ground_truth
            and ground_truth[row["match_id"]]["phase"] == "group"
        ]

        knockout_rows = [
            row for row in rows
            if row["match_id"] in ground_truth
            and ground_truth[row["match_id"]]["phase"] != "group"
        ]

        aggregated["group"][model] = aggregate_metrics(group_rows)

        aggregated["knockout"][model] = aggregate_metrics(knockout_rows)

        aggregated["overall"][model] = aggregate_metrics(rows)

    with open(EVALUATION_DIR / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(aggregated, file, indent=4, ensure_ascii=False)

    pd.DataFrame(per_match_rows).to_csv(EVALUATION_DIR / "per_match.csv", index=False)

    leaderboard = create_leaderboard(aggregated)

    with open(EVALUATION_DIR / "leaderboard.md", "w", encoding="utf-8") as file:
        file.write(leaderboard)

    print(f"[SUCCESS] Evaluation completed for {len(model_results)} models.")