import json
import re
import sys
from pathlib import Path

PREDICTIONS_DIR = Path("data/predictions")

SCORE_PATTERN = re.compile(r"^\d+-\d+$")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_score(score):
    if not isinstance(score, str):
        raise ValueError("predicted_score must be a string.")

    if not SCORE_PATTERN.fullmatch(score):
        raise ValueError("predicted_score must have format '<int>-<int>'.")

    home, away = map(int, score.split("-"))
    return home, away


def validate_structure(data):
    errors = []

    if not isinstance(data, dict):
        return ["Root JSON must be an object."]

    required_root = {
        "match_id",
        "simulation_env",
        "match_context",
        "prediction",
    }

    missing = required_root - data.keys()
    if missing:
        errors.append(f"Missing root keys: {sorted(missing)}")
        return errors

    if not isinstance(data["match_id"], str):
        errors.append("'match_id' must be a string.")

    sim = data["simulation_env"]

    if not isinstance(sim, dict):
        errors.append("'simulation_env' must be an object.")
    else:
        required = {
            "timestamp",
            "model",
            "hyperparameters",
        }

        missing = required - sim.keys()
        if missing:
            errors.append(f"simulation_env missing keys: {sorted(missing)}")

        if "timestamp" in sim and not isinstance(sim["timestamp"], str):
            errors.append("'timestamp' must be a string.")

        if "model" in sim and not isinstance(sim["model"], str):
            errors.append("'model' must be a string.")

        hp = sim.get("hyperparameters")

        if not isinstance(hp, dict):
            errors.append("'hyperparameters' must be an object.")
        else:
            required = {
                "temperature",
                "top_p",
                "max_tokens",
            }

            missing = required - hp.keys()
            if missing:
                errors.append(f"hyperparameters missing keys: {sorted(missing)}")

            if "temperature" in hp and not is_number(hp["temperature"]):
                errors.append("'temperature' must be numeric.")

            if "top_p" in hp and not is_number(hp["top_p"]):
                errors.append("'top_p' must be numeric.")

            if "max_tokens" in hp and not isinstance(
                hp["max_tokens"], int
            ):
                errors.append("'max_tokens' must be an integer.")
    
    ctx = data["match_context"]

    if not isinstance(ctx, dict):
        errors.append("'match_context' must be an object.")
    else:
        required = {
            "tournament",
            "phase",
            "team_a",
            "team_b",
            "host_country",
        }

        missing = required - ctx.keys()
        if missing:
            errors.append(f"match_context missing keys: {sorted(missing)}")

        for key in required:
            if key in ctx and not isinstance(ctx[key], str):
                errors.append(f"'{key}' must be a string.")

        if "phase" in ctx and ctx["phase"] not in {"group", "knockout"}:
            errors.append("phase must be either 'group' or 'knockout'.")

    pred = data["prediction"]

    if not isinstance(pred, dict):
        errors.append("'prediction' must be an object.")
        return errors

    required = {
        "probabilities",
        "predicted_score",
        "predicted_winner",
        "knockout_resolution",
        "confidence",
    }

    missing = required - pred.keys()
    if missing:
        errors.append(f"prediction missing keys: {sorted(missing)}")

    if "confidence" in pred and not is_number(pred["confidence"]):
        errors.append("'confidence' must be numeric.")

    if ("predicted_score" in pred and not isinstance(pred["predicted_score"], str)):
        errors.append("'predicted_score' must be a string.")

    if ("predicted_winner" in pred and not isinstance(pred["predicted_winner"], str)):
        errors.append("'predicted_winner' must be a string.")

    probs = pred.get("probabilities")

    if not isinstance(probs, dict):
        errors.append("'probabilities' must be an object.")
    else:
        if len(probs) == 0:
            errors.append("'probabilities' cannot be empty.")

        for key, value in probs.items():
            if not is_number(value):
                errors.append(f"Probability '{key}' must be numeric.")

    resolution = pred.get("knockout_resolution")

    if not isinstance(resolution, dict):
        errors.append("'knockout_resolution' must be an object.")
    else:
        required = {
            "ended_in_extra_time",
            "ended_in_penalties",
            "penalty_shootout_score",
        }

        missing = required - resolution.keys()
        if missing:
            errors.append(f"knockout_resolution missing keys: {sorted(missing)}")

        if ("ended_in_extra_time" in resolution and not isinstance(resolution["ended_in_extra_time"], bool)):
            errors.append("'ended_in_extra_time' must be boolean.")

        if ("ended_in_penalties" in resolution and not isinstance(resolution["ended_in_penalties"], bool)):
            errors.append("'ended_in_penalties' must be boolean.")

        ps = resolution.get("penalty_shootout_score")

        if ps is not None and not isinstance(ps, str):
            errors.append("'penalty_shootout_score' must be a string or null.")

    return errors


def validate_semantics(data):
    errors = []

    ctx = data["match_context"]
    pred = data["prediction"]

    team_a = ctx["team_a"]
    team_b = ctx["team_b"]
    phase = ctx["phase"]

    winner = pred["predicted_winner"]
    score = pred["predicted_score"]

    try:
        home, away = parse_score(score)
    except ValueError as exc:
        return [str(exc)]

    tied = home == away

    probs = pred["probabilities"]

    total = sum(probs.values())

    if abs(total - 1.0) > 1e-6:
        errors.append(f"Probabilities sum to {total:.6f} instead of 1.")

    resolution = pred["knockout_resolution"]

    extra = resolution["ended_in_extra_time"]
    penalties = resolution["ended_in_penalties"]
    penalty_score = resolution["penalty_shootout_score"]

    if phase == "group":

        expected = {
            "team_a_win",
            "draw",
            "team_b_win",
        }

        if set(probs.keys()) != expected:
            errors.append("Invalid probability keys for group stage.")

        if winner not in {team_a, team_b, "Draw"}:
            errors.append("Winner must be Team A, Team B or Draw.")

        if tied and winner != "Draw":
            errors.append("Tied score requires predicted_winner='Draw'.")

        if not tied and winner == "Draw":
            errors.append("Non-tied score cannot have predicted_winner='Draw'.")

        if extra:
            errors.append("Group stage cannot end in extra time.")

        if penalties:
            errors.append("Group stage cannot end in penalties.")

        if penalty_score is not None:
            errors.append("Group stage cannot contain penalty_shootout_score.")

    else:

        expected = {
            "team_a_advance",
            "team_b_advance",
        }

        if set(probs.keys()) != expected:
            errors.append("Invalid probability keys for knockout stage.")

        if winner not in {team_a, team_b}:
            errors.append("Knockout winner must be Team A or Team B.")

        if extra and penalties:
            errors.append("Cannot end in both extra time and penalties.")

        if penalties:

            if not tied:
                errors.append("Penalty shootout requires a tied predicted_score.")

            if penalty_score is None:
                errors.append("Penalty shootout score is missing.")

        else:

            if tied:
                errors.append("Tied predicted_score requires penalties.")

            if penalty_score is not None:
                errors.append("Penalty shootout score present although penalties=False.")

    return errors


def validate_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON: {exc}"]

    errors = validate_structure(data)

    if errors:
        return errors

    return validate_semantics(data)


def main():
    files = sorted(PREDICTIONS_DIR.rglob("*.json"))

    if not files:
        print("No prediction files found.")
        sys.exit(1)

    failed = False

    print(f"Validating {len(files)} prediction files...\n")

    for file in files:
        errors = validate_file(file)

        if errors:
            failed = True
            print(f"[ERROR] {file}")

            for err in errors:
                print(f"   - {err}")

            print()

    if failed:
        print("Validation FAILED.")
        sys.exit(1)

    print("[SUCCESS] All prediction files passed validation.")


if __name__ == "__main__":
    main()
