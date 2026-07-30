from pathlib import Path

from validators import validate_file


PREDICTIONS_DIR = Path("data/predictions")


if __name__ == "__main__":

    prediction_files = sorted(PREDICTIONS_DIR.rglob("*.json"))

    if len(prediction_files) == 0:
        raise RuntimeError("No prediction files found.")

    failed = False

    print(f"Validating {len(prediction_files)} prediction files...\n")

    for prediction_file in prediction_files:

        errors = validate_file(prediction_file)

        if errors:

            failed = True

            print(f"[ERROR] {prediction_file}")

            for error in errors:
                print(f"   - {error}")

            print()

    if failed:
        raise RuntimeError("Validation failed.")

    print("[SUCCESS] All prediction files passed validation.")
