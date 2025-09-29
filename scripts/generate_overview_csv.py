#!/usr/bin/env python3
"""
Script to generate and manage t        headers = [
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
            "LSD",
        ] overview CSV file.
This script allows you to add new experiments and maintain the overview.csv file.
"""

import csv
import os
import yaml
from datetime import datetime
from dataclasses import dataclass, fields
from typing import Optional, List, Union


@dataclass
class ExperimentEntry:
    """Data class representing a single experiment entry."""

    group: str
    setup: str
    target: str
    model_type: str
    starting_checkpoint: str
    max_iterations: Optional[Union[str, int]] = None
    resolution_nm: Optional[Union[str, int]] = None
    batch_size: Optional[float] = None
    learning_rate: Optional[float] = None
    creation_date: Optional[str] = None
    still_running: str = "NO"
    lsd: str = "NO"
    trained_until: Optional[str] = None

    def to_dict(self):
        """Convert the entry to a dictionary for CSV writing."""
        return {
            "Group": self.group,
            "Setup": self.setup,
            "Target": self.target,
            "Model Type": self.model_type,
            "Starting Checkpoint": self.starting_checkpoint,
            "Max Iterations": self.max_iterations,
            "Resolution (nm)": self.resolution_nm,
            "Batch Size": self.batch_size,
            "Learning Rate": self.learning_rate,
            "Creation Date": self.creation_date,
            "Still Running": self.still_running,
            "LSD": self.lsd,
            "Trained Until": self.trained_until,
        }


class ExperimentOverviewGenerator:
    """Class to manage the experiment overview CSV file."""

    def __init__(self, csv_file_path: str = "auto_generated_overview.csv"):
        self.csv_file_path = csv_file_path
        self.fieldnames = [
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
            "LSD",
            "Trained Until",
        ]
        self.experiments = []

    def load_existing_data(self):
        """Load existing data from CSV file if it exists."""
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Convert back to ExperimentEntry
                    entry = ExperimentEntry(
                        group=row["Group"],
                        setup=row["Setup"],
                        target=row["Target"],
                        model_type=row["Model Type"],
                        starting_checkpoint=row["Starting Checkpoint"],
                        max_iterations=(
                            row["Max Iterations"] if row["Max Iterations"] else None
                        ),
                        resolution_nm=(
                            row["Resolution (nm)"] if row["Resolution (nm)"] else None
                        ),
                        batch_size=(
                            float(row["Batch Size"]) if row["Batch Size"] else None
                        ),
                        learning_rate=(
                            float(row["Learning Rate"])
                            if row["Learning Rate"]
                            else None
                        ),
                        creation_date=(
                            row["Creation Date"] if row["Creation Date"] else None
                        ),
                        still_running=row["Still Running"],
                        lsd=row.get("LSD", "NO"),
                        trained_until=row.get("Trained Until", None),
                    )
                    self.experiments.append(entry)

    def add_experiment(self, experiment: ExperimentEntry):
        """Add a new experiment to the list."""
        if experiment.creation_date is None:
            experiment.creation_date = datetime.now().strftime("%Y-%m-%d")
        self.experiments.append(experiment)

    def write_csv(self):
        """Write all experiments to the CSV file."""
        with open(self.csv_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for experiment in self.experiments:
                writer.writerow(experiment.to_dict())

    def add_experiments_from_data(self, experiment_data: List[dict]):
        """Add multiple experiments from a list of dictionaries."""
        for data in experiment_data:
            experiment = ExperimentEntry(**data)
            self.add_experiment(experiment)


def scan_experiment_directories(base_path="/groups/cellmap/cellmap/zouinkhim"):
    """Scan experiment directories and extract real experiment data."""
    import yaml
    import glob
    from pathlib import Path

    experiments = []

    # Define experiment directory patterns
    exp_dirs = [
        "exp_cell",
        "exp_cerebellum",
        "exp_pancreas",
        "exp_c-elegen",
        "ex_mito",
        "exp_salivary",
    ]

    for exp_dir in exp_dirs:
        exp_path = Path(base_path) / exp_dir
        if not exp_path.exists():
            continue

        print(f"Scanning {exp_dir}...")

        if exp_dir == "exp_c-elegen":
            # Handle special structure for c-elegen
            experiments.extend(scan_c_elegen_directory(exp_path))
        elif exp_dir == "ex_mito":
            # Handle ex_mito structure
            experiments.extend(scan_ex_mito_directory(exp_path))
        elif exp_dir == "exp_salivary":
            # Handle exp_salivary (which contains exp_mito runs due to naming mistake)
            experiments.extend(scan_standard_exp_directory(exp_path, "exp_mito"))
        else:
            # Handle standard experiment structure
            experiments.extend(scan_standard_exp_directory(exp_path, exp_dir))

    return experiments


def scan_standard_exp_directory(exp_path, group_name):
    """Scan standard experiment directory structure."""
    import yaml
    from pathlib import Path
    import os

    experiments = []
    runs_path = exp_path / "runs"

    if not runs_path.exists():
        return experiments

    # Get all setup directories
    setup_dirs = [
        d for d in runs_path.iterdir() if d.is_dir() and d.name.startswith("setup_")
    ]

    for setup_dir in setup_dirs:
        config_file = setup_dir / "config.yaml"
        if not config_file.exists():
            continue

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            # Extract experiment info
            experiment_data = extract_experiment_from_config(
                config, group_name, setup_dir.name, setup_dir
            )
            if experiment_data:
                experiments.append(experiment_data)

        except Exception as e:
            print(f"Error reading config for {setup_dir}: {e}")
            continue

    return experiments


def scan_c_elegen_directory(exp_path):
    """Scan exp_c-elegen directory with its special structure."""
    import yaml
    from pathlib import Path

    experiments = []

    # Check v2, v3, v4 subdirectories
    for version_dir in ["v2", "v3", "v4"]:
        version_path = exp_path / version_dir
        if not version_path.exists():
            continue

        group_name = f"exp_c-elegen_{version_dir}"

        if version_dir == "v3":
            # v3 has train subdirectory with runs
            train_path = version_path / "train"
            if train_path.exists():
                experiments.extend(scan_v3_train_directory(train_path, group_name))
        elif version_dir == "v4":
            # v4 has train/runs structure
            runs_path = version_path / "train" / "runs"
            if runs_path.exists():
                setup_dirs = [
                    d
                    for d in runs_path.iterdir()
                    if d.is_dir() and d.name.startswith("setup_")
                ]
                for setup_dir in setup_dirs:
                    config_file = setup_dir / "config.yaml"
                    if config_file.exists():
                        try:
                            with open(config_file, "r") as f:
                                config = yaml.safe_load(f)
                            experiment_data = extract_experiment_from_config(
                                config, group_name, setup_dir.name, setup_dir
                            )
                            if experiment_data:
                                experiments.append(experiment_data)
                        except Exception as e:
                            print(f"Error reading config for {setup_dir}: {e}")

    return experiments


def scan_v3_train_directory(train_path, group_name):
    """Scan v3 train directory for experiments."""
    experiments = []

    # Look for run directories in train/runs
    runs_path = train_path / "runs"
    if runs_path.exists():
        run_dirs = [d for d in runs_path.iterdir() if d.is_dir()]
        for run_dir in run_dirs:
            # For v3, the run directory names are the setup names
            setup_name = run_dir.name

            # Try to infer experiment details from directory name and structure
            experiment_data = {
                "group": group_name,
                "setup": setup_name,
                "target": infer_target_from_name(setup_name),
                "model_type": "fly model",
                "starting_checkpoint": "from scratch",  # Default, will be updated below
                "creation_date": infer_date_from_name(setup_name),
                "still_running": "NO",  # v3 experiments are likely finished
                "max_iterations": None,
                "resolution_nm": None,
                "batch_size": None,
                "learning_rate": None,
                "lsd": "NO",  # Default
                "trained_until": None,
            }

            # Try to get starting checkpoint from train.py
            train_py_file = run_dir / "train.py"
            if train_py_file.exists():
                try:
                    checkpoint_info = extract_checkpoint_from_train_py(train_py_file)
                    if checkpoint_info:
                        experiment_data["starting_checkpoint"] = checkpoint_info
                except Exception as e:
                    print(f"Error reading train.py for {run_dir}: {e}")

            # Check for actual checkpoint files and max iterations
            max_iterations = get_max_iterations_from_checkpoints(run_dir)
            experiment_data["max_iterations"] = max_iterations

            # Determine if still running based on recent activity
            still_running = determine_if_running(run_dir)
            experiment_data["still_running"] = still_running

            # Try to get more details from any config files
            # Try to extract target from config files
            config_target = extract_additional_config_info(run_dir)
            if config_target:
                experiment_data["target"] = config_target
            # If no target found in config, keep the name-based inference

            # Check for LSD usage
            lsd_detected = detect_lsd_usage(run_dir)
            if lsd_detected:
                experiment_data["lsd"] = "YES"

            # Get trained until date from latest checkpoint
            trained_until_date = get_trained_until_date(run_dir)
            experiment_data["trained_until"] = trained_until_date

            # Skip experiments that have no checkpoint files AND are not running
            # This filters out incomplete/failed experiments
            if max_iterations is None and still_running == "NO":
                print(f"Skipping {setup_name} - no checkpoints found and not running")
                continue

            # Skip experiments with low max_iterations that are not still running
            # This filters out experiments that likely failed early
            if (
                max_iterations is not None
                and max_iterations < 20000
                and still_running == "NO"
            ):
                print(
                    f"Skipping {setup_name} - low max iterations ({max_iterations}) and not running"
                )
                continue

            experiments.append(experiment_data)

    return experiments


def scan_ex_mito_directory(exp_path):
    """Scan ex_mito directory."""
    experiments = []

    # Look for yaml files that might contain experiment configs
    yaml_path = exp_path / "yamls"
    if yaml_path.exists():
        yaml_files = list(yaml_path.glob("*.yaml"))
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    config = yaml.safe_load(f)

                # Check if there's a corresponding train.py file or training evidence
                train_py_file = yaml_path / f"{yaml_file.stem}_train.py"
                if not train_py_file.exists():
                    train_py_file = yaml_path / "train.py"

                # Only include if there's evidence this is a training experiment
                # (has a train.py file or the YAML contains training configuration)
                is_training_experiment = False

                if train_py_file.exists():
                    is_training_experiment = True
                elif isinstance(config, dict):
                    # Check if YAML contains training-related configuration
                    if any(
                        key in config
                        for key in [
                            "run",
                            "training",
                            "model",
                            "optimizer",
                            "checkpoint",
                        ]
                    ):
                        is_training_experiment = True

                # Skip if this doesn't look like a training experiment
                if not is_training_experiment:
                    print(
                        f"Skipping {yaml_file.stem} - appears to be a data config file, not a training experiment"
                    )
                    continue

                # Create experiment entry for ex_mito
                experiment_data = {
                    "group": "exp_mito",
                    "setup": yaml_file.stem,
                    "target": "mito",
                    "model_type": "fly model",
                    "starting_checkpoint": "from scratch",
                    "still_running": "NO",
                }

                if train_py_file.exists():
                    checkpoint_info = extract_checkpoint_from_train_py(train_py_file)
                    if checkpoint_info:
                        experiment_data["starting_checkpoint"] = checkpoint_info

                experiments.append(experiment_data)
            except Exception as e:
                print(f"Error processing {yaml_file}: {e}")
                continue

    return experiments


def extract_experiment_from_config(config, group_name, setup_name, setup_dir):
    """Extract experiment data from a config.yaml file."""
    from pathlib import Path
    import os

    experiment_data = {
        "group": group_name,
        "setup": setup_name,
        "target": infer_target_from_name(setup_name),  # Default fallback
        "model_type": "fly model",  # default
        "starting_checkpoint": "",
        "max_iterations": None,
        "resolution_nm": None,
        "batch_size": None,
        "learning_rate": None,
        "creation_date": None,
        "still_running": "NO",
        "lsd": "NO",  # Default
        "trained_until": None,
    }

    # Extract target from labels (preferred)
    if "run" in config and "labels" in config["run"]:
        labels = config["run"]["labels"]
        if isinstance(labels, list):
            # Remove duplicates while preserving order
            unique_labels = []
            seen = set()
            for label in labels:
                if label not in seen:
                    unique_labels.append(label)
                    seen.add(label)
            experiment_data["target"] = "+".join(unique_labels)
        else:
            experiment_data["target"] = str(labels)

    # Extract model type
    if "checkpoint" in config:
        if "model_type" in config["checkpoint"]:
            experiment_data["model_type"] = config["checkpoint"]["model_type"]

        # Extract starting checkpoint
        if "path" in config["checkpoint"]:
            checkpoint_path = config["checkpoint"]["path"]
            experiment_data["starting_checkpoint"] = extract_checkpoint_name(
                checkpoint_path
            )

    # Extract run parameters
    if "run" in config:
        run_config = config["run"]

        if "voxel_size" in run_config:
            experiment_data["resolution_nm"] = run_config["voxel_size"]

        if "batch_size" in run_config:
            experiment_data["batch_size"] = run_config["batch_size"]

        if "l_rate" in run_config:
            experiment_data["learning_rate"] = run_config["l_rate"]

        # Check for LSD usage
        if run_config.get("is_lsd", False) or run_config.get("lsd", False):
            experiment_data["lsd"] = "YES"

    # Also check train.py for LSD usage (affinities_map parameter)
    train_file = setup_dir / "train.py"
    if (
        train_file.exists() and experiment_data["lsd"] == "NO"
    ):  # Only check if not already found
        try:
            with open(train_file, "r") as f:
                train_content = f.read()
            # Look for uncommented affinities_map parameter in run() function call
            lines = train_content.split("\n")
            for line in lines:
                stripped_line = line.strip()
                # Skip commented lines
                if stripped_line.startswith("#"):
                    continue
                # Look for affinities_map assignment or parameter
                if "affinities_map" in line and (
                    "affinities_map =" in line or "affinities_map=" in line
                ):
                    experiment_data["lsd"] = "YES"
                    break
        except Exception as e:
            print(
                f"Warning: Could not read train.py for LSD detection in {setup_dir}: {e}"
            )

    # Determine max iterations from checkpoint files
    experiment_data["max_iterations"] = get_max_iterations_from_checkpoints(setup_dir)

    # Determine if still running based on recent activity
    experiment_data["still_running"] = determine_if_running(setup_dir)

    # Try to get creation date from directory modification time
    experiment_data["creation_date"] = get_creation_date(setup_dir)

    # Get trained until date from latest checkpoint
    experiment_data["trained_until"] = get_trained_until_date(setup_dir)

    # Skip experiments that have no checkpoint files AND are not running
    # This filters out incomplete/failed experiments
    if (
        experiment_data["max_iterations"] is None
        and experiment_data["still_running"] == "NO"
    ):
        print(f"Skipping {setup_name} - no checkpoints found and not running")
        return None

    # Skip experiments with low max_iterations that are not still running
    # This filters out experiments that likely failed early
    if (
        experiment_data["max_iterations"] is not None
        and experiment_data["max_iterations"] < 20000
        and experiment_data["still_running"] == "NO"
    ):
        print(
            f"Skipping {setup_name} - low max iterations ({experiment_data['max_iterations']}) and not running"
        )
        return None

    return experiment_data


def extract_checkpoint_name(checkpoint_path):
    """Extract a readable checkpoint name from full path."""
    from pathlib import Path

    path = Path(checkpoint_path)

    # Get the parent directory name and checkpoint name
    if "model_checkpoint_" in path.name:
        iteration = path.name.replace("model_checkpoint_", "")
        parent_name = path.parent.name
        return (
            f"{parent_name}/{iteration}k"
            if len(iteration) >= 4
            else f"{parent_name}/{iteration}"
        )
    else:
        # Just return the last two parts of the path
        return f"{path.parent.name}/{path.name}"


def get_max_iterations_from_checkpoints(setup_dir):
    """Get maximum iterations from checkpoint files in the directory."""
    from pathlib import Path
    import re

    checkpoint_files = list(setup_dir.glob("model_checkpoint_*"))
    if not checkpoint_files:
        return None

    max_iter = 0
    for checkpoint in checkpoint_files:
        match = re.search(r"model_checkpoint_(\d+)", checkpoint.name)
        if match:
            iteration = int(match.group(1))
            max_iter = max(max_iter, iteration)

    return max_iter if max_iter > 0 else None


def determine_if_running(setup_dir):
    """Determine if experiment is still running based on directory contents."""
    from pathlib import Path
    import os
    from datetime import datetime, timedelta

    # Check if there are recent checkpoint files (within last 7 days)
    recent_threshold = datetime.now() - timedelta(days=7)

    checkpoint_files = list(setup_dir.glob("model_checkpoint_*"))
    for checkpoint in checkpoint_files:
        try:
            mtime = datetime.fromtimestamp(checkpoint.stat().st_mtime)
            if mtime > recent_threshold:
                return "YES"
        except:
            continue

    return "NO"


def get_creation_date(setup_dir):
    """Get creation date from directory modification time."""
    import os
    from datetime import datetime

    try:
        # Use the directory creation/modification time
        mtime = datetime.fromtimestamp(setup_dir.stat().st_mtime)
        return mtime.strftime("%Y-%m-%d")
    except:
        return None


def get_trained_until_date(setup_dir):
    """Get the date when training ended by finding the latest checkpoint file."""
    from pathlib import Path
    from datetime import datetime
    import re

    try:
        # Find all checkpoint files
        checkpoint_files = list(setup_dir.glob("model_checkpoint_*"))
        if not checkpoint_files:
            return None

        # Find the checkpoint with the highest iteration number
        latest_checkpoint = None
        max_iteration = -1

        for checkpoint in checkpoint_files:
            match = re.search(r"model_checkpoint_(\d+)", checkpoint.name)
            if match:
                iteration = int(match.group(1))
                if iteration > max_iteration:
                    max_iteration = iteration
                    latest_checkpoint = checkpoint

        if latest_checkpoint:
            # Get the modification time of the latest checkpoint
            mtime = datetime.fromtimestamp(latest_checkpoint.stat().st_mtime)
            return mtime.strftime("%Y-%m-%d")

        return None
    except Exception as e:
        print(f"Warning: Could not get trained until date for {setup_dir}: {e}")
        return None


def infer_target_from_name(name):
    """Infer target organelle from experiment name."""
    name_lower = name.lower()

    # More specific patterns first
    targets = []

    if "mito" in name_lower:
        targets.append("mito")
    if "nuc" in name_lower:
        targets.append("nuc")
    if "cell" in name_lower:
        targets.append("cell")
    if "er" in name_lower:
        targets.append("er")
    if "ld" in name_lower:
        targets.append("ld")
    if "lyso" in name_lower:
        targets.append("lyso")
    if "perox" in name_lower:
        targets.append("perox")
    if "yolk" in name_lower:
        targets.append("yolk")
    if "ecs" in name_lower:
        targets.append("ecs")
    if "isg" in name_lower:
        targets.append("isg")

    if targets:
        return "+".join(targets)
    else:
        return "unknown"  # Changed from 'various' to 'unknown'


def infer_date_from_name(name):
    """Infer date from experiment name if it contains a date."""
    import re

    # Look for date pattern YYYYMMDD
    date_match = re.search(r"(\d{8})", name)
    if date_match:
        date_str = date_match.group(1)
        try:
            from datetime import datetime

            date_obj = datetime.strptime(date_str, "%Y%m%d")
            return date_obj.strftime("%Y-%m-%d")
        except:
            pass

    return None


def extract_checkpoint_from_train_py(train_py_file):
    """Extract starting checkpoint information from train.py file."""
    try:
        with open(train_py_file, "r") as f:
            content = f.read()

        # Look for common patterns that indicate checkpoint paths
        import re

        # Pattern 1: checkpoint_path = "..."
        checkpoint_patterns = [
            r'checkpoint_path\s*=\s*["\']([^"\']+)["\']',
            r'checkpoint\s*=\s*["\']([^"\']+)["\']',
            r'model_checkpoint_path\s*=\s*["\']([^"\']+)["\']',
            r'load_checkpoint\s*=\s*["\']([^"\']+)["\']',
            r'resume_from\s*=\s*["\']([^"\']+)["\']',
            r'pretrained_model\s*=\s*["\']([^"\']+)["\']',
            # Look for paths that contain model_checkpoint_
            r'["\']([^"\']*model_checkpoint_[^"\']+)["\']',
            # Look for paths that might be checkpoints
            r'["\']([^"\']*\/\d+)["\']',
        ]

        for pattern in checkpoint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if (
                    match
                    and "model_checkpoint_" in match
                    or "/run" in match
                    or any(
                        word in match.lower()
                        for word in ["checkpoint", "model", "pretrain"]
                    )
                ):
                    return extract_checkpoint_name(match)

        # If no explicit checkpoint found, look for commented checkpoints or paths
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("#") and (
                "checkpoint" in line.lower() or "model_checkpoint_" in line
            ):
                # Try to extract path from comment
                match = re.search(r'["\']([^"\']*model_checkpoint_[^"\']+)["\']', line)
                if match:
                    return extract_checkpoint_name(match.group(1))

                # Look for paths in comments
                match = re.search(r'(/[^"\'\s]+model_checkpoint_\d+)', line)
                if match:
                    return extract_checkpoint_name(match.group(1))

        return None

    except Exception as e:
        print(f"Error reading train.py: {e}")
        return None


def detect_lsd_usage(run_dir):
    """Detect if experiment uses LSD by checking config.yaml and train.py files."""
    config_file = run_dir / "config.yaml"
    train_file = run_dir / "train.py"

    # Check config.yaml for is_lsd or lsd flags
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            if isinstance(config, dict):
                # Check run section for lsd flags
                run_config = config.get("run", {})
                if run_config:
                    if run_config.get("is_lsd", False) or run_config.get("lsd", False):
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

            # Look for uncommented affinities_map parameter in run() function call
            lines = train_content.split("\n")
            for line in lines:
                stripped_line = line.strip()
                # Skip commented lines
                if stripped_line.startswith("#"):
                    continue
                # Look for affinities_map assignment or parameter
                if "affinities_map" in line and (
                    "affinities_map =" in line or "affinities_map=" in line
                ):
                    return True

        except Exception as e:
            print(
                f"Warning: Could not read train.py for LSD detection in {run_dir}: {e}"
            )

    return False


def extract_additional_config_info(run_dir):
    """Extract target organelles from config.yaml and train.py files."""
    config_file = run_dir / "config.yaml"
    train_file = run_dir / "train.py"

    config_targets = set()

    # First try to extract from config.yaml
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            # Extract labels from segmentation tasks
            if isinstance(config, dict):
                # First check for labels directly at the top level (C. elegans v3 style)
                labels = config.get("labels", [])

                # If no top-level labels, look for labels in task configuration
                if not labels:
                    task = config.get("task", {})
                    if task:
                        # Check for labels in segmentation configuration
                        seg_config = task.get("segmentation", {}) or task
                        labels = seg_config.get("labels", [])

                if labels:
                    for label in labels:
                        if isinstance(label, str):
                            label_lower = label.lower()
                            if "mito" in label_lower or "mitochondria" in label_lower:
                                config_targets.add("mito")
                            elif "nuc" in label_lower or "nucleus" in label_lower:
                                config_targets.add("nuc")
                            elif "cell" in label_lower:
                                config_targets.add("cell")
                            elif "er" in label_lower or "endoplasmic" in label_lower:
                                config_targets.add("er")
                            elif "ld" in label_lower or "lipid" in label_lower:
                                config_targets.add("ld")
                            elif "lyso" in label_lower or "lysosome" in label_lower:
                                config_targets.add("lyso")
                            elif "perox" in label_lower or "peroxisome" in label_lower:
                                config_targets.add("perox")
                            elif "yolk" in label_lower:
                                config_targets.add("yolk")
                            elif "ecs" in label_lower or "extracellular" in label_lower:
                                config_targets.add("ecs")
                            elif "isg" in label_lower:
                                config_targets.add("isg")

                    # Also check for dataset names that might contain target info
                    dataset = config.get("dataset", {})
                    if dataset:
                        dataset_name = dataset.get("name", "") or str(dataset)
                        if dataset_name:
                            name_lower = dataset_name.lower()
                            if "mito" in name_lower:
                                config_targets.add("mito")
                            elif "nuc" in name_lower:
                                config_targets.add("nuc")
                            elif "cell" in name_lower:
                                config_targets.add("cell")

        except Exception as e:
            print(f"Warning: Could not parse config.yaml in {run_dir}: {e}")

    # If no targets found in config.yaml, try to extract from train.py
    if not config_targets and train_file.exists():
        try:
            with open(train_file, "r") as f:
                train_content = f.read()

            # Look for label or target mentions in train.py
            train_lower = train_content.lower()
            if "mito" in train_lower or "mitochondria" in train_lower:
                config_targets.add("mito")
            if "nuc" in train_lower or "nucleus" in train_lower:
                config_targets.add("nuc")
            if "cell" in train_lower and "mitochondria" not in train_lower:
                config_targets.add("cell")
            if "er" in train_lower or "endoplasmic" in train_lower:
                config_targets.add("er")
            if "ld" in train_lower or "lipid" in train_lower:
                config_targets.add("ld")
            if "lyso" in train_lower or "lysosome" in train_lower:
                config_targets.add("lyso")
            if "perox" in train_lower or "peroxisome" in train_lower:
                config_targets.add("perox")
            if "yolk" in train_lower:
                config_targets.add("yolk")
            if "ecs" in train_lower or "extracellular" in train_lower:
                config_targets.add("ecs")
            if "isg" in train_lower:
                config_targets.add("isg")

        except Exception as e:
            print(f"Warning: Could not read train.py in {run_dir}: {e}")

    if config_targets:
        return "+".join(sorted(config_targets))
    else:
        return None


def create_sample_data():
    """Create experiment data by scanning actual directories."""
    return scan_experiment_directories()


def compare_csvs(original_csv, generated_csv):
    """Compare the original CSV with the auto-generated CSV."""
    import pandas as pd

    try:
        # Read both CSV files
        original_df = pd.read_csv(original_csv)
        generated_df = pd.read_csv(generated_csv)

        print(f"\nComparison Results:")
        print(f"Original CSV ({original_csv}): {len(original_df)} experiments")
        print(f"Generated CSV ({generated_csv}): {len(generated_df)} experiments")

        # Compare by setup names (most reliable identifier)
        original_setups = set(original_df["Setup"].values)
        generated_setups = set(generated_df["Setup"].values)

        # Find matches and differences
        matched_setups = original_setups.intersection(generated_setups)
        only_in_original = original_setups - generated_setups
        only_in_generated = generated_setups - original_setups

        print(f"\nSetup Comparison:")
        print(f"Matched setups: {len(matched_setups)}")
        print(f"Only in original: {len(only_in_original)}")
        print(f"Only in generated: {len(only_in_generated)}")

        if only_in_original:
            print(f"\nSetups only in original CSV:")
            for setup in sorted(only_in_original):
                print(f"  - {setup}")

        if only_in_generated:
            print(f"\nSetups only in generated CSV:")
            for setup in sorted(only_in_generated):
                print(f"  - {setup}")

        # Compare matched entries in detail
        if matched_setups:
            print(f"\nDetailed comparison of matched setups:")
            mismatches = []

            for setup in sorted(matched_setups):
                orig_row = original_df[original_df["Setup"] == setup].iloc[0]
                gen_row = generated_df[generated_df["Setup"] == setup].iloc[0]

                differences = []
                for col in original_df.columns:
                    if col in generated_df.columns:
                        orig_val = str(orig_row[col]).strip()
                        gen_val = str(gen_row[col]).strip()
                        if orig_val != gen_val and not (
                            pd.isna(orig_row[col]) and pd.isna(gen_row[col])
                        ):
                            differences.append(f"{col}: '{orig_val}' vs '{gen_val}'")

                if differences:
                    mismatches.append((setup, differences))

            if mismatches:
                print(f"Found differences in {len(mismatches)} matched setups:")
                for setup, diffs in mismatches[:10]:  # Show first 10
                    print(f"  {setup}:")
                    for diff in diffs[:3]:  # Show first 3 differences
                        print(f"    {diff}")
                if len(mismatches) > 10:
                    print(
                        f"    ... and {len(mismatches) - 10} more setups with differences"
                    )
            else:
                print("All matched setups have identical data!")

    except ImportError:
        print("pandas not available, doing basic comparison...")
        basic_compare_csvs(original_csv, generated_csv)
    except Exception as e:
        print(f"Error comparing CSVs: {e}")
        basic_compare_csvs(original_csv, generated_csv)


def basic_compare_csvs(original_csv, generated_csv):
    """Basic CSV comparison without pandas."""
    try:
        with open(original_csv, "r") as f:
            original_lines = f.readlines()

        with open(generated_csv, "r") as f:
            generated_lines = f.readlines()

        print(f"\nBasic Comparison:")
        print(f"Original CSV: {len(original_lines)-1} experiments (excluding header)")
        print(f"Generated CSV: {len(generated_lines)-1} experiments (excluding header)")

        # Extract setup names for comparison
        original_setups = set()
        generated_setups = set()

        for line in original_lines[1:]:  # Skip header
            parts = line.strip().split(",")
            if len(parts) > 1:
                original_setups.add(parts[1])  # Setup is column 1

        for line in generated_lines[1:]:  # Skip header
            parts = line.strip().split(",")
            if len(parts) > 1:
                generated_setups.add(parts[1])  # Setup is column 1

        matched = original_setups.intersection(generated_setups)
        only_original = original_setups - generated_setups
        only_generated = generated_setups - original_setups

        print(f"Matched setups: {len(matched)}")
        print(f"Only in original: {len(only_original)}")
        print(f"Only in generated: {len(only_generated)}")

    except Exception as e:
        print(f"Error in basic comparison: {e}")


def main():
    """Main function to demonstrate usage."""
    # Create the CSV generator
    generator = ExperimentOverviewGenerator(
        "data/processed/auto_generated_overview.csv"
    )

    # Generate from scratch with scanned data
    print(
        "Generating data/processed/auto_generated_overview.csv by scanning experiment directories..."
    )
    scanned_data = create_sample_data()
    generator.add_experiments_from_data(scanned_data)
    generator.write_csv()
    print(
        f"Generated {len(scanned_data)} experiment entries in data/processed/auto_generated_overview.csv"
    )

    # Compare with original overview.csv
    print("\nComparing with original overview.csv...")
    compare_csvs("data/raw/overview.csv", "data/processed/auto_generated_overview.csv")


if __name__ == "__main__":
    main()
