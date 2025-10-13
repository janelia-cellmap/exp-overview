# Dataset Tracking - Quick Reference Guide

## 🚀 Quick Start

### Generate Everything
```bash
cd /groups/cellmap/cellmap/zouinkhim/exp-overview
python scripts/generate_overview_csv.py  # Generate CSV + YAML
python3 scripts/generate_timeline.py      # Generate website
```

## 📁 Key Files

| File | Purpose | Size |
|------|---------|------|
| `data/processed/auto_generated_overview.csv` | CSV with "Datasets Used" column | 20K |
| `data/processed/data_usage_overview.yaml` | Detailed crop-level tracking | 64K |
| `output/visualizations/index.html` | Main landing page | 14K |
| `output/visualizations/dataset_usage.html` | Dataset statistics page | 4.6M |

## 🔍 What's New

### CSV Format
```
...,Datasets Used
...,jrc_c-elegans-P3_E5_D1_N2: 5; jrc_c-elegans-bw-1: 4; jrc_cos7-1a: 10
```

### YAML Format
```yaml
setup_20:
  jrc_c-elegans-P3_E5_D1_N2:
    - crop1047
    - crop1048
    - crop1049
  jrc_c-elegans-bw-1:
    - crop518
    - crop519
```

## 🌐 Website Updates

### New Pages
- **Dataset Usage**: `/output/visualizations/dataset_usage.html`
  - 4 interactive charts showing dataset usage patterns

### Updated Pages
- **Timeline**: Now shows dataset info in hover tooltips
- **Gantt Chart**: Now shows dataset info in hover tooltips
- **Landing Page**: New cards for dataset usage and YAML download

## 📊 Visualizations

### Dataset Usage Page Includes:
1. **Dataset Usage Frequency** - Which datasets are most used
2. **Total Crops per Dataset** - Dataset coverage
3. **Most Reused Crops** - Popular training data
4. **Distribution Analysis** - Usage patterns

## 💡 Use Cases

### Find which datasets a specific run uses:
```bash
# CSV approach
grep "setup_20" data/processed/auto_generated_overview.csv | cut -d',' -f14

# YAML approach
grep -A 20 "^setup_20:" data/processed/data_usage_overview.yaml
```

### Count experiments using a specific dataset:
```bash
grep "jrc_c-elegans" data/processed/auto_generated_overview.csv | wc -l
```

### List all crops from a specific dataset:
```bash
grep -A 100 "jrc_c-elegans-P3_E5_D1_N2:" data/processed/data_usage_overview.yaml | grep "crop"
```

## 🔧 Technical Details

### Data Source Chain
```
config.yaml → yaml_file path → training YAML → datasets & crops
```

### Processing Flow
```
1. Read config.yaml from each run
2. Extract paths.yaml_file reference
3. Load training YAML file
4. Parse datasets and crops sections
5. Generate summary (CSV) and details (YAML)
6. Create visualizations
```

## ✅ Verification

### Check CSV has dataset column:
```bash
head -1 data/processed/auto_generated_overview.csv | grep "Datasets Used"
```

### Count experiments with dataset info:
```bash
awk -F',' 'NR>1 && $14!="" {count++} END {print count}' data/processed/auto_generated_overview.csv
```

### Check YAML structure:
```bash
head -20 data/processed/data_usage_overview.yaml
```

### Verify website files:
```bash
ls -lh output/visualizations/*.html
```

## 🎯 Statistics

- **Total Experiments**: 69
- **With Dataset Info**: 69 (100%)
- **Setups Tracked in YAML**: 41
- **Website Pages**: 5 HTML files
- **Dataset Visualizations**: 4 charts

## 📞 Support

- Main documentation: `docs/DATASET_TRACKING.md`
- Website updates: `docs/WEBSITE_UPDATE.md`
- Complete summary: `DATASET_TRACKING_COMPLETE.md`

## 🎉 Success Indicators

✅ CSV has "Datasets Used" column  
✅ YAML file exists with proper structure  
✅ Website generates without errors  
✅ dataset_usage.html created  
✅ Hover tooltips show dataset info  
✅ Landing page has dataset links  

All systems operational! 🚀
