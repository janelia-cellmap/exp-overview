# Simplified Scores Visualization - Design Decisions

## Problem
The previous visualizations were confusing and not informative:
- Too many subplots crammed together
- Hard to compare setups
- Metrics correlation didn't provide actionable insights
- Box plots were unclear

## Solution: Simple, Clear, Actionable

### 1. **Organelle-Specific Pages** ✅
**What:** One clean horizontal bar chart per organelle
- **Why:** Easy to read, clear ranking of setups
- **Shows:** Best iteration for each setup (no duplicates)
- **Sorted:** Ascending F1 score (worst to best)
- **Color:** Coded by experiment group
- **Labels:** F1 score displayed on each bar
- **Details:** Hover shows accuracy, val_loss, dataset

**Example:**
```
MITO - F1 Scores by Setup
┌────────────────────────────────────┐
setup_10 (iter 10000) ████████ 0.8590
setup_15 (iter 10000) █████ 0.5356
setup_20 (iter 15000) ███ 0.2542
```

### 2. **Summary Landing Page** ✅
**What:** Card-based overview with links
- **Shows:** Best F1 for each organelle
- **Quick stats:** Total evaluations, setups tested
- **Clear CTA:** "View Detailed Results" button per organelle

### 3. **Best Scores Table** ✅
**What:** Simple table showing top performer per organelle
- **Columns:** Organelle, F1, Accuracy, Val Loss, Iteration, Setup, Experiment, Dataset
- **Purpose:** Quick reference for best models

### 4. **Iteration Progression** ✅
**What:** Line charts showing F1 improvement over iterations
- **Only shows:** Setups with multiple checkpoints
- **Purpose:** Track training progress, identify plateau
- **Useful for:** Deciding when to stop training

## What Was Removed (and Why)

### ❌ Metrics Correlation Scatter Plots
- **Removed because:** Not actionable
- F1 vs Accuracy scatter doesn't help choose models
- Validation loss relationship is dataset-dependent

### ❌ Box Plots by Experiment Group
- **Removed because:** Too abstract
- Users care about specific setups, not group distributions
- Organelle-specific rankings are more useful

### ❌ Multi-subplot Grid
- **Removed because:** Cramped and hard to read
- Individual pages per organelle are clearer
- Easier to share specific results

## New Structure

```
scores_by_organelle.html    ← Landing page with all organelles
├── scores_mito.html        ← MITO detailed rankings
├── scores_isg.html         ← ISG detailed rankings
└── scores_<organelle>.html ← One per organelle

best_scores.html            ← Quick reference table
iteration_progression.html  ← Training curves (if data exists)
```

## Key Design Principles

### 1. **One Question Per Page**
- Landing page: "Which organelles have I tested?"
- Organelle page: "Which setup is best for this organelle?"
- Best scores: "What's my top score for each organelle?"
- Progression: "Is my model still improving?"

### 2. **Horizontal Bars > Vertical Bars**
- Setup names are long → horizontal is easier to read
- Sorted ascending → best models at the top (visual priority)

### 3. **Show Iteration in Label**
- `setup_15 (iter 10000)` tells complete story
- No need to hover to see checkpoint info
- Instant understanding of which checkpoint was used

### 4. **Color = Context**
- Color by experiment group shows which project
- Not used for ranking (F1 score does that)
- Helps identify related setups

### 5. **Hover = Details**
- Don't clutter the main view
- Accuracy, val_loss, dataset in hover
- F1 score visible without hover

## User Workflows

### "Which is my best setup for mitochondria?"
1. Click "View Scores" → Landing page
2. See MITO card shows best F1
3. Click "View Detailed Results"
4. See full ranking → top setup at bottom

### "Has my model stopped improving?"
1. Click "Training Progression"
2. Find your setup's line
3. See if slope flattens → can stop training

### "Quick lookup: what's the best score?"
1. Click "Best Scores"
2. Table shows top performer for each organelle
3. Note the iteration number for reloading

## Generated Files

| File | Purpose | Content |
|------|---------|---------|
| `scores_by_organelle.html` | Main entry point | Summary cards for all organelles |
| `scores_<organelle>.html` | Detailed ranking | Horizontal bar chart for one organelle |
| `best_scores.html` | Quick reference | Table of top scores |
| `iteration_progression.html` | Training analysis | Line charts (only if multi-checkpoint data exists) |

## What Makes This Better

✅ **Clear:** One organelle, one chart, easy ranking  
✅ **Actionable:** Immediately see which setup to use  
✅ **Informative:** Iteration shown inline, no guessing  
✅ **Scalable:** Adding organelles just adds new pages  
✅ **Shareable:** Send direct link to specific organelle results  

## Example Use Case

**Scenario:** Testing 10 setups for mitochondria segmentation

**Old way (confusing):**
- Open subplot grid with 2 organelles
- Find MITO subplot (small, cramped)
- Read vertical labels at 45° angle
- Hover each bar to see which iteration
- Compare 10 bars in tiny subplot

**New way (clear):**
- Click "MITO" from landing page
- See full-page horizontal bar chart
- Setup names readable (horizontal)
- Iteration shown in label
- F1 scores labeled on bars
- Sorted best-to-worst → top setup obvious
