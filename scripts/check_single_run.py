#!/usr/bin/env python3
"""
Single Run Zarr Data Validation
Checks if organelle zarr data exists and is non-empty for all crops in a single run
Usage: python check_single_run.py <path_to_config.yaml>
"""

import yaml
from pathlib import Path
import zarr
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import sys
import json
from urllib.parse import quote


def generate_neuroglancer_link(raw_path, label_path, organelle):
    """
    Generate a Neuroglancer link for visualizing raw and label data

    Args:
        raw_path: Path to raw zarr data
        label_path: Path to label zarr data (crop_path/organelle/s0)
        organelle: Name of the organelle

    Returns:
        str: Neuroglancer URL
    """

    # Convert local paths to HTTP URLs
    def convert_path(path):
        path_str = str(path)
        if path_str.startswith("/nrs/cellmap/"):
            return path_str.replace(
                "/nrs/cellmap/", "https://cellmap-vm1.int.janelia.org/nrs/"
            )
        return path_str

    raw_url = convert_path(raw_path)
    label_url = convert_path(label_path)

    # Create the state configuration
    state = {
        # "dimensions": {"x": [1e-9, "m"], "y": [1e-9, "m"], "z": [1e-9, "m"]},
        "layers": [
            {
                "type": "image",
                "source": f"{raw_url}",
                "name": "raw",
                "shader": """void main() {
  emitGrayscale(toNormalized(getDataValue()));
}""",
            },
            {
                "type": "segmentation",
                "source": f"{label_url.replace('/s0', '')}",
                "name": organelle,
            },
        ],
        # "layout": "xy",
    }

    # Convert to JSON and URL encode
    state_json = json.dumps(state, separators=(",", ":"))
    encoded_state = quote(state_json)

    return f"https://neuroglancer-demo.appspot.com/#!{encoded_state}"


def check_zarr_data(zarr_path):
    """
    Check if zarr data exists and contains any non-zero values

    Args:
        zarr_path: Path to zarr file/directory (crop_path/ORGANELLE/s0)

    Returns:
        tuple: (exists, has_data, error_message)
    """
    try:
        zarr_path = Path(zarr_path)

        if not zarr_path.exists():
            return False, False, "Path does not exist"

        # Open zarr array
        try:
            z = zarr.open(str(zarr_path), mode="r")
        except Exception as e:
            return False, False, f"Cannot open zarr: {str(e)}"

        # Check if any data exists (non-zero or non-empty)
        if hasattr(z, "shape"):
            if z.size == 0:
                return True, False, "Zarr array is empty (size=0)"

            # Check if any values in the entire array are non-zero
            try:
                has_any = z[:].any()
                if not has_any:
                    return True, False, "Array is all zeros"
                return True, True, None
            except Exception as e:
                return True, False, f"Error reading data: {str(e)}"
        else:
            return False, False, "Not a valid zarr array"

    except Exception as e:
        return False, False, f"Unexpected error: {str(e)}"


def check_crop(
    dataset_name,
    crop_name,
    crop_path,
    raw_path,
    labels,
    progress_counter,
    total_crops,
    lock,
):
    """
    Check a single crop for specified organelles

    Args:
        dataset_name: Name of the dataset
        crop_name: Name of the crop
        crop_path: Path to the crop directory
        raw_path: Path to the raw zarr data
        labels: List of organelle labels to check (from config.yaml)
        progress_counter: Shared counter for progress tracking
        total_crops: Total number of crops to check
        lock: Thread lock for synchronized printing

    Returns:
        dict: Error information for this crop
    """
    errors = {}

    crop_path = Path(crop_path)

    with lock:
        progress_counter[0] += 1
        current = progress_counter[0]
        print(f"[{current}/{total_crops}] Checking {dataset_name}/{crop_name}...")

    if not crop_path or not crop_path.exists():
        return {
            "dataset": dataset_name,
            "crop": crop_name,
            "error": f"Crop path does not exist: {crop_path}",
        }

    # Check only the specified organelles (labels)
    try:
        for organelle in labels:
            organelle_path = crop_path / organelle

            if not organelle_path.exists():
                if organelle not in errors:
                    errors[organelle] = []

                # Get parent path for the label (remove /organelle/s0 to get crop root)
                label_base = str(organelle_path / "s0")
                ng_link = generate_neuroglancer_link(raw_path, label_base, organelle)

                errors[organelle].append(
                    {
                        "dataset": dataset_name,
                        "crop": crop_name,
                        "crop_path": str(crop_path),
                        "zarr_path": label_base,
                        "error": f"Organelle directory does not exist: {organelle_path}",
                        "neuroglancer_link": ng_link,
                    }
                )
                continue

            # Check if s0 exists
            s0_path = organelle_path / "s0"

            exists, has_data, error_msg = check_zarr_data(s0_path)

            if not exists or not has_data:
                if organelle not in errors:
                    errors[organelle] = []

                ng_link = generate_neuroglancer_link(raw_path, str(s0_path), organelle)

                errors[organelle].append(
                    {
                        "dataset": dataset_name,
                        "crop": crop_name,
                        "crop_path": str(crop_path),
                        "zarr_path": str(s0_path),
                        "error": error_msg if error_msg else "No data found",
                        "neuroglancer_link": ng_link,
                    }
                )
    except Exception as e:
        return {
            "dataset": dataset_name,
            "crop": crop_name,
            "scan_error": f"Error scanning directory: {str(e)}",
        }

    return errors if errors else None


def validate_run_data(config_file):
    """
    Validate zarr data for a single run based on its config

    Returns:
        dict: Error information for this run
    """
    config_file = Path(config_file)

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Extract run information from path
        parts = config_file.parts
        exp_group = parts[-4] if len(parts) >= 4 else "unknown"
        setup_name = parts[-2] if len(parts) >= 2 else "unknown"

        # Get labels from config (under run.labels)
        run_config = config.get("run", {})
        labels = run_config.get("labels", [])
        if not labels:
            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "error": "No labels found in config.run.labels",
            }

        # Get yaml_file from config (under paths.yaml_file)
        paths = config.get("paths", {})
        yaml_file = paths.get("yaml_file")
        if not yaml_file:
            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "error": "No yaml_file found in config.paths",
            }

        # Load the yaml file to get crops (handle relative paths)
        yaml_path = Path(yaml_file)
        if not yaml_path.is_absolute():
            # Relative to config file directory
            yaml_path = config_file.parent / yaml_file

        if not yaml_path.exists():
            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "error": f"yaml_file does not exist: {yaml_path}",
            }

        with open(yaml_path, "r") as f:
            data_config = yaml.safe_load(f)

        # Get all datasets and their crops
        datasets = data_config.get("datasets", {})
        if not datasets:
            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "error": "No datasets found in yaml_file",
            }

        # Collect all crops with their raw paths
        all_crops = []
        for dataset_name, dataset_info in datasets.items():
            raw_path = dataset_info.get("raw", "")
            crops = dataset_info.get("crops", {})
            for crop_name, crop_path in crops.items():
                # Skip crops with "inference" in the name
                if "inference" in crop_name.lower():
                    continue
                all_crops.append((dataset_name, crop_name, crop_path, raw_path))

        total_crops = len(all_crops)
        print(f"\n{'='*60}")
        print(f"Run: {exp_group}/{setup_name}")
        print(f"Config: {config_file}")
        print(f"Data YAML: {yaml_path}")
        print(f"Labels to check: {', '.join(labels)}")
        print(f"Total crops to check: {total_crops}")
        print(f"{'='*60}\n")

        if total_crops == 0:
            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "error": "No crops found (or all crops have 'inference' in name)",
            }

        # Check all crops in parallel using 100 threads
        dataset_errors = {}  # Changed to group by dataset
        lock = Lock()
        progress_counter = [0]  # Use list to make it mutable in nested function

        with ThreadPoolExecutor(max_workers=100) as executor:
            # Submit all crop checks
            futures = {
                executor.submit(
                    check_crop,
                    dn,
                    cn,
                    cp,
                    rp,
                    labels,
                    progress_counter,
                    total_crops,
                    lock,
                ): (dn, cn)
                for dn, cn, cp, rp in all_crops
            }

            # Collect results
            for future in as_completed(futures):
                try:
                    crop_errors = future.result()
                    if crop_errors:
                        # Group errors by dataset, then by organelle
                        for key, value in crop_errors.items():
                            if key in ["dataset", "crop", "error", "scan_error"]:
                                # These are top-level errors - add to dataset group
                                dataset_name = crop_errors.get("dataset", "unknown")
                                if dataset_name not in dataset_errors:
                                    dataset_errors[dataset_name] = {}
                                if "crop_errors" not in dataset_errors[dataset_name]:
                                    dataset_errors[dataset_name]["crop_errors"] = []
                                dataset_errors[dataset_name]["crop_errors"].append(
                                    crop_errors
                                )
                                break
                            else:
                                # These are organelle-specific errors - group by dataset
                                for error_item in value:
                                    dataset_name = error_item.get("dataset", "unknown")
                                    if dataset_name not in dataset_errors:
                                        dataset_errors[dataset_name] = {}
                                    if key not in dataset_errors[dataset_name]:
                                        dataset_errors[dataset_name][key] = []
                                    dataset_errors[dataset_name][key].append(error_item)
                except Exception as e:
                    dataset_name, crop_name = futures[future]
                    print(f"❌ Error processing {dataset_name}/{crop_name}: {e}")

        print(f"\n{'='*60}")
        if dataset_errors:
            # Count total errors across all datasets
            total_errors = 0
            for dataset, organelles in dataset_errors.items():
                for organelle, errors in organelles.items():
                    if isinstance(errors, list):
                        total_errors += len(errors)
                    else:
                        total_errors += 1

            print(f"✅ Validation complete: Found {total_errors} error(s)")

            # Summary by dataset and organelle
            print("\nErrors by dataset:")
            for dataset in sorted(dataset_errors.keys()):
                organelles = dataset_errors[dataset]
                dataset_total = sum(
                    len(v) if isinstance(v, list) else 1 for v in organelles.values()
                )
                print(f"\n  {dataset}: {dataset_total} error(s)")
                for organelle in sorted(organelles.keys()):
                    errors = organelles[organelle]
                    if isinstance(errors, list):
                        print(f"    - {organelle}: {len(errors)} crop(s)")

            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "yaml_file": str(yaml_path),
                "total_crops_checked": total_crops,
                "dataset_errors": dataset_errors,
            }
        else:
            print(f"✅ Validation complete: No errors found!")
            return None

    except Exception as e:
        return {
            "experiment_group": exp_group if "exp_group" in locals() else "unknown",
            "setup": setup_name if "setup_name" in locals() else "unknown",
            "error": f"Error processing config: {str(e)}",
        }


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_single_run.py <path_to_config.yaml>")
        print("\nExample:")
        print(
            "  python check_single_run.py /groups/cellmap/cellmap/zouinkhim/exp_salivary/runs/setup_15/config.yaml"
        )
        sys.exit(1)

    config_file = Path(sys.argv[1])

    if not config_file.exists():
        print(f"❌ Error: Config file not found: {config_file}")
        sys.exit(1)

    if not config_file.name == "config.yaml":
        print(f"⚠️  Warning: File is not named 'config.yaml': {config_file.name}")

    print(f"🔍 Starting validation for: {config_file}")

    errors = validate_run_data(config_file)

    # Save errors to YAML
    if errors:
        output_dir = config_file.parent / "validation"
        output_dir.mkdir(parents=True, exist_ok=True)

        errors_file = output_dir / "errors.yaml"

        with open(errors_file, "w") as f:
            yaml.dump(errors, f, default_flow_style=False, sort_keys=False)

        print(f"\n📁 Errors saved to: {errors_file}")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print(f"{'='*60}\n")
        print("✅ No errors found - all crops validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
