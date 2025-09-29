# Comparison Report: Manual vs Auto-Generated Overview

## Summary
- **Manual CSV**: 41 experiments (curated)
- **Auto-Generated CSV**: 120 experiments (scanned)
- **Match Rate**: 34/41 (83%) of manual experiments found automatically

## Successfully Matched (34 experiments)
The script successfully found and extracted data for most experiments including:
- All `setup_*` experiments from exp_cerebellum, exp_pancreas, exp_cell
- Most exp_c-elegen_v3 and exp_c-elegen_v4 experiments
- Configuration data extraction working well

## Missing from Auto-Generated (7 experiments)
1. `[+80 more organelle runs]` - Summary entry, not real experiment
2. `setup_15-19` (exp_mito) - Location not found
3. `train_fly_model` (exp_c-elegen_v2) - Directory structure issue

## Extra Discoveries (86 experiments)
The auto-scanner found many additional experiments, particularly:
- 80+ organelle training runs from exp_c-elegen_v3
- Various combinations of targets: cell, ecs, er, isg, ld, lyso, mito, nuc, perox, yolk
- Different training configurations (distance, lsd, mixed)

## Data Quality Issues Found

### 1. Checkpoint Name Formatting
- **Manual**: `20250725_mito_all_mixed_distance_16nm/568k`
- **Generated**: `20250725_mito_all_mixed_distance_16nm/568000k`
- **Issue**: Generated shows full numbers instead of abbreviated form

### 2. Number Formatting
- **Manual**: `16` (integer)
- **Generated**: `16.0` (float)
- **Issue**: Inconsistent data types

### 3. Missing Data in exp_c-elegen_v3
- Many v3 experiments lack max_iterations and resolution data
- This is likely because config files are structured differently or missing

## Recommendations

### Immediate Fixes
1. **Find missing exp_mito setups**: Check if setup_15-19 are in a different location
2. **Format checkpoint names**: Abbreviate large numbers (568000k → 568k)
3. **Standardize number formats**: Convert floats to integers where appropriate
4. **Improve v3 parsing**: Better extraction from exp_c-elegen_v3 structure

### Process Improvements
1. **Hybrid approach**: Use auto-scanning as base, manual curation for special cases
2. **Validation**: Add checks for missing required fields
3. **Incremental updates**: Merge new experiments with existing manual data

## Conclusion
The automated scanning works very well overall, finding 83% of manually curated experiments plus discovering many additional ones. The main issues are formatting consistency and handling special directory structures.