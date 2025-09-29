# Project Configuration
# =====================

# Main experiment directories to scan
EXPERIMENT_DIRS = [
    "exp_cell",
    "exp_cerebellum",
    "exp_pancreas",
    "exp_c-elegen",
    "ex_mito",
    "exp_salivary",
]

# Base path for experiments (relative to repository root)
BASE_EXPERIMENT_PATH = "/groups/cellmap/cellmap/zouinkhim"

# Output paths
DATA_RAW_PATH = "data/raw"
DATA_PROCESSED_PATH = "data/processed"
OUTPUT_REPORTS_PATH = "output/reports"
OUTPUT_VIZ_PATH = "output/visualizations"

# File naming
MAIN_OUTPUT_CSV = "auto_generated_overview.csv"
ORIGINAL_CSV = "overview.csv"
COMPARISON_REPORT = "comparison_report.md"

# Detection settings
ORGANELLE_PATTERNS = [
    "mito",
    "nuc",
    "cell",
    "er",
    "ld",
    "lyso",
    "perox",
    "yolk",
    "ecs",
    "isg",
]

# Model types
MODEL_TYPES = ["fly model", "isolated_unet"]
