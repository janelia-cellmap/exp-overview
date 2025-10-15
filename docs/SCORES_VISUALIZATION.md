# Model Scores Visualization

## Overview

The scores visualization feature automatically collects and visualizes model performance metrics from all experiment runs. It groups scores by organelle type, allowing you to compare model performance across different setups and experiment groups.

## Score File Format

Score files should be YAML files located at:
```
exp_<group>/runs/<setup>/scores.yaml
```

Example structure:
```yaml
model_checkpoint_10000:
  jrc_c-elegans-bw-1:
    crop495:
      mito:
        f1: 0.535552064330222
        accuracy: 0.9485093355178833
        val_loss: 0.6820682287216187
```

## Generated Visualizations

### 1. Scores by Organelle (`scores_by_organelle.html`)
- Interactive bar charts grouped by organelle type
- Compare F1 scores across all setups for each organelle
- Color-coded by experiment group
- Hover for detailed metrics including accuracy and validation loss

### 2. Best Performing Models (`best_scores.html`)
- Table showing the best F1 score achieved for each organelle
- Includes full metrics and model configuration details
- Sorted by F1 score (highest first)

### 3. Metrics Correlation (`metrics_correlation.html`)
- Scatter plots showing relationships between metrics:
  - F1 vs Accuracy
  - F1 vs Validation Loss
- Color-coded by organelle type
- Helps identify metric patterns and outliers

### 4. Group Performance Comparison (`group_comparison.html`)
- Box plots showing F1 score distribution by experiment group
- Visualize median, quartiles, and outliers
- Compare performance across different experimental approaches

## Usage

### Generate Scores Visualizations

```bash
cd /groups/cellmap/cellmap/zouinkhim/exp-overview
python scripts/generate_scores.py
```

### View Results

Open the generated HTML files in your browser:
```bash
# View all visualizations on the main dashboard
open output/visualizations/index.html

# Or view individual score pages
open output/visualizations/scores_by_organelle.html
open output/visualizations/best_scores.html
open output/visualizations/metrics_correlation.html
open output/visualizations/group_comparison.html
```

## Integration with Main Dashboard

The scores visualizations are automatically integrated into the main experiment timeline dashboard (`index.html`). New visualization cards are added to the dashboard:

- 🎯 **Model Scores by Organelle** - Main scores comparison view
- 🏆 **Best Performing Models** - Top performers table
- 📊 **Metrics Correlation** - Metric relationships
- 📦 **Group Performance Comparison** - Group-level analysis

## Automation

To automatically generate scores visualizations along with the timeline:

1. Add scores generation to the daily update script:
   ```bash
   # Edit scripts/daily_update.sh to include:
   python scripts/generate_scores.py
   ```

2. Or run both scripts together:
   ```bash
   python scripts/generate_timeline.py && python scripts/generate_scores.py
   ```

## Metrics Tracked

Each score record includes:
- **F1 Score**: Harmonic mean of precision and recall
- **Accuracy**: Overall classification accuracy
- **Validation Loss**: Model loss on validation data
- **Checkpoint**: Model checkpoint iteration
- **Dataset**: Source dataset name
- **Crop**: Specific crop used for validation
- **Organelle**: Target organelle type

## Adding New Score Files

Simply add a `scores.yaml` file to any experiment run directory:
```
/groups/cellmap/cellmap/zouinkhim/exp_<group>/runs/<setup>/scores.yaml
```

The next time you run `generate_scores.py`, it will automatically be included in the visualizations.

## Troubleshooting

### No scores found
- Ensure your score files follow the correct YAML structure
- Check that files are named `scores.yaml` (not `score.yaml` or other variations)
- Verify files are in the correct path: `exp_*/runs/*/scores.yaml`

### Visualization not updating
- Re-run `python scripts/generate_scores.py` after adding new score files
- Check for YAML syntax errors in score files
- Verify the script has read permissions for all experiment directories

## Future Enhancements

Potential improvements to the scores visualization system:
- Track scores over time (multiple checkpoints)
- Add statistical significance testing
- Include precision/recall breakdown
- Compare against baseline models
- Export scores to CSV for external analysis
