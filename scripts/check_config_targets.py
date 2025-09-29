#!/usr/bin/env python3
"""
Extract target organelles from config.yaml files for all setups
"""

import yaml
import os
import pandas as pd
from pathlib import Path


def extract_targets_from_config(config_path):
    """Extract target labels from a config.yaml file"""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Look for targets in different possible locations
        targets = []

        # Check run -> labels (most common structure)
        if "run" in config and "labels" in config["run"]:
            targets = config["run"]["labels"]

        # Check task_config -> targets
        elif "task_config" in config and "targets" in config["task_config"]:
            for target_name, target_info in config["task_config"]["targets"].items():
                targets.append(target_name)

        # Check tasks section
        elif "tasks" in config:
            for task_name, task_info in config["tasks"].items():
                if isinstance(task_info, dict) and "targets" in task_info:
                    for target_name in task_info["targets"]:
                        targets.append(target_name)

        # Check if there's a direct targets section
        elif "targets" in config:
            for target_name in config["targets"]:
                targets.append(target_name)

        # Check checkpoint -> classes
        elif "checkpoint" in config and "classes" in config["checkpoint"]:
            targets = config["checkpoint"]["classes"]

        return "+".join(sorted(set(targets))) if targets else "unknown"

    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return "error"


def check_all_setups():
    """Check all setup configs and extract targets"""
    base_path = Path("/groups/cellmap/cellmap/zouinkhim")
    results = []

    # Define experiment groups to check with their correct paths
    exp_paths = [
        ("exp_cerebellum", "exp_cerebellum/runs"),
        ("exp_pancreas", "exp_pancreas/runs"),
        ("exp_cell", "exp_cell/runs"),
        ("exp_mito", "exp_salivary/runs"),  # mito experiments are in exp_salivary
    ]

    for group_name, group_path in exp_paths:
        full_path = base_path / group_path
        if not full_path.exists():
            continue

        # Look for setup directories
        for setup_dir in sorted(full_path.glob("setup_*")):
            setup_name = setup_dir.name
            config_path = setup_dir / "config.yaml"

            if config_path.exists():
                targets = extract_targets_from_config(config_path)
                results.append(
                    {
                        "Group": group_name,
                        "Setup": setup_name,
                        "Config_Path": str(config_path),
                        "Targets_Found": targets,
                    }
                )
                print(f"{group_name:20} {setup_name:10} -> {targets}")
            else:
                print(f"{group_name:20} {setup_name:10} -> NO CONFIG")

    # Check exp_c-elegen/v4
    v4_path = base_path / "exp_c-elegen" / "v4" / "train" / "runs"
    if v4_path.exists():
        for setup_dir in sorted(v4_path.glob("setup_*")):
            setup_name = setup_dir.name
            config_path = setup_dir / "config.yaml"

            if config_path.exists():
                targets = extract_targets_from_config(config_path)
                results.append(
                    {
                        "Group": "exp_c-elegen_v4",
                        "Setup": setup_name,
                        "Config_Path": str(config_path),
                        "Targets_Found": targets,
                    }
                )
                print(f"{'exp_c-elegen_v4':20} {setup_name:10} -> {targets}")

    return results


if __name__ == "__main__":
    print("🔍 Checking organelle targets in config files...")
    print("=" * 60)

    results = check_all_setups()

    # Save results
    df = pd.DataFrame(results)
    df.to_csv("config_targets_check.csv", index=False)

    print("\n" + "=" * 60)
    print(f"✅ Checked {len(results)} setups")
    print("📄 Results saved to 'config_targets_check.csv'")
