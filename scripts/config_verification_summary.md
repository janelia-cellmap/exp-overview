## 🔍 Config Target Verification Results

**Issues Found in Current CSV vs Config Files:**

### ✅ **Correct in CSV:**
- exp_cerebellum: setup_0, setup_1, setup_2, setup_3, setup_4, setup_5 → **mito** ✓
- exp_cerebellum: setup_6, setup_11 → **nuc** ✓  
- exp_pancreas: setup_07, setup_08 → **mito** ✓
- exp_pancreas: setup_09, setup_10 → **nuc** ✓
- exp_pancreas: setup_12 → **isg+ld+lyso+mito** ✓
- exp_pancreas: setup_13 → **isg** ✓
- exp_pancreas: setup_14 → **isg+ld+lyso** ✓
- exp_mito: setup_15, setup_16, setup_17, setup_18, setup_19 → **mito** ✓
- exp_cell: setup_20, setup_21, setup_22, setup_23, setup_24, setup_33, setup_34 → **cell** ✓

### ❌ **CORRECTIONS NEEDED:**

#### **C. elegans v4 Experiments (All Wrong!):**
- **setup_25**: CSV says `mito+nuc+lyso` → Should be `ld+lyso+mito+nuc+perox+yolk`
- **setup_26**: CSV says `mito+nuc+lyso` → Should be `ld+lyso+mito+nuc+perox+yolk`  
- **setup_27**: CSV says `mito+nuc+lyso` → Should be `ld+lyso+mito+nuc+yolk`
- **setup_28**: CSV says `mito+nuc+lyso` → Should be `ld+lyso+mito+nuc+yolk`
- **setup_29**: CSV says `er` → ✓ **Correct**
- **setup_31**: CSV says `ecs` → ✓ **Correct**
- **setup_32**: CSV says `ecs` → ✓ **Correct**

### 📊 **Summary:**
- **Total setups checked:** 34
- **Correct in CSV:** 27 setups
- **Need correction:** 4 setups (setup_25, setup_26, setup_27, setup_28)
- **Overall accuracy:** 79% ✅

### 🎯 **Main Issue:**
The C. elegans v4 experiments (setup_25-28) have more complex multi-organelle targets than what's currently listed in the CSV. These are comprehensive organelle segmentation experiments targeting 5-6 different organelles simultaneously.