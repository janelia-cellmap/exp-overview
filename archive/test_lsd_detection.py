#!/usr/bin/env python3

import yaml
from pathlib import Path


def detect_lsd_usage(run_dir):
    """Detect if experiment uses LSD by checking config.yaml and train.py files."""
    config_file = run_dir / "config.yaml"
    train_file = run_dir / "train.py"

    print(f"Checking LSD for: {run_dir}")
    print(f"Config file exists: {config_file.exists()}")
    print(f"Train file exists: {train_file.exists()}")

    # Check config.yaml for is_lsd or lsd flags
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            if isinstance(config, dict):
                # Check run section for lsd flags
                run_config = config.get("run", {})
                if run_config:
                    is_lsd = run_config.get("is_lsd", False)
                    lsd = run_config.get("lsd", False)
                    print(f"Config is_lsd: {is_lsd}, lsd: {lsd}")
                    if is_lsd or lsd:
                        print("Found LSD flag in config.yaml")
                        return True

        except Exception as e:
            print(
                f"Warning: Could not parse config.yaml for LSD detection in {run_dir}: {e}"
            )

    # Check train.py for affinities_map parameter
    if train_file.exists():
        try:
            with open(train_file, "r") as f:
                train_content = f.read()

            # Look for affinities_map parameter in run() function call
            has_affinities_map = "affinities_map" in train_content
            has_assignment = "affinities_map =" in train_content
            print(f"Train.py has 'affinities_map': {has_affinities_map}")
            print(f"Train.py has 'affinities_map =': {has_assignment}")

            if has_affinities_map and has_assignment:
                print("Found affinities_map in train.py")
                return True

        except Exception as e:
            print(
                f"Warning: Could not read train.py for LSD detection in {run_dir}: {e}"
            )

    print("No LSD indicators found")
    return False


# Test setup_15
setup_15_dir = Path("/groups/cellmap/cellmap/zouinkhim/exp_salivary/runs/setup_15")
result = detect_lsd_usage(setup_15_dir)
print(f"\nSetup_15 LSD result: {result}")
