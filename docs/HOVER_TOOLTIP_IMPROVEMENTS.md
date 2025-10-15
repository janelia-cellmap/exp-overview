# Hover Tooltip Improvements

## 🎯 Changes Made

### Problem
When experiments used many datasets, the hover tooltip displayed them in a single long line, making it difficult to read and causing the popup to extend off-screen.

### Solution
Implemented formatted dataset display with line breaks and better styling.

## ✨ Features

### 1. Line-by-Line Dataset Display

**Before:**
```
Datasets Used: jrc_dataset1: 5; jrc_dataset2: 10; jrc_dataset3: 8; jrc_dataset4: 12; ...
```

**After:**
```
Datasets Used:
  • jrc_dataset1: 5
  • jrc_dataset2: 10
  • jrc_dataset3: 8
  • jrc_dataset4: 12
  ...
```

### 2. Automatic Truncation

To prevent extremely long tooltips, the display is limited to the first 15 datasets:
- Shows first 15 datasets with full details
- Adds "... and X more" indicator if there are additional datasets
- Keeps tooltips readable while providing comprehensive information

### 3. Improved Styling

**Enhanced hover label properties:**
- **Background**: Clean white background
- **Font**: Monospace font for better alignment
- **Alignment**: Left-aligned for easier reading
- **Font Size**: Consistent 12px for readability

## 📝 Implementation Details

### New Function: `format_datasets_for_hover()`

Located in: `scripts/generate_timeline.py`

```python
def format_datasets_for_hover(datasets_str):
    """
    Format the datasets string for better display in hover tooltips.
    Converts semicolon-separated list to line breaks.
    """
    if pd.isna(datasets_str) or datasets_str == "" or datasets_str == "N/A":
        return "N/A"
    
    # Split by semicolon and rejoin with HTML line breaks
    datasets = datasets_str.split(";")
    
    # Limit to first 15 datasets to avoid extremely long tooltips
    if len(datasets) > 15:
        displayed = datasets[:15]
        formatted = "<br>  • ".join([d.strip() for d in displayed])
        return f"<br>  • {formatted}<br>  ... and {len(datasets) - 15} more"
    else:
        formatted = "<br>  • ".join([d.strip() for d in datasets])
        return f"<br>  • {formatted}"
```

### Updated Visualizations

**1. Timeline Graph (`create_timeline_graph()`)**
- Preprocesses datasets with `format_datasets_for_hover()`
- Creates new column: `Datasets_Formatted`
- Uses formatted version in hover tooltips
- Added `hoverlabel` styling to layout

**2. Gantt Chart (`create_gantt_chart()`)**
- Same preprocessing approach
- Uses formatted datasets in hover template
- Added `hoverlabel` styling to layout

## 🎨 Visual Improvements

### Hover Label Styling
```python
hoverlabel=dict(
    bgcolor="white",
    font_size=12,
    font_family="monospace",
    align="left",
)
```

**Benefits:**
- **White background**: Clear contrast for readability
- **Monospace font**: Aligned columns for structured data
- **Left alignment**: Natural reading flow
- **Consistent sizing**: Professional appearance

## 📊 Example Output

### Experiment with 28 datasets:

**Tooltip displays:**
```
Setup: setup_20
Group: exp_cell
Target: cell
Model: isolated_unet
Status: Running
LSD: YES
Resolution: 8nm
Max Iterations: 220000
Batch Size: 14
Learning Rate: 5e-05
Creation Date: 2025-10-10
Trained Until: 2025-10-10
Starting Checkpoint: config_2/278361
Datasets Used:
  • jrc_c-elegans-P3_E5_D1_N2: 5
  • jrc_c-elegans-bw-1: 4
  • jrc_c-elegans-comma-1: 12
  • jrc_c-elegans-op50-1: 1
  • jrc_celegans-20250414: 5
  • jrc_celegans_bw25113: 5
  • jrc_cos7-1a: 10
  • jrc_cos7-1b: 10
  • jrc_ctl-id8-1: 5
  • jrc_fly-mb-1a: 6
  • jrc_fly-vnc-1: 6
  • jrc_hela-2: 26
  • jrc_hela-3: 17
  • jrc_jurkat-1: 20
  • jrc_macrophage-2: 18
  ... and 13 more
```

### Experiment with 3 datasets:

**Tooltip displays:**
```
...
Datasets Used:
  • jrc_mus-cerebellum-1: 5
  • jrc_mus-kidney: 10
  • jrc_mus-liver: 15
```

## 🔄 Files Modified

1. **`scripts/generate_timeline.py`**
   - Added `format_datasets_for_hover()` function
   - Updated `create_timeline_graph()` to preprocess datasets
   - Updated `create_gantt_chart()` to preprocess datasets
   - Enhanced hover label styling in both layouts

## ✅ Testing

**Verified with:**
- ✅ Experiments with 3-5 datasets (short list, fully displayed)
- ✅ Experiments with 10-15 datasets (medium list, fully displayed)
- ✅ Experiments with 28+ datasets (long list, truncated with counter)
- ✅ Experiments with no datasets (shows "N/A")
- ✅ Hover tooltip readability and positioning

## 🚀 Usage

Simply regenerate the website:

```bash
cd /groups/cellmap/cellmap/zouinkhim/exp-overview
python3 scripts/generate_timeline.py
```

The improvements are automatically applied to:
- `output/visualizations/experiment_timeline.html`
- `output/visualizations/experiment_gantt.html`

## 📈 Benefits

1. **Improved Readability**: Line-by-line display is much easier to scan
2. **Better UX**: Tooltips stay on screen and don't overflow
3. **Professional Look**: Consistent formatting with monospace font
4. **Performance**: Limiting to 15 datasets keeps tooltips snappy
5. **Accessibility**: Left-aligned text is easier to read
6. **Scalability**: Works well with any number of datasets

## 💡 Future Enhancements

Potential improvements:
- Add scrolling to tooltips for experiments with 15+ datasets
- Color-code datasets by organism type
- Add click-to-expand functionality for truncated lists
- Include dataset preview images in tooltips
- Add filtering by dataset in the visualization

---

**Result**: Clean, readable hover tooltips that scale gracefully from experiments with few datasets to those using many datasets! 🎉
