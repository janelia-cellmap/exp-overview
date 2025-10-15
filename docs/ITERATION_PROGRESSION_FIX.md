# Iteration Progression - Fixed Design

## Problem
The previous iteration progression chart was **unreadable**:
- ❌ All setups plotted on same chart with same colors
- ❌ Lines overlapping everywhere
- ❌ Too many lines to distinguish
- ❌ Legend crowded with duplicate experiment group names
- ❌ Couldn't tell which line was which setup

## Solution: Separate Charts with Distinct Colors

### Key Changes

#### 1. **One Full-Page Chart Per Organelle** ✅
- Each organelle gets its own dedicated page
- No cramped subplots
- Full space to show all setups clearly

#### 2. **Each Setup Gets Unique Color** ✅
- 10 distinct colors in palette
- No more "all same color because same experiment group"
- Easy to distinguish different setups
- Legend shows setup name only (not redundant group info)

#### 3. **Only Show Setups with Multiple Iterations** ✅
- Filters out single-checkpoint setups (nothing to track)
- Only shows meaningful progression data
- Cleaner, less cluttered

#### 4. **Bigger, Clearer Markers** ✅
- Larger markers (size 10) with white borders
- Thicker lines (width 3)
- Easy to see individual data points
- Can distinguish overlapping lines

#### 5. **Better Hover Info** ✅
```
Setup: setup_15
Iteration: 10,000
F1 Score: 0.8590
Group: exp_salivary
```
- Shows all relevant info
- Iteration with thousand separator
- Includes experiment group for context

#### 6. **Grid Lines for Reference** ✅
- Light gray gridlines
- Easier to read values
- Better visual alignment

## File Structure

```
iteration_progression.html           ← Summary page with cards
├── iteration_progression_mito.html  ← MITO training curves
└── iteration_progression_isg.html   ← ISG training curves (if exists)
```

## Visual Design

### Before (Confusing)
```
All in one cramped subplot:
- setup_10 (salivary) [purple]
- setup_15 (salivary) [purple]  ← Same color!
- setup_20 (salivary) [purple]  ← Can't tell apart!
- setup_05 (mito) [red]
- setup_07 (mito) [red]         ← Same color!
```

### After (Clear)
```
MITO page - Full screen chart:
- setup_10 [Red]
- setup_15 [Teal]      ← Each gets unique color
- setup_20 [Blue]
- setup_05 [Green]
- setup_07 [Purple]
```

## Features

### Clean Legend
- Setup names only (e.g., "setup_15")
- No redundant "(salivary)" suffix
- Positioned in corner with white background
- Bordered for clarity

### Smart Filtering
- Only includes setups with 2+ checkpoints
- No clutter from single-evaluation runs
- Summary page shows count: "X setups with multiple checkpoints"

### Formatted Axes
- X-axis: Iteration with thousand separators (10,000 not 10000)
- Y-axis: F1 Score from 0 to 1.0
- Both axes have descriptive labels
- Grid for easy value reading

## Benefits

✅ **Readable:** Each line is visually distinct  
✅ **Clear:** No overlapping same-color lines  
✅ **Informative:** See which setups improve fastest  
✅ **Actionable:** Identify when to stop training  
✅ **Scalable:** Each organelle gets full page  

## Use Cases

### 1. Compare Training Speed
- See which setup reaches high F1 fastest
- Identify efficient configurations
- Decide which approach to use for new experiments

### 2. Find Optimal Stopping Point
- See when line flattens (no more improvement)
- Avoid wasting compute on overtraining
- Know which checkpoint to deploy

### 3. Detect Issues
- Sharp drops indicate training problems
- Plateaus show convergence
- Unstable lines suggest hyperparameter issues

## Example Workflow

**Goal:** "When should I stop training setup_15 for mitochondria?"

1. Open `iteration_progression.html`
2. Click "MITO" card
3. Find `setup_15` line (unique color, e.g., teal)
4. See progression: 10k→0.54, 20k→0.75, 30k→0.82, 40k→0.83
5. **Answer:** Plateau after 30k iterations, can stop training

## Technical Details

- **Color Palette:** 10 distinct colors, cycles if >10 setups
- **Marker Size:** 10px with 1px white border
- **Line Width:** 3px for visibility
- **Chart Height:** 600px (plenty of vertical space)
- **Y-axis Range:** Fixed 0-1.0 for consistency
- **Grid:** Light gray, subtle but helpful

## What Makes This Better

**Before:** Trying to read spaghetti of purple lines all tangled together

**After:** Clean, distinct colored lines each showing one setup's journey

The difference is like trying to follow one strand in a ball of yarn vs. following colored ribbons laid out separately. Much clearer!
