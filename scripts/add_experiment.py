#!/usr/bin/env python3
"""
Quick script to add new experiments to the overview.csv file.
Usage: python add_experiment.py
"""

import csv
import os
from datetime import datetime


def add_experiment_interactive():
    """Interactive function to add a new experiment."""
    print("Add New Experiment to Overview CSV")
    print("=" * 40)

    # Get experiment details from user
    group = input("Group (e.g., exp_mito, exp_cell): ")
    setup = input("Setup (e.g., setup_35): ")
    target = input("Target (e.g., mito, cell, nuc): ")
    model_type = input("Model Type (e.g., fly model, isolated_unet): ")
    starting_checkpoint = input("Starting Checkpoint: ")

    # Optional fields
    max_iterations = input("Max Iterations (optional): ") or None
    resolution_nm = input("Resolution (nm) (optional): ") or None
    batch_size = input("Batch Size (optional): ") or None
    learning_rate = input("Learning Rate (optional): ") or None
    creation_date = input(
        "Creation Date (YYYY-MM-DD, optional - today if empty): "
    ) or datetime.now().strftime("%Y-%m-%d")
    still_running = input("Still Running? (YES/NO, default NO): ").upper() or "NO"

    # Convert empty strings to appropriate values
    if max_iterations:
        try:
            max_iterations = int(max_iterations)
        except ValueError:
            pass  # Keep as string for values like "80000+"

    if resolution_nm:
        try:
            resolution_nm = int(resolution_nm)
        except ValueError:
            pass  # Keep as string for values like "16-64"

    if batch_size:
        try:
            batch_size = float(batch_size)
        except ValueError:
            batch_size = None

    if learning_rate:
        try:
            learning_rate = float(learning_rate)
        except ValueError:
            learning_rate = None

    # Create new row
    new_row = {
        "Group": group,
        "Setup": setup,
        "Target": target,
        "Model Type": model_type,
        "Starting Checkpoint": starting_checkpoint,
        "Max Iterations": str(max_iterations) if max_iterations is not None else "",
        "Resolution (nm)": str(resolution_nm) if resolution_nm is not None else "",
        "Batch Size": str(batch_size) if batch_size is not None else "",
        "Learning Rate": str(learning_rate) if learning_rate is not None else "",
        "Creation Date": creation_date,
        "Still Running": still_running,
    }

    return new_row


def append_to_csv(csv_file, new_row):
    """Append a new row to the CSV file."""
    fieldnames = [
        "Group",
        "Setup",
        "Target",
        "Model Type",
        "Starting Checkpoint",
        "Max Iterations",
        "Resolution (nm)",
        "Batch Size",
        "Learning Rate",
        "Creation Date",
        "Still Running",
    ]

    # Check if file exists
    file_exists = os.path.exists(csv_file)

    with open(csv_file, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if file doesn't exist
        if not file_exists:
            writer.writeheader()

        writer.writerow(new_row)


def main():
    csv_file = "overview.csv"

    print(f"Adding experiment to {csv_file}")
    print()

    # Get new experiment details
    new_experiment = add_experiment_interactive()

    # Show summary
    print("\nExperiment Summary:")
    print("-" * 20)
    for key, value in new_experiment.items():
        if value:  # Only show non-empty values
            print(f"{key}: {value}")

    # Confirm
    confirm = input("\nAdd this experiment? (y/n): ").lower()
    if confirm == "y" or confirm == "yes":
        append_to_csv(csv_file, new_experiment)
        print(f"Experiment added to {csv_file}")
    else:
        print("Experiment not added.")


if __name__ == "__main__":
    main()
