# Iteration Tracking in Scores Visualization

## Overview

The scores visualization system now properly tracks and displays training iteration information from checkpoint names (e.g., `model_checkpoint_10000` → iteration 10000).

## What's New

### 1. **Iteration Extraction**
- Automatically extracts iteration numbers from checkpoint names
- Handles format: `model_checkpoint_<iteration>` 
- Example: `model_checkpoint_10000` → `iteration: 10000`

### 2. **Enhanced Visualizations**

#### All Existing Pages Now Show Iterations:
- **Scores by Organelle** - Hover shows iteration number for each score
- **Best Scores Table** - New "Iteration" column showing at which iteration the best score was achieved
- **Metrics Correlation** - Iteration info in hover tooltips
- **Group Comparison** - Iteration context preserved

#### New Visualization:
- **📈 Training Iteration Progression** (`iteration_progression.html`)
  - Line charts showing F1 score improvement over training iterations
  - Separate plots for each organelle type
  - Each setup shown as a separate line
  - Color-coded by experiment group
  - Track training progress and identify optimal stopping points

## Score File Format

Your `scores.yaml` files should follow this structure:

```yaml
model_checkpoint_10000:  # ← Iteration number extracted from here (10000)
  jrc_c-elegans-bw-1:
    crop495:
      mito:
        f1: 0.535552064330222
        accuracy: 0.9485093355178833
        val_loss: 0.6820682287216187

model_checkpoint_20000:  # ← Another checkpoint at iteration 20000
  jrc_c-elegans-bw-1:
    crop495:
      mito:
        f1: 0.582341234567890
        accuracy: 0.9521234567890123
        val_loss: 0.6543210987654321
```

## Multiple Checkpoints per Setup

You can track multiple checkpoints for the same setup to see training progression:

```yaml
model_checkpoint_5000:
  # scores at 5k iterations
  
model_checkpoint_10000:
  # scores at 10k iterations
  
model_checkpoint_15000:
  # scores at 15k iterations
  
model_checkpoint_20000:
  # scores at 20k iterations
```

The **Iteration Progression** chart will automatically plot these as a line graph showing improvement over time.

## Viewing Iteration Information

### In Hover Tooltips
All visualizations now include iteration information when you hover over data points:
```
Setup: setup_15
Group: exp_salivary
Iteration: 10000  ← Shows the training iteration
F1: 0.5356
Accuracy: 0.9485
Val Loss: 0.6821
```

### In Best Scores Table
The table now includes an "Iteration" column:
| Organelle | Best F1 | Accuracy | Val Loss | **Iteration** | Setup | Experiment |
|-----------|---------|----------|----------|---------------|-------|------------|
| mito      | 0.8590  | 0.9873   | 0.6816   | **10000**     | setup_15 | salivary |

### In Progression Charts
The new iteration progression visualization shows:
- X-axis: Training iteration (5000, 10000, 15000, etc.)
- Y-axis: F1 Score
- Lines: Each setup's progression
- Separate subplots for each organelle

## Use Cases

### 1. **Identify Optimal Training Duration**
See when models plateau or start overfitting by viewing the iteration progression chart.

### 2. **Compare Training Efficiency**
Compare how quickly different setups reach high F1 scores across iterations.

### 3. **Track Multiple Checkpoints**
Add multiple checkpoint evaluations to your `scores.yaml` to see continuous improvement.

### 4. **Find Best Checkpoint**
Quickly identify which iteration produced the best results for each organelle in the Best Scores table.

## Generated Files

All score visualizations are saved to `output/visualizations/`:

1. `scores_by_organelle.html` - Bar charts with iteration info in hover
2. `best_scores.html` - Table with iteration column
3. `metrics_correlation.html` - Scatter plots with iteration context
4. `group_comparison.html` - Box plots by experiment group
5. `iteration_progression.html` - **NEW:** Line charts showing score vs iteration
6. All linked from `index.html` main dashboard

## Regenerating Visualizations

```bash
# Generate all scores visualizations (including iteration tracking)
python scripts/generate_scores.py

# Or use the main run script
./run.sh
```

## Example Output

The iteration progression chart will show something like:

```
MITO - F1 Score by Iteration
┌─────────────────────────────────────┐
│ 1.0 ┤                                │
│     │                     setup_15   │
│ 0.8 ┤              ●──●──●──●        │
│     │         ●─●─●                  │
│ 0.6 ┤    ●──●          setup_20      │
│     │   ●                            │
│ 0.4 ┤  ●                             │
│     │                                │
│ 0.2 ┤                                │
│     └────────────────────────────────│
│     5k   10k  15k  20k  25k  30k    │
│           Training Iterations        │
└─────────────────────────────────────┘
```

This helps you:
- See which setups train faster
- Identify when to stop training
- Compare convergence patterns
- Find the best checkpoint for deployment
