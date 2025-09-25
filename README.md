# exp-overview
an overview and reference for the experimental projects

## CellMap Experimental Projects

This repository provides an overview of the current experimental setups and projects within the CellMap initiative at Janelia Research Campus.

## Current Experimental Projects

| Project | Repository | Status | Dataset(s) | Organelles/Targets | ML Framework | Description | Key Tools |
|---------|------------|--------|------------|-------------------|--------------|-------------|-----------|
| **C. elegans Expression** | [expr_c-elegans](https://github.com/janelia-cellmap/expr_c-elegans) | 🔶 Archived | jrc_c-elegans-op50-1<br/>jrc_c-elegans-bw-1<br/>jrc_c-elegans-comma-1 | Mitochondria [mito]<br/>Lipid droplets [ld] | DaCapo + UNet | C. elegans organelle segmentation experiments | DaCapo, process-blockwise |

## Core CellMap Infrastructure

| Component | Repository | Purpose | Key Features |
|-----------|------------|---------|--------------|
| **Data Loading** | [cellmap-data](https://github.com/janelia-cellmap/cellmap-data) | PyTorch data loading for ML training | Multi-class segmentation, spatial transforms, efficient streaming |
| **Model Repository** | [cellmap-models](https://github.com/janelia-cellmap/cellmap-models) | Pre-trained segmentation models | COSEM models, whole-cell organelle segmentation |
| **Segmentation Challenge** | [cellmap-segmentation-challenge](https://github.com/janelia-cellmap/cellmap-segmentation-challenge) | Competition framework and toolbox | Data access, training, prediction, evaluation |
| **Data Analysis** | [cellmap-analyze](https://github.com/janelia-cellmap/cellmap-analyze) | Analysis utilities | Post-processing and metrics |
| **Nucleus Segmentation** | [cellmap-nuclei](https://github.com/janelia-cellmap/cellmap-nuclei) | Nucleus segmentation for FIB-SEM | Specialized nucleus detection |
| **Visualization** | [cellmap-flow](https://github.com/janelia-cellmap/cellmap-flow) | Results visualization | Neuroglancer integration |

## Experimental Setup Details

### C. elegans Expression Project
- **Datasets**: 
  - `jrc_c-elegans-op50-1` and `jrc_c-elegans-bw-1` (similar characteristics, combined for training)
  - `jrc_c-elegans-comma-1` (different characteristics, limited crops available)
- **Target Organelles**: 
  - Mitochondria using full pipeline
  - Lipid droplets using lightweight U-Net (large, round, easy to identify)
- **ML Framework**: [DaCapo](https://github.com/janelia-cellmap/dacapo) for training
- **Inference**: [process-blockwise](https://github.com/janelia-cellmap/process-blockwise)
- **Status**: Archived (completed experimental phase)

## Data Format and Storage
- **Primary Format**: OME-NGFF/Zarr with multiscale support
- **Storage**: Local filesystem and cloud (S3/GCS) via TensorStore
- **Visualization**: Neuroglancer for 3D volume inspection

## Common Tools and Workflows

### Training Pipeline
1. **Data Preparation**: cellmap-data for efficient loading and augmentation
2. **Model Training**: DaCapo framework with configurable architectures
3. **Inference**: process-blockwise for large-volume prediction
4. **Visualization**: cellmap-flow with Neuroglancer integration

### Model Architectures
- **U-Net variants**: 2D and 3D configurations
- **Multi-class segmentation**: Support for mutually exclusive classes
- **Pre-trained models**: Available via cellmap-models

## Getting Started

To work with CellMap experimental data:

1. **Install core packages**:
   ```bash
   pip install cellmap-data cellmap-models
   ```

2. **Download challenge data**:
   ```bash
   pip install cellmap-segmentation-challenge
   csc fetch-data
   ```

3. **Explore existing experiments**:
   - Review the [expr_c-elegans](https://github.com/janelia-cellmap/expr_c-elegans) repository for C. elegans workflows
   - Check [cellmap-segmentation-challenge](https://github.com/janelia-cellmap/cellmap-segmentation-challenge) for training examples

## Contributing

To add a new experimental project:
1. Create a repository following the `expr_*` naming convention
2. Include a comprehensive README with dataset and organelle information
3. Document the ML frameworks and tools used
4. Update this overview table with your project details

## Resources

- [CellMap Project Page](https://www.janelia.org/project-team/cellmap)
- [CellMap Segmentation Challenge](https://cellmapchallenge.janelia.org/)
- [DaCapo Documentation](https://github.com/janelia-cellmap/dacapo)
