# Complete Update Summary: Dataset Tracking Feature

## 🎯 Overview

Successfully implemented comprehensive dataset tracking across the experiment overview system, including both CSV data files and interactive website visualizations.

## 📋 Files Modified

### 1. Core Script Updates

**`scripts/generate_overview_csv.py`**
- Added `datasets_used` field to `ExperimentEntry` dataclass
- Created `extract_dataset_info_from_yaml()` function to parse training YAML files
- Created `get_yaml_file_path()` function to locate YAML files
- Updated all scan functions to return data usage information
- Created `write_data_usage_yaml()` function to export detailed usage
- Updated main() to generate both CSV and YAML outputs

**`scripts/generate_timeline.py`**
- Updated `create_timeline_graph()` hover tooltips to show dataset usage
- Updated `create_gantt_chart()` hover tooltips to show dataset usage
- Created new `create_dataset_usage_stats()` function for dataset visualizations
- Updated main landing page HTML to include dataset usage links
- Added dataset usage page generation to main script execution

## 📊 Generated Outputs

### Data Files

1. **`data/processed/auto_generated_overview.csv`**
   - New column: "Datasets Used"
   - Format: "dataset1: X crops; dataset2: Y crops; ..."
   - 69 experiments with dataset information

2. **`data/processed/data_usage_overview.yaml`**
   - Complete crop-level tracking
   - Structure: setup → dataset → [crop1, crop2, ...]
   - 5,033 lines of detailed usage data

### Website Files

3. **`output/visualizations/index.html`**
   - Updated main landing page
   - Added "Dataset Usage" card
   - Added "Data Usage YAML" download link

4. **`output/visualizations/experiment_timeline.html`**
   - Updated hover tooltips with dataset information

5. **`output/visualizations/experiment_gantt.html`**
   - Updated hover tooltips with dataset information

6. **`output/visualizations/dataset_usage.html`** ✨ NEW
   - 4 interactive visualizations:
     * Dataset Usage Frequency (Top 20)
     * Total Crops per Dataset (Top 20)
     * Most Reused Crops (Top 20)
     * Experiments per Dataset Distribution

## 📚 Documentation Created

1. **`docs/DATASET_TRACKING.md`**
   - Feature overview and implementation details
   - Usage instructions
   - File format documentation

2. **`docs/WEBSITE_UPDATE.md`**
   - Complete website changes documentation
   - Technical implementation details
   - Future enhancement ideas

## 🔄 Workflow

### Data Generation Flow
```
config.yaml (paths.yaml_file)
    ↓
Training YAML file (datasets → crops)
    ↓
extract_dataset_info_from_yaml()
    ↓
├─→ CSV: Summary format (dataset: count)
└─→ YAML: Detailed format (dataset → [crops])
```

### Visualization Flow
```
auto_generated_overview.csv + data_usage_overview.yaml
    ↓
generate_timeline.py
    ↓
├─→ index.html (landing page)
├─→ experiment_timeline.html (updated tooltips)
├─→ experiment_gantt.html (updated tooltips)
└─→ dataset_usage.html (NEW statistics page)
```

## ✅ Testing & Validation

- ✅ All 69 experiments have dataset information
- ✅ CSV properly formatted with new column
- ✅ YAML file correctly structured
- ✅ Website generates without errors
- ✅ All hover tooltips display dataset info
- ✅ New dataset usage page renders correctly
- ✅ Landing page links work properly

## 🚀 Usage Instructions

### Generate All Data and Visualizations

```bash
cd /groups/cellmap/cellmap/zouinkhim/exp-overview

# Step 1: Generate CSV and YAML with dataset tracking
python scripts/generate_overview_csv.py

# Step 2: Generate website visualizations
python3 scripts/generate_timeline.py
```

### Output Locations

```
data/processed/
├── auto_generated_overview.csv    # CSV with Datasets Used column
└── data_usage_overview.yaml       # Detailed crop-level data

output/visualizations/
├── index.html                     # Updated landing page
├── experiment_timeline.html       # Timeline with dataset tooltips
├── experiment_gantt.html          # Gantt with dataset tooltips
├── experiment_stats.html          # General statistics
└── dataset_usage.html             # NEW: Dataset usage stats
```

## 📈 Key Statistics

- **Total Experiments Tracked**: 69
- **Experiments with Dataset Info**: 69 (100%)
- **Total YAML Lines**: 5,033
- **Website Files Generated**: 5 HTML files
- **New Visualizations**: 4 dataset usage charts

## 🎨 Visualization Features

### Timeline & Gantt Charts (Updated)
- Hover over any experiment to see:
  - All previous information (target, model, status, etc.)
  - **NEW**: Datasets Used with crop counts

### Dataset Usage Page (NEW)
1. **Top Datasets by Frequency**: Which datasets are most popular
2. **Crops per Dataset**: Dataset annotation coverage
3. **Most Reused Crops**: High-quality/trusted training data
4. **Distribution Analysis**: Usage pattern statistics

## 🔗 Integration

The dataset tracking feature is fully integrated:
- ✅ Data generation (CSV + YAML)
- ✅ Website visualization (hover info)
- ✅ Dedicated statistics page
- ✅ Landing page navigation
- ✅ Documentation complete

## 🎯 Benefits

1. **Data Transparency**: See exactly what data trains each model
2. **Resource Planning**: Identify underutilized datasets
3. **Quality Tracking**: Find trusted, reused crops
4. **Reproducibility**: Complete data provenance
5. **Collaboration**: Share detailed usage information
6. **Analysis**: Understand data distribution patterns

## 📝 Notes

- Dataset information is extracted from the `yaml_file` referenced in each experiment's `config.yaml`
- The script searches multiple locations for YAML files (run dir, preparation/yamls/generated/, yamls/)
- Non-crop entries (inference_upscale, raw, contrast) are automatically filtered out
- All visualizations are interactive with Plotly, allowing zoom, pan, and detailed exploration

## ✨ Result

A comprehensive dataset tracking system that provides complete visibility into which datasets and crops are used for training each machine learning model, with both detailed data files and interactive visualizations for exploration and analysis.
