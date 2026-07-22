import json
import re
from pathlib import Path
from typing import Any, List, Tuple


SCORE_PATTERN = re.compile(r"^\d+-\d+$")


def is_number(value: Any) -> bool:
    """
    Determines whether a value is a numeric type excluding booleans.

    :param value: Value to validate.
    :return: True if the value is numeric, otherwise False.
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_score(score: str) -> Tuple[int, int]:
    """
    Parses a football score string into integer goal counts.

    :param score: Score string in the form "<team_a_goals>-<team_b_goals>".
    :return: Tuple containing Team A goals and Team B goals.
    """
    if not isinstance(score, str):
        raise ValueError("predicted_score must be a string.")

    if not SCORE_PATTERN.fullmatch(score):
        raise ValueError("predicted_score must have format '<int>-<int>'.")

    team_a, team_b = map(int, score.split("-"))
    return team_a, team_b


def validate_confidence(confidence: float) -> List[str]:
    """
    Validates that confidence is a numeric probability within the closed interval [0, 1].

    :param confidence: Confidence value extracted from the prediction payload.
    :return: List of validation errors (empty if valid).
    """
    errors = []

    if not is_number(confidence):
        errors.append("'confidence' must be numeric.")
    elif confidence < 0 or confidence > 1:
        errors.append("'confidence' must be between 0 and 1.")

    return errors


def validate_score_winner_alignment(
    team_a: str,
    team_b: str,
    predicted_score: str,
    predicted_winner: str,
    phase: str,
) -> List[str]:
    """
    Validates that the predicted winner is logically consistent with the predicted score.

    :param team_a: Name of Team A.
    :param team_b: Name of Team B.
    :param predicted_score: Predicted score.
    :param predicted_winner: Predicted winner.
    :param phase: Tournament phase.
    :return: List of validation errors (empty if valid).
    """
    errors = []

    home_score, away_score = parse_score(predicted_score)

    if home_score > away_score and predicted_winner != team_a:
        errors.append("Predicted score indicates Team A victory but predicted_winner does not match.")
    elif away_score > home_score and predicted_winner != team_b:
        errors.append("Predicted score indicates Team B victory but predicted_winner does not match.")

    if phase == "group":
        if home_score == away_score and predicted_winner != "Draw":
            errors.append("Predicted score indicates a draw but predicted_winner is inconsistent.")

    return errors


def validate_structure(data: dict) -> List[str]:
    """
    Validates the structural integrity of a prediction document.

    :param data: Parsed prediction document.
    :return: List of validation errors (empty if valid).
    """
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

            if ("max_tokens" in hp and not isinstance(hp["max_tokens"], int)):
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

    if "confidence" in pred:
        errors.extend(validate_confidence(pred["confidence"]))

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

        penalty_score = resolution.get("penalty_shootout_score")

        if (penalty_score is not None and not isinstance(penalty_score, str)):
            errors.append("'penalty_shootout_score' must be a string or null.")

    return errors


def validate_semantics(data: dict) -> List[str]:
    """
    Validates the semantic consistency of a prediction document.

    :param data: Parsed prediction document.
    :return: List of validation errors (empty if valid).
    """
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

    errors.extend(
        validate_score_winner_alignment(
            team_a=team_a,
            team_b=team_b,
            predicted_score=score,
            predicted_winner=winner,
            phase=phase,
        )
    )

    tied = home == away

    probabilities = pred["probabilities"]

    total = sum(probabilities.values())

    if abs(total - 1.0) > 1e-6:
        errors.append(f"Probabilities sum to {total:.6f} instead of 1.")

    resolution = pred["knockout_resolution"]

    extra_time = resolution["ended_in_extra_time"]
    penalties = resolution["ended_in_penalties"]
    penalty_score = resolution["penalty_shootout_score"]

    if phase == "group":

        expected = {
            "team_a_win",
            "draw",
            "team_b_win",
        }

        if set(probabilities.keys()) != expected:
            errors.append("Invalid probability keys for group stage.")

        if winner not in {team_a, team_b, "Draw"}:
            errors.append("Winner must be Team A, Team B or Draw.")

        if tied and winner != "Draw":
            errors.append("Tied score requires predicted_winner='Draw'.")

        if not tied and winner == "Draw":
            errors.append("Non-tied score cannot have predicted_winner='Draw'.")

        if extra_time:
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

        if set(probabilities.keys()) != expected:
            errors.append("Invalid probability keys for knockout stage.")

        if winner not in {team_a, team_b}:
            errors.append("Knockout winner must be Team A or Team B.")

        if extra_time and penalties:
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


def validate_file(path: Path) -> List[str]:
    """
    Validates a prediction file against structural and semantic rules.

    :param path: Path to the prediction JSON file.
    :return: List of validation errors (empty if valid).
    """
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        return [f"Invalid JSON: {exc}"]

    errors = validate_structure(data)

    if errors:
        return errors

    return validate_semantics(data)
