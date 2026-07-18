import math
from typing import Tuple, List


EPSILON = 1e-15


def parse_score(score: str) -> Tuple[int, int]:
    """
    Parses a football score string into integer goal counts.

    :param score: Score string in the form "<team_a_goals>-<team_b_goals>".
    :return: Tuple containing Team A goals and Team B goals.
    """
    team_a, team_b = score.split("-")
    return int(team_a), int(team_b)


def match_outcome(score: str) -> str:
    """
    Determines the categorical match outcome from a scoreline.

    :param score: Score string in the form "<team_a_goals>-<team_b_goals>".
    :return: One of "team_a", "draw", or "team_b".
    """
    team_a, team_b = parse_score(score)

    if team_a > team_b:
        return "team_a"

    if team_b > team_a:
        return "team_b"

    return "draw"


def exact_score_accuracy(true_score: str, predicted_score: str) -> int:
    """
    Computes whether the predicted score exactly matches the official result.

    :param true_score: Official match score.
    :param predicted_score: Predicted score.
    :return: 1 if both scores are identical, otherwise 0.
    """
    return int(true_score == predicted_score)


def goal_mae(true_score: str, predicted_score: str) -> float:
    """
    Computes the mean absolute error across both teams' goal counts.

    :param true_score: Official match score.
    :param predicted_score: Predicted score.
    :return: Mean absolute error of predicted goals.
    """
    true_a, true_b = parse_score(true_score)
    pred_a, pred_b = parse_score(predicted_score)

    return (abs(true_a - pred_a) + abs(true_b - pred_b)) / 2


def goal_difference_mae(true_score: str, predicted_score: str) -> float:
    """
    Computes the absolute error between the predicted and official goal differences.

    :param true_score: Official match score.
    :param predicted_score: Predicted score.
    :return: Absolute error of goal difference.
    """
    true_a, true_b = parse_score(true_score)
    pred_a, pred_b = parse_score(predicted_score)

    true_difference = true_a - true_b
    predicted_difference = pred_a - pred_b

    return abs(true_difference - predicted_difference)


def outcome_accuracy(true_outcome: str, predicted_outcome: str) -> int:
    """
    Computes whether the predicted match outcome is correct.

    :param true_outcome: Official match outcome.
    :param predicted_outcome: Predicted outcome.
    :return: 1 if the predicted outcome matches the official outcome, otherwise 0.
    """
    return int(true_outcome == predicted_outcome)


def outcome_to_one_hot(outcome: str) -> List[float]:
    """
    Converts a categorical football outcome into a one-hot encoded vector.

    :param outcome: Match outcome label.
    :return: One-hot encoded probability vector.
    """
    mapping = {
        "team_a": [1.0, 0.0, 0.0],
        "draw": [0.0, 1.0, 0.0],
        "team_b": [0.0, 0.0, 1.0],
    }

    return mapping[outcome]


def group_probability_vector(probabilities: dict) -> List[float]:
    """
    Converts group-stage probability predictions into a fixed vector ordering.

    :param probabilities: Prediction probability dictionary.
    :return: Probability vector ordered as Team A, Draw, Team B.
    """
    return [
        probabilities["team_a_win"],
        probabilities["draw"],
        probabilities["team_b_win"],
    ]


def knockout_probability_vector(probabilities: dict, true_outcome: str) -> Tuple[List[float], List[float]]:
    """
    Converts knockout probabilities into binary vectors.

    :param probabilities: Prediction probability dictionary.
    :param true_outcome: True advancing team label.
    :return: Tuple containing the true vector and predicted probability vector.
    """
    if true_outcome == "team_a":
        truth = [1.0, 0.0]
    else:
        truth = [0.0, 1.0]

    prediction = [
        probabilities["team_a_advance"],
        probabilities["team_b_advance"],
    ]

    return truth, prediction


def brier_score(true_vector: List[float], predicted_vector: List[float]) -> float:
    """
    Computes the multiclass Brier score.

    :param true_vector: One-hot encoded ground-truth vector.
    :param predicted_vector: Predicted probability vector.
    :return: Brier score.
    """
    return sum(
        (truth - prediction) ** 2
        for truth, prediction in zip(true_vector, predicted_vector)
    )


def log_loss(true_vector: List[float], predicted_vector: List[float]) -> float:
    """
    Computes the multiclass logarithmic loss.

    :param true_vector: One-hot encoded ground-truth vector.
    :param predicted_vector: Predicted probability vector.
    :return: Logarithmic loss.
    """
    total = 0.0

    for truth, prediction in zip(true_vector, predicted_vector):
        probability = min(max(prediction, EPSILON), 1.0 - EPSILON)

        if truth == 1:
            total -= math.log(probability)

    return total


def evaluate_prediction(
    phase: str,
    true_score: str,
    predicted_score: str,
    probabilities: dict
) -> dict:
    """
    Evaluates a single prediction across all benchmark metrics.

    :param phase: Tournament phase.
    :param true_score: Official match score.
    :param predicted_score: Predicted score.
    :param probabilities: Prediction probability dictionary.
    :return: Dictionary containing all evaluation metrics.
    """
    metrics = {
        "exact_score_accuracy": exact_score_accuracy(true_score, predicted_score),
        "goal_mae": goal_mae(true_score, predicted_score),
        "goal_difference_mae": goal_difference_mae(true_score, predicted_score),
        "outcome_accuracy": outcome_accuracy(true_score, predicted_score),
    }

    outcome = match_outcome(true_score)

    if phase == "group":
        truth = outcome_to_one_hot(outcome)
        prediction = group_probability_vector(probabilities)
    else:
        truth, prediction = knockout_probability_vector(probabilities, outcome)

    metrics["brier_score"] = brier_score(truth, prediction)
    metrics["log_loss"] = log_loss(truth, prediction)

    return metrics