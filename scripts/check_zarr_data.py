#!/usr/bin/env python3
"""
Zarr Data Validation
Checks if organelle zarr data exists and is non-empty for all crops in experiment runs
"""

import yaml
from pathlib import Path
import zarr
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


def collect_configs_from_runs():
    """
    Scan all experiment directories for config.yaml files
    """
    base_path = Path("/groups/cellmap/cellmap/zouinkhim")

    # Find all config.yaml files in exp_* directories
    config_files = []
    for exp_dir in base_path.glob("exp_*/runs/*/config.yaml"):
        config_files.append(exp_dir)

    print(f"Found {len(config_files)} config files")
    return config_files


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
        # For large arrays, we'll sample to avoid loading everything into memory
        if hasattr(z, "shape"):
            if z.size == 0:
                return True, False, "Zarr array is empty (size=0)"

            # Sample a small region efficiently to check if there's any data
            # This is much more efficient than loading the entire array
            try:
                # Sample a small region from the center of the array
                sample_size = min(100, *z.shape)

                # Get center coordinates
                center = tuple(s // 2 for s in z.shape)

                # Create slices for a small sample region around the center
                slices = tuple(
                    slice(max(0, c - sample_size // 2), min(s, c + sample_size // 2))
                    for c, s in zip(center, z.shape)
                )

                # Sample the data
                sample = z[slices]

                # Check if any values are non-zero
                has_any = np.any(sample)
                if not has_any:
                    return (
                        True,
                        False,
                        "Sampled region is all zeros (may need manual verification)",
                    )
                return True, True, None
            except Exception as e:
                return True, False, f"Error reading data: {str(e)}"
        else:
            return False, False, "Not a valid zarr array"

    except Exception as e:
        return False, False, f"Unexpected error: {str(e)}"


def validate_run_data(config_file):
    """
    Validate zarr data for a single run based on its config

    Returns:
        dict: Error information for this run
    """
    run_errors = {}

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Extract run information from path
        parts = config_file.parts
        exp_group = parts[-4]  # exp_salivary
        setup_name = parts[-2]  # setup_15

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

        # Check each dataset's crops for each organelle
        organelle_errors = {}

        for dataset_name, dataset_info in datasets.items():
            crops = dataset_info.get("crops", {})
            if not crops:
                continue

            for crop_name, crop_path in crops.items():
                # Skip crops with "inference" in the name
                if "inference" in crop_name.lower():
                    continue

                crop_path = Path(crop_path)
                print(
                    f"  Checking dataset: {dataset_name}, crop: {crop_name} at {crop_path}"
                )

                if not crop_path or not crop_path.exists():
                    if "path_errors" not in organelle_errors:
                        organelle_errors["path_errors"] = []
                    organelle_errors["path_errors"].append(
                        {
                            "dataset": dataset_name,
                            "crop": crop_name,
                            "error": f"Crop path does not exist: {crop_path}",
                        }
                    )
                    continue

                # List all directories in crop_path (these should be organelles)
                try:
                    for item in crop_path.iterdir():
                        if item.is_dir() and not item.name.startswith("."):
                            organelle = item.name

                            # Check if s0 exists
                            s0_path = item / "s0"

                            exists, has_data, error_msg = check_zarr_data(s0_path)

                            if not exists or not has_data:
                                if organelle not in organelle_errors:
                                    organelle_errors[organelle] = []

                                organelle_errors[organelle].append(
                                    {
                                        "dataset": dataset_name,
                                        "crop": crop_name,
                                        "crop_path": str(crop_path),
                                        "zarr_path": str(s0_path),
                                        "error": (
                                            error_msg if error_msg else "No data found"
                                        ),
                                    }
                                )
                except Exception as e:
                    if "scan_errors" not in organelle_errors:
                        organelle_errors["scan_errors"] = []
                    organelle_errors["scan_errors"].append(
                        {
                            "dataset": dataset_name,
                            "crop": crop_name,
                            "crop_path": str(crop_path),
                            "error": f"Error scanning directory: {str(e)}",
                        }
                    )

        if organelle_errors:
            return {
                "experiment_group": exp_group,
                "setup": setup_name,
                "yaml_file": str(yaml_file),
                "organelle_errors": organelle_errors,
            }

        return None  # No errors

    except Exception as e:
        parts = config_file.parts
        return {
            "experiment_group": parts[-4] if len(parts) >= 4 else "unknown",
            "setup": parts[-2] if len(parts) >= 2 else "unknown",
            "error": f"Error processing config: {str(e)}",
        }


def main():
    print("🔍 Scanning for config.yaml files...")
    config_files = collect_configs_from_runs()

    if not config_files:
        print("❌ No config files found!")
        return

    print(f"✅ Found {len(config_files)} config files")
    print(f"🔬 Validating zarr data using 100 threads...\n")

    all_errors = {}
    runs_with_errors = 0
    runs_checked = 0

    # Thread-safe lock for updating shared data
    lock = Lock()

    def process_config(config_file):
        """Process a single config file"""
        result_msg = f"Checking {config_file.parts[-4]}/{config_file.parts[-2]}... "

        errors = validate_run_data(config_file)

        with lock:
            nonlocal runs_checked, runs_with_errors
            runs_checked += 1

        if errors:
            run_key = f"{errors['experiment_group']}/{errors['setup']}"

            with lock:
                all_errors[run_key] = errors
                runs_with_errors += 1

            # Count organelle errors
            if "organelle_errors" in errors:
                error_count = sum(
                    len(crops) for crops in errors["organelle_errors"].values()
                )
                result_msg += f"⚠️  {error_count} error(s) found"
            else:
                result_msg += f"⚠️  Configuration error"
        else:
            result_msg += "✅ OK"

        print(result_msg)
        return errors

    # Use ThreadPoolExecutor with 100 threads
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Submit all tasks
        futures = {executor.submit(process_config, cf): cf for cf in config_files}

        # Wait for all to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                config_file = futures[future]
                print(f"❌ Error processing {config_file}: {e}")

    # Save errors to YAML
    output_dir = Path("output/validation")
    output_dir.mkdir(parents=True, exist_ok=True)

    errors_file = output_dir / "errors.yaml"

    with open(errors_file, "w") as f:
        yaml.dump(all_errors, f, default_flow_style=False, sort_keys=False)

    print(f"\n{'='*60}")
    print(f"📊 Validation Summary:")
    print(f"   Total runs checked: {runs_checked}")
    print(f"   Runs with errors: {runs_with_errors}")
    print(f"   Runs OK: {runs_checked - runs_with_errors}")
    print(f"\n📁 Errors saved to: {errors_file}")

    if runs_with_errors > 0:
        print(f"\n⚠️  Found errors in {runs_with_errors} run(s)")
        print("\nSample errors by organelle:")

        # Summarize errors by organelle
        organelle_summary = {}
        for run_key, run_errors in all_errors.items():
            if "organelle_errors" in run_errors:
                for organelle, crops in run_errors["organelle_errors"].items():
                    if organelle not in organelle_summary:
                        organelle_summary[organelle] = 0
                    organelle_summary[organelle] += len(crops)

        for organelle, count in sorted(
            organelle_summary.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"   {organelle}: {count} crop error(s)")
    else:
        print("\n✅ All runs validated successfully!")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
