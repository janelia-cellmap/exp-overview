#!/usr/bin/env python3
"""
Comprehensive CSV correction script:
1. Fix target organelles from config.yaml
2. Get max iterations from highest model_checkpoint_XX file
3. Extract creation dates from DATE_XX.yaml files
"""

import yaml
import os
import pandas as pd
from pathlib import Path
import re
from datetime import datetime


def extract_targets_from_config(config_path):
    """Extract target labels from a config.yaml file"""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        targets = []

        # Check run -> labels (most common structure)
        if "run" in config and "labels" in config["run"]:
            targets = config["run"]["labels"]
        # Check checkpoint -> classes
        elif "checkpoint" in config and "classes" in config["checkpoint"]:
            targets = config["checkpoint"]["classes"]
        # Check task_config -> targets
        elif "task_config" in config and "targets" in config["task_config"]:
            for target_name, target_info in config["task_config"]["targets"].items():
                targets.append(target_name)

        return "+".join(sorted(set(targets))) if targets else "unknown"

    except Exception as e:
        print(f"Error reading {config_path}: {e}")
        return "error"


def get_max_iterations(setup_dir):
    """Get max iterations from highest model_checkpoint_XX file"""
    try:
        checkpoint_files = list(setup_dir.glob("model_checkpoint_*"))
        if not checkpoint_files:
            return "N/A"

        max_iter = 0
        for file in checkpoint_files:
            # Extract number from filename like model_checkpoint_90000
            match = re.search(r"model_checkpoint_(\d+)", file.name)
            if match:
                iteration = int(match.group(1))
                max_iter = max(max_iter, iteration)

        return max_iter if max_iter > 0 else "N/A"

    except Exception as e:
        print(f"Error checking iterations in {setup_dir}: {e}")
        return "error"


def extract_date_from_yaml_filename(setup_dir):
    """Extract creation date from DATE_XX.yaml files"""
    try:
        # Look for files matching date pattern like 20250827_*.yaml
        yaml_files = list(setup_dir.glob("*.yaml"))

        for yaml_file in yaml_files:
            # Match pattern like 20250827_something.yaml
            match = re.match(r"(\d{8})_.*\.yaml", yaml_file.name)
            if match:
                date_str = match.group(1)
                # Convert YYYYMMDD to YYYY-MM-DD
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                return formatted_date

        return None

    except Exception as e:
        print(f"Error extracting date from {setup_dir}: {e}")
        return None


def check_all_setups_comprehensive():
    """Comprehensive check of all setup information"""
    base_path = Path("/groups/cellmap/cellmap/zouinkhim")
    results = []

    # Define experiment groups with their correct paths
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

            # Extract information
            targets = "unknown"
            max_iterations = "N/A"
            creation_date = None

            if config_path.exists():
                targets = extract_targets_from_config(config_path)

            max_iterations = get_max_iterations(setup_dir)
            creation_date = extract_date_from_yaml_filename(setup_dir)

            results.append(
                {
                    "Group": group_name,
                    "Setup": setup_name,
                    "Targets_Found": targets,
                    "Max_Iterations_Found": max_iterations,
                    "Creation_Date_Found": creation_date,
                    "Setup_Path": str(setup_dir),
                }
            )

            print(
                f"{group_name:15} {setup_name:10} | {str(targets):25} | {str(max_iterations):8} | {str(creation_date)}"
            )

    # Check exp_c-elegen/v4
    v4_path = base_path / "exp_c-elegen" / "v4" / "train" / "runs"
    if v4_path.exists():
        for setup_dir in sorted(v4_path.glob("setup_*")):
            setup_name = setup_dir.name
            config_path = setup_dir / "config.yaml"

            # Extract information
            targets = "unknown"
            max_iterations = "N/A"
            creation_date = None

            if config_path.exists():
                targets = extract_targets_from_config(config_path)

            max_iterations = get_max_iterations(setup_dir)
            creation_date = extract_date_from_yaml_filename(setup_dir)

            results.append(
                {
                    "Group": "exp_c-elegen_v4",
                    "Setup": setup_name,
                    "Targets_Found": targets,
                    "Max_Iterations_Found": max_iterations,
                    "Creation_Date_Found": creation_date,
                    "Setup_Path": str(setup_dir),
                }
            )

            print(
                f"{'exp_c-elegen_v4':15} {setup_name:10} | {str(targets):25} | {str(max_iterations):8} | {str(creation_date)}"
            )

    return results


def update_csv_with_corrections():
    """Update the overview.csv with all corrections"""

    print("🔍 Checking all setups comprehensively...")
    print("=" * 80)
    print(f"{'Group':15} {'Setup':10} | {'Targets':25} | {'Max_Iter':8} | {'Date'}")
    print("=" * 80)

    # Get corrected information
    corrected_data = check_all_setups_comprehensive()

    # Read current CSV
    current_df = pd.read_csv("overview.csv")

    print(f"\n📊 Found {len(corrected_data)} setups with config information")
    print("🔧 Updating CSV...")

    # Create lookup dictionaries for corrections
    targets_lookup = {
        f"{row['Group']}_{row['Setup']}": row["Targets_Found"] for row in corrected_data
    }
    iterations_lookup = {
        f"{row['Group']}_{row['Setup']}": row["Max_Iterations_Found"]
        for row in corrected_data
    }
    dates_lookup = {
        f"{row['Group']}_{row['Setup']}": row["Creation_Date_Found"]
        for row in corrected_data
    }

    # Apply corrections
    corrections_made = {"targets": 0, "iterations": 0, "dates": 0}

    for idx, row in current_df.iterrows():
        lookup_key = f"{row['Group']}_{row['Setup']}"

        # Update targets
        if lookup_key in targets_lookup and targets_lookup[lookup_key] != "unknown":
            old_target = row["Target"]
            new_target = targets_lookup[lookup_key]
            if old_target != new_target:
                current_df.at[idx, "Target"] = new_target
                corrections_made["targets"] += 1
                print(
                    f"  ✏️  {row['Group']} {row['Setup']}: {old_target} → {new_target}"
                )

        # Update max iterations (only if we found actual checkpoint files)
        if lookup_key in iterations_lookup and isinstance(
            iterations_lookup[lookup_key], int
        ):
            old_iter = row["Max Iterations"]
            new_iter = iterations_lookup[lookup_key]
            if old_iter != new_iter:
                current_df.at[idx, "Max Iterations"] = new_iter
                corrections_made["iterations"] += 1
                print(f"  📊 {row['Group']} {row['Setup']}: {old_iter} → {new_iter}")

        # Update creation dates (only if we found date in yaml filename and current is empty)
        if (
            lookup_key in dates_lookup
            and dates_lookup[lookup_key] is not None
            and (pd.isna(row["Creation Date"]) or row["Creation Date"] == "")
        ):
            new_date = dates_lookup[lookup_key]
            current_df.at[idx, "Creation Date"] = new_date
            corrections_made["dates"] += 1
            print(f"  📅 {row['Group']} {row['Setup']}: Added date {new_date}")

    # Save corrected CSV
    current_df.to_csv("overview_corrected.csv", index=False)

    print(f"\n✅ Corrections completed:")
    print(f"   🎯 Targets corrected: {corrections_made['targets']}")
    print(f"   📊 Iterations corrected: {corrections_made['iterations']}")
    print(f"   📅 Dates added: {corrections_made['dates']}")
    print(f"   💾 Saved as 'overview_corrected.csv'")

    return current_df


if __name__ == "__main__":
    updated_df = update_csv_with_corrections()

    # Save detailed results for reference
    detailed_results = check_all_setups_comprehensive()
    detailed_df = pd.DataFrame(detailed_results)
    detailed_df.to_csv("detailed_setup_analysis.csv", index=False)
    print(f"   📋 Detailed analysis saved as 'detailed_setup_analysis.csv'")
