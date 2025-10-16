#!/usr/bin/env python3
"""
Scores Visualization
Generates interactive visualizations of model scores grouped by organelle
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from pathlib import Path
import glob


def collect_scores_from_runs():
    """
    Scan all experiment directories for scores.yaml files and collect them
    """
    base_path = Path("/groups/cellmap/cellmap/zouinkhim")

    # Find all scores.yaml files in exp_* directories
    score_files = []
    for exp_dir in base_path.glob("exp_*/runs/*/scores.yaml"):
        score_files.append(exp_dir)

    print(f"Found {len(score_files)} score files")

    all_scores = []

    for score_file in score_files:
        try:
            with open(score_file, "r") as f:
                scores_data = yaml.safe_load(f)

            # Extract experiment group and setup from path
            # Path format: /groups/cellmap/cellmap/zouinkhim/exp_salivary/runs/setup_15/scores.yaml
            parts = score_file.parts
            exp_group = parts[-4]  # exp_salivary
            setup_name = parts[-2]  # setup_15

            if not scores_data:
                continue

            # Process the nested structure
            for checkpoint, checkpoint_data in scores_data.items():
                # Extract iteration number from checkpoint name (e.g., model_checkpoint_10000 -> 10000)
                iteration = None
                if "checkpoint_" in checkpoint:
                    try:
                        iteration = int(checkpoint.split("_")[-1])
                    except:
                        iteration = None

                for dataset, dataset_data in checkpoint_data.items():
                    for crop, crop_data in dataset_data.items():
                        for organelle, metrics in crop_data.items():
                            record = {
                                "experiment_group": exp_group,
                                "setup": setup_name,
                                "checkpoint": checkpoint,
                                "iteration": iteration,
                                "dataset": dataset,
                                "crop": crop,
                                "organelle": organelle,
                                "f1": metrics.get("f1", None),
                                "accuracy": metrics.get("accuracy", None),
                                "val_loss": metrics.get("val_loss", None),
                            }
                            all_scores.append(record)

        except Exception as e:
            print(f"Error processing {score_file}: {e}")
            continue

    return pd.DataFrame(all_scores)


def create_organelle_comparison_charts(df):
    """
    Create simple, clear bar charts showing F1 scores for each organelle per dataset
    One chart per organelle, grouped by dataset
    """
    organelles = sorted(df["organelle"].unique())

    # Create one figure per organelle for clarity
    figs = []

    for organelle in organelles:
        org_data = df[df["organelle"] == organelle].copy()

        # Get best score per setup AND dataset (in case multiple iterations exist)
        best_per_setup_dataset = org_data.loc[
            org_data.groupby(["setup", "dataset"])["f1"].idxmax()
        ]
        best_per_setup_dataset = best_per_setup_dataset.sort_values(
            ["dataset", "f1"], ascending=[True, True]
        )  # Sort by dataset first, then f1

        # Create setup label with iteration and dataset
        best_per_setup_dataset["setup_label"] = best_per_setup_dataset.apply(
            lambda x: f"{x['setup']} - {x['dataset']} (iter {int(x['iteration']) if pd.notna(x['iteration']) else 'N/A'})",
            axis=1,
        )

        # Color by dataset
        datasets = best_per_setup_dataset["dataset"].unique()
        dataset_color_map = {
            dataset: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
            for i, dataset in enumerate(datasets)
        }

        colors = [
            dataset_color_map.get(d, "#95A5A6")
            for d in best_per_setup_dataset["dataset"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=best_per_setup_dataset["setup_label"],
                x=best_per_setup_dataset["f1"],
                orientation="h",
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=best_per_setup_dataset["f1"].round(4),
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>"
                + "F1 Score: %{x:.4f}<br>"
                + "Accuracy: %{customdata[0]:.4f}<br>"
                + "Val Loss: %{customdata[1]:.4f}<br>"
                + "Dataset: %{customdata[2]}<br>"
                + "Crop: %{customdata[3]}<br>"
                + "Group: %{customdata[4]}<br>"
                + "<extra></extra>",
                customdata=best_per_setup_dataset[
                    ["accuracy", "val_loss", "dataset", "crop", "experiment_group"]
                ].values,
            )
        )

        # Add legend for datasets
        for dataset, color in dataset_color_map.items():
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    legendgroup=dataset,
                    showlegend=True,
                    name=dataset,
                )
            )

        fig.update_layout(
            title=dict(
                text=f"<b>{organelle.upper()}</b> - F1 Scores by Setup & Dataset<br><sub>Showing best iteration for each setup-dataset combination</sub>",
                font=dict(size=20),
            ),
            xaxis_title="F1 Score",
            yaxis_title="Setup - Dataset (Iteration)",
            height=max(400, len(best_per_setup_dataset) * 35 + 150),
            margin=dict(l=250, r=100, t=100, b=80),
            template="plotly_white",
            xaxis=dict(range=[0, 1.0]),
            font=dict(size=12),
        )

        figs.append((organelle, fig))

    return figs


def create_best_scores_table(df):
    """
    Create a table showing the best F1 score for each organelle per dataset
    """

    # Get best score for each organelle-dataset combination
    best_scores = df.loc[df.groupby(["organelle", "dataset"])["f1"].idxmax()]
    best_scores = best_scores.sort_values(["organelle", "f1"], ascending=[True, False])

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "<b>Organelle</b>",
                        "<b>Dataset</b>",
                        "<b>Best F1</b>",
                        "<b>Accuracy</b>",
                        "<b>Val Loss</b>",
                        "<b>Iteration</b>",
                        "<b>Setup</b>",
                        "<b>Experiment</b>",
                        "<b>Crop</b>",
                    ],
                    fill_color="#2b6cb0",
                    font=dict(color="white", size=12),
                    align="left",
                ),
                cells=dict(
                    values=[
                        best_scores["organelle"],
                        best_scores["dataset"],
                        best_scores["f1"].round(4),
                        best_scores["accuracy"].round(4),
                        best_scores["val_loss"].round(4),
                        best_scores["iteration"].fillna("N/A").astype(str),
                        best_scores["setup"],
                        best_scores["experiment_group"].str.replace("exp_", ""),
                        best_scores["crop"],
                    ],
                    fill_color=[["#f7fafc", "white"] * len(best_scores)],
                    align="left",
                    font=dict(size=11),
                    height=30,
                ),
            )
        ]
    )

    fig.update_layout(
        title_text="🏆 Best Performing Models per Organelle per Dataset",
        height=max(400, len(best_scores) * 40 + 100),
    )

    return fig


def create_searchable_scores_table(df):
    """
    Create an interactive, searchable HTML table with all scores
    """
    # Prepare data for the table
    table_data = df.copy()
    table_data = table_data.sort_values(
        ["organelle", "dataset", "f1"], ascending=[True, True, False]
    )

    # Format numerical columns
    table_data["f1_formatted"] = table_data["f1"].round(4)
    table_data["accuracy_formatted"] = table_data["accuracy"].round(4)
    table_data["val_loss_formatted"] = table_data["val_loss"].round(4)
    table_data["iteration_formatted"] = (
        table_data["iteration"].fillna("N/A").astype(str)
    )

    # Convert to JSON for JavaScript
    import json

    rows_data = []
    for _, row in table_data.iterrows():
        rows_data.append(
            {
                "organelle": row["organelle"],
                "dataset": row["dataset"],
                "crop": row["crop"],
                "setup": row["setup"],
                "experiment": row["experiment_group"].replace("exp_", ""),
                "checkpoint": row["checkpoint"],
                "iteration": row["iteration_formatted"],
                "f1": float(row["f1"]) if pd.notna(row["f1"]) else 0,
                "accuracy": float(row["accuracy"]) if pd.notna(row["accuracy"]) else 0,
                "val_loss": float(row["val_loss"]) if pd.notna(row["val_loss"]) else 0,
            }
        )

    rows_json = json.dumps(rows_data)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Searchable Model Scores</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            max-width: 1600px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
        }}
        h1 {{
            color: #1a365d;
            border-bottom: 3px solid #2b6cb0;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        .controls {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .search-box {{
            width: 100%;
            max-width: 400px;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #cbd5e0;
            border-radius: 6px;
            margin-right: 10px;
        }}
        .filter-group {{
            display: inline-block;
            margin-right: 20px;
            margin-top: 10px;
        }}
        .filter-group label {{
            font-weight: 600;
            margin-right: 8px;
            color: #2d3748;
        }}
        .filter-group select {{
            padding: 8px 12px;
            border: 2px solid #cbd5e0;
            border-radius: 6px;
            font-size: 14px;
            background: white;
        }}
        .stats {{
            display: inline-block;
            margin-left: 20px;
            color: #4a5568;
            font-weight: 600;
        }}
        .table-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #2b6cb0;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        th:hover {{
            background: #2c5282;
        }}
        th::after {{
            content: ' ⇅';
            opacity: 0.5;
        }}
        th.sort-asc::after {{
            content: ' ↑';
            opacity: 1;
        }}
        th.sort-desc::after {{
            content: ' ↓';
            opacity: 1;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        tr.hidden {{
            display: none;
        }}
        .f1-high {{
            background: #48bb78;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .f1-medium {{
            background: #ecc94b;
            color: #1a202c;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .f1-low {{
            background: #fc8181;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .export-btn {{
            background: #2b6cb0;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            margin-left: 10px;
        }}
        .export-btn:hover {{
            background: #2c5282;
        }}
    </style>
</head>
<body>
    <h1>🔍 Searchable Model Scores Table</h1>
    
    <div class="controls">
        <input type="text" id="searchBox" class="search-box" placeholder="Search by any field...">
        
        <div class="filter-group">
            <label>Organelle:</label>
            <select id="organelleFilter">
                <option value="">All</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label>Dataset:</label>
            <select id="datasetFilter">
                <option value="">All</option>
            </select>
        </div>
        
        <div class="filter-group">
            <label>Experiment:</label>
            <select id="experimentFilter">
                <option value="">All</option>
            </select>
        </div>
        
        <button class="export-btn" onclick="exportToCSV()">📥 Export to CSV</button>
        
        <span class="stats" id="statsText">Showing <strong id="visibleCount">0</strong> of <strong id="totalCount">0</strong> rows</span>
    </div>
    
    <div class="table-container">
        <table id="scoresTable">
            <thead>
                <tr>
                    <th data-column="organelle">Organelle</th>
                    <th data-column="dataset">Dataset</th>
                    <th data-column="crop">Crop</th>
                    <th data-column="setup">Setup</th>
                    <th data-column="experiment">Experiment</th>
                    <th data-column="checkpoint">Checkpoint</th>
                    <th data-column="iteration">Iteration</th>
                    <th data-column="f1">F1 Score</th>
                    <th data-column="accuracy">Accuracy</th>
                    <th data-column="val_loss">Val Loss</th>
                </tr>
            </thead>
            <tbody id="tableBody">
            </tbody>
        </table>
    </div>
    
    <script>
        // Data
        const allData = {rows_json};
        let currentSort = {{ column: 'f1', ascending: false }};
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            populateFilters();
            renderTable();
            updateStats();
            
            // Event listeners
            document.getElementById('searchBox').addEventListener('input', filterTable);
            document.getElementById('organelleFilter').addEventListener('change', filterTable);
            document.getElementById('datasetFilter').addEventListener('change', filterTable);
            document.getElementById('experimentFilter').addEventListener('change', filterTable);
            
            // Sort headers
            document.querySelectorAll('th[data-column]').forEach(th => {{
                th.addEventListener('click', () => sortTable(th.dataset.column));
            }});
        }});
        
        function populateFilters() {{
            const organelles = [...new Set(allData.map(r => r.organelle))].sort();
            const datasets = [...new Set(allData.map(r => r.dataset))].sort();
            const experiments = [...new Set(allData.map(r => r.experiment))].sort();
            
            const organelleSelect = document.getElementById('organelleFilter');
            organelles.forEach(o => {{
                const option = document.createElement('option');
                option.value = o;
                option.textContent = o;
                organelleSelect.appendChild(option);
            }});
            
            const datasetSelect = document.getElementById('datasetFilter');
            datasets.forEach(d => {{
                const option = document.createElement('option');
                option.value = d;
                option.textContent = d;
                datasetSelect.appendChild(option);
            }});
            
            const experimentSelect = document.getElementById('experimentFilter');
            experiments.forEach(e => {{
                const option = document.createElement('option');
                option.value = e;
                option.textContent = e;
                experimentSelect.appendChild(option);
            }});
        }}
        
        function getF1Class(f1) {{
            if (f1 >= 0.8) return 'f1-high';
            if (f1 >= 0.5) return 'f1-medium';
            return 'f1-low';
        }}
        
        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            allData.forEach((row, index) => {{
                const tr = document.createElement('tr');
                tr.dataset.index = index;
                
                tr.innerHTML = `
                    <td>${{row.organelle}}</td>
                    <td>${{row.dataset}}</td>
                    <td>${{row.crop}}</td>
                    <td>${{row.setup}}</td>
                    <td>${{row.experiment}}</td>
                    <td>${{row.checkpoint}}</td>
                    <td>${{row.iteration}}</td>
                    <td><span class="${{getF1Class(row.f1)}}">${{row.f1.toFixed(4)}}</span></td>
                    <td>${{row.accuracy.toFixed(4)}}</td>
                    <td>${{row.val_loss.toFixed(4)}}</td>
                `;
                
                tbody.appendChild(tr);
            }});
        }}
        
        function filterTable() {{
            const searchText = document.getElementById('searchBox').value.toLowerCase();
            const organelleFilter = document.getElementById('organelleFilter').value;
            const datasetFilter = document.getElementById('datasetFilter').value;
            const experimentFilter = document.getElementById('experimentFilter').value;
            
            const rows = document.querySelectorAll('#tableBody tr');
            
            rows.forEach(row => {{
                const index = parseInt(row.dataset.index);
                const data = allData[index];
                
                // Check search text
                const matchesSearch = !searchText || 
                    Object.values(data).some(val => 
                        String(val).toLowerCase().includes(searchText)
                    );
                
                // Check filters
                const matchesOrganelle = !organelleFilter || data.organelle === organelleFilter;
                const matchesDataset = !datasetFilter || data.dataset === datasetFilter;
                const matchesExperiment = !experimentFilter || data.experiment === experimentFilter;
                
                if (matchesSearch && matchesOrganelle && matchesDataset && matchesExperiment) {{
                    row.classList.remove('hidden');
                }} else {{
                    row.classList.add('hidden');
                }}
            }});
            
            updateStats();
        }}
        
        function sortTable(column) {{
            const ascending = currentSort.column === column ? !currentSort.ascending : false;
            currentSort = {{ column, ascending }};
            
            // Update header classes
            document.querySelectorAll('th').forEach(th => {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            const header = document.querySelector(`th[data-column="${{column}}"]`);
            header.classList.add(ascending ? 'sort-asc' : 'sort-desc');
            
            // Sort data
            allData.sort((a, b) => {{
                let aVal = a[column];
                let bVal = b[column];
                
                // Handle numeric values
                if (typeof aVal === 'number' && typeof bVal === 'number') {{
                    return ascending ? aVal - bVal : bVal - aVal;
                }}
                
                // Handle strings
                aVal = String(aVal).toLowerCase();
                bVal = String(bVal).toLowerCase();
                
                if (aVal < bVal) return ascending ? -1 : 1;
                if (aVal > bVal) return ascending ? 1 : -1;
                return 0;
            }});
            
            renderTable();
            filterTable(); // Reapply filters
        }}
        
        function updateStats() {{
            const total = allData.length;
            const visible = document.querySelectorAll('#tableBody tr:not(.hidden)').length;
            
            document.getElementById('totalCount').textContent = total;
            document.getElementById('visibleCount').textContent = visible;
        }}
        
        function exportToCSV() {{
            const rows = document.querySelectorAll('#tableBody tr:not(.hidden)');
            const headers = Array.from(document.querySelectorAll('th')).map(th => th.textContent.replace(' ⇅', '').replace(' ↑', '').replace(' ↓', ''));
            
            let csv = headers.join(',') + '\\n';
            
            rows.forEach(row => {{
                const index = parseInt(row.dataset.index);
                const data = allData[index];
                const values = [
                    data.organelle,
                    data.dataset,
                    data.crop,
                    data.setup,
                    data.experiment,
                    data.checkpoint,
                    data.iteration,
                    data.f1.toFixed(4),
                    data.accuracy.toFixed(4),
                    data.val_loss.toFixed(4)
                ];
                csv += values.map(v => `"${{v}}"`).join(',') + '\\n';
            }});
            
            // Download
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'model_scores.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
"""

    return html


def create_metrics_scatter(df):
    """
    Create scatter plots comparing different metrics
    """

    fig = make_subplots(
        rows=1, cols=2, subplot_titles=("F1 vs Accuracy", "F1 vs Validation Loss")
    )

    # Color by organelle
    organelles = df["organelle"].unique()
    colors = px.colors.qualitative.Set3[: len(organelles)]
    color_map = dict(zip(organelles, colors))

    for organelle in organelles:
        org_data = df[df["organelle"] == organelle]

        # F1 vs Accuracy
        fig.add_trace(
            go.Scatter(
                x=org_data["accuracy"],
                y=org_data["f1"],
                mode="markers",
                name=organelle,
                marker=dict(size=8, color=color_map[organelle]),
                text=org_data["setup"],
                hovertemplate="<b>%{text}</b><br>"
                + "Accuracy: %{x:.4f}<br>"
                + "F1: %{y:.4f}<br>"
                + "<extra></extra>",
                showlegend=True,
            ),
            row=1,
            col=1,
        )

        # F1 vs Val Loss
        fig.add_trace(
            go.Scatter(
                x=org_data["val_loss"],
                y=org_data["f1"],
                mode="markers",
                name=organelle,
                marker=dict(size=8, color=color_map[organelle]),
                text=org_data["setup"],
                hovertemplate="<b>%{text}</b><br>"
                + "Val Loss: %{x:.4f}<br>"
                + "F1: %{y:.4f}<br>"
                + "<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=2,
        )

    fig.update_xaxes(title_text="Accuracy", row=1, col=1)
    fig.update_yaxes(title_text="F1 Score", row=1, col=1)
    fig.update_xaxes(title_text="Validation Loss", row=1, col=2)
    fig.update_yaxes(title_text="F1 Score", row=1, col=2)

    fig.update_layout(
        height=500, title_text="📊 Metrics Correlation Analysis", hovermode="closest"
    )

    return fig


def create_experiment_group_comparison(df):
    """
    Create box plots comparing performance across experiment groups
    """

    fig = go.Figure()

    for exp_group in sorted(df["experiment_group"].unique()):
        group_data = df[df["experiment_group"] == exp_group]

        fig.add_trace(
            go.Box(y=group_data["f1"], name=exp_group.replace("exp_", ""), boxmean="sd")
        )

    fig.update_layout(
        title_text="📦 F1 Score Distribution by Experiment Group",
        yaxis_title="F1 Score",
        xaxis_title="Experiment Group",
        height=500,
        showlegend=False,
    )

    return fig


def create_iteration_progression(df):
    """
    Create SEPARATE line charts for each setup - one chart per organelle
    Much clearer than overlapping lines
    """
    # Filter to only records with iteration info
    df_iter = df[df["iteration"].notna()].copy()

    if df_iter.empty:
        return []

    # Only include setups with multiple iterations
    setup_counts = df_iter.groupby("setup")["iteration"].nunique()
    multi_iter_setups = setup_counts[setup_counts > 1].index.tolist()

    if not multi_iter_setups:
        return []

    df_iter = df_iter[df_iter["setup"].isin(multi_iter_setups)]

    # Get unique organelles
    organelles = sorted(df_iter["organelle"].unique())

    if len(organelles) == 0:
        return []

    # Create ONE figure per organelle
    figs = []

    color_palette = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#A78BFA",
        "#FECA57",
        "#FF9FF3",
        "#54A0FF",
        "#95A5A6",
        "#E67E22",
    ]

    for organelle in organelles:
        org_data = df_iter[df_iter["organelle"] == organelle].copy()
        setups = sorted(org_data["setup"].unique())

        if not setups:
            continue

        fig = go.Figure()

        for idx, setup in enumerate(setups):
            setup_data = org_data[org_data["setup"] == setup].copy()

            # Create a unique identifier for each dataset/crop combination
            setup_data["dataset_crop"] = (
                setup_data["dataset"] + "/" + setup_data["crop"]
            )

            exp_group = setup_data["experiment_group"].iloc[0]
            base_color = color_palette[idx % len(color_palette)]

            # Plot each dataset/crop combination as a separate line
            # This way lines connect horizontally (same dataset across iterations)
            # Not vertically (different datasets at same iteration)
            for dataset_crop in setup_data["dataset_crop"].unique():
                dc_data = setup_data[
                    setup_data["dataset_crop"] == dataset_crop
                ].sort_values("iteration")

                # Only show in legend once per setup (not for every dataset/crop)
                show_legend = dataset_crop == setup_data["dataset_crop"].unique()[0]

                fig.add_trace(
                    go.Scatter(
                        x=dc_data["iteration"],
                        y=dc_data["f1"],
                        mode="lines+markers",
                        name=f"{setup}",
                        legendgroup=setup,  # Group all traces for this setup
                        showlegend=show_legend,  # Only show setup name once in legend
                        marker=dict(
                            size=8, color=base_color, line=dict(width=1, color="white")
                        ),
                        line=dict(width=2, color=base_color, dash="solid"),
                        opacity=0.7,
                        hovertemplate="<b>%{fullData.legendgroup}</b><br>"
                        + f"Dataset/Crop: {dataset_crop}<br>"
                        + "Iteration: %{x:,}<br>"
                        + "F1 Score: %{y:.4f}<br>"
                        + f"Group: {exp_group}<br>"
                        + "<extra></extra>",
                    )
                )

        fig.update_layout(
            title=dict(
                text=f"<b>{organelle.upper()}</b> - Training Progression<br><sub>F1 Score vs Training Iteration</sub>",
                font=dict(size=20),
            ),
            xaxis_title="Training Iteration",
            yaxis_title="F1 Score",
            height=600,
            template="plotly_white",
            hovermode="closest",
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="gray",
                borderwidth=1,
            ),
            xaxis=dict(tickformat=",", showgrid=True, gridcolor="lightgray"),
            yaxis=dict(range=[0, 1.0], showgrid=True, gridcolor="lightgray"),
            font=dict(size=12),
        )

        figs.append((organelle, fig))

    return figs


def create_scores_summary_page(df):
    """
    Create a simple summary page with links to individual organelle pages
    """
    organelles = sorted(df["organelle"].unique())

    # Get best F1 for each organelle (overall best)
    best_scores_overall = df.loc[df.groupby("organelle")["f1"].idxmax()]

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Scores by Organelle</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
        }}
        h1 {{
            color: #1a365d;
            border-bottom: 3px solid #2b6cb0;
            padding-bottom: 10px;
        }}
        .organelle-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .organelle-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            border-left: 4px solid #2b6cb0;
        }}
        .organelle-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        .organelle-name {{
            font-size: 24px;
            font-weight: 600;
            color: #1a365d;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}
        .stats {{
            margin: 10px 0;
            color: #4a5568;
            line-height: 1.8;
        }}
        .stat-label {{
            font-weight: 500;
            color: #2d3748;
        }}
        .best-f1 {{
            font-size: 32px;
            font-weight: 700;
            color: #2b6cb0;
            margin: 15px 0;
        }}
        .dataset-scores {{
            margin-top: 15px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 4px;
            font-size: 13px;
        }}
        .dataset-item {{
            margin: 5px 0;
            padding: 5px;
            background: white;
            border-radius: 3px;
        }}
        .view-btn {{
            display: inline-block;
            background: #2b6cb0;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 10px;
            transition: background 0.2s;
        }}
        .view-btn:hover {{
            background: #2c5282;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <h1>🎯 Model Performance by Organelle & Dataset</h1>
    
    <div class="summary">
        <p><strong>Total Evaluations:</strong> {len(df)}</p>
        <p><strong>Unique Setups:</strong> {df['setup'].nunique()}</p>
        <p><strong>Unique Datasets:</strong> {df['dataset'].nunique()}</p>
        <p><strong>Organelles Tested:</strong> {', '.join(organelles)}</p>
        <p style="margin-top: 15px;">
            <a href="searchable_scores.html" style="background: #2b6cb0; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block;">
                🔍 View Searchable Table
            </a>
            <a href="best_scores.html" style="background: #48bb78; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; margin-left: 10px;">
                🏆 View Best Scores
            </a>
            <a href="iteration_progression.html" style="background: #9f7aea; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; margin-left: 10px;">
                📈 View Training Progress
            </a>
        </p>
    </div>
    
    <div class="organelle-grid">
"""

    for organelle in organelles:
        org_data = df[df["organelle"] == organelle]
        best_overall = best_scores_overall[
            best_scores_overall["organelle"] == organelle
        ].iloc[0]

        # Get best score per dataset for this organelle
        best_per_dataset = org_data.loc[org_data.groupby("dataset")["f1"].idxmax()]
        best_per_dataset = best_per_dataset.sort_values("f1", ascending=False)

        dataset_scores_html = ""
        for _, row in best_per_dataset.iterrows():
            dataset_scores_html += f"""
                <div class="dataset-item">
                    <strong>{row['dataset']}:</strong> F1 = {row['f1']:.4f} ({row['setup']})
                </div>
            """

        html += f"""
        <div class="organelle-card">
            <div class="organelle-name">{organelle}</div>
            <div class="best-f1">{best_overall['f1']:.4f}</div>
            <div class="stats">
                <div><span class="stat-label">Best Overall Setup:</span> {best_overall['setup']}</div>
                <div><span class="stat-label">Best Dataset:</span> {best_overall['dataset']}</div>
                <div><span class="stat-label">Iteration:</span> {int(best_overall['iteration']) if pd.notna(best_overall['iteration']) else 'N/A'}</div>
                <div><span class="stat-label">Datasets Tested:</span> {org_data['dataset'].nunique()}</div>
                <div><span class="stat-label">Total Evaluations:</span> {len(org_data)}</div>
            </div>
            <div class="dataset-scores">
                <strong>Best per Dataset:</strong>
                {dataset_scores_html}
            </div>
            <a href="scores_{organelle}.html" class="view-btn">View Detailed Results →</a>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html


def create_iteration_progression_summary(df, iteration_figs):
    """
    Create a summary page linking to individual iteration progression charts
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Training Iteration Progression</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
        }}
        h1 {{
            color: #1a365d;
            border-bottom: 3px solid #2b6cb0;
            padding-bottom: 10px;
        }}
        .organelle-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .organelle-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            border-left: 4px solid #2b6cb0;
        }}
        .organelle-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        .organelle-name {{
            font-size: 24px;
            font-weight: 600;
            color: #1a365d;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}
        .view-btn {{
            display: inline-block;
            background: #2b6cb0;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 10px;
            transition: background 0.2s;
        }}
        .view-btn:hover {{
            background: #2c5282;
        }}
        .info {{
            color: #4a5568;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <h1>📈 Training Iteration Progression</h1>
    <p class="info">Track how F1 scores improve over training iterations. Each chart shows setups with multiple checkpoints.</p>
    
    <div class="organelle-grid">
"""

    for organelle, fig in iteration_figs:
        org_data = df[df["organelle"] == organelle]
        # Count setups with multiple iterations
        multi_iter = org_data.groupby("setup")["iteration"].nunique()
        setups_with_progression = multi_iter[multi_iter > 1].count()

        html += f"""
        <div class="organelle-card">
            <div class="organelle-name">{organelle}</div>
            <div class="info">
                <strong>{setups_with_progression}</strong> setups with multiple checkpoints
            </div>
            <a href="iteration_progression_{organelle}.html" class="view-btn">View Training Curves →</a>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    return html


def create_scores_summary_stats(df):
    """
    Create summary statistics
    """

    stats = {
        "total_evaluations": len(df),
        "unique_setups": df["setup"].nunique(),
        "unique_organelles": df["organelle"].nunique(),
        "avg_f1": df["f1"].mean(),
        "max_f1": df["f1"].max(),
        "min_f1": df["f1"].min(),
    }

    return stats


def main():
    print("🔍 Collecting scores from all experiment runs...")
    df = collect_scores_from_runs()

    if df.empty:
        print("❌ No scores found!")
        return

    print(f"✅ Collected {len(df)} score records")
    print(f"   - {df['organelle'].nunique()} unique organelles")
    print(f"   - {df['setup'].nunique()} unique setups")
    print(f"   - {df['experiment_group'].nunique()} experiment groups")

    # Get summary stats
    stats = create_scores_summary_stats(df)

    print("\n📊 Generating visualizations...")

    # Create organelle comparison charts (one per organelle)
    organelle_figs = create_organelle_comparison_charts(df)
    for organelle, fig in organelle_figs:
        filename = f"output/visualizations/scores_{organelle}.html"
        fig.write_html(filename)
        print(f"✅ {organelle.upper()} scores saved to '{filename}'")

    # Create summary page with links to all organelles
    summary_html = create_scores_summary_page(df)
    with open("output/visualizations/scores_by_organelle.html", "w") as f:
        f.write(summary_html)
    print(
        "✅ Scores summary page saved to 'output/visualizations/scores_by_organelle.html'"
    )

    # Create best scores table
    best_scores_fig = create_best_scores_table(df)
    best_scores_fig.write_html("output/visualizations/best_scores.html")
    print("✅ Best scores table saved to 'output/visualizations/best_scores.html'")

    # Create searchable scores table
    searchable_table_html = create_searchable_scores_table(df)
    with open("output/visualizations/searchable_scores.html", "w") as f:
        f.write(searchable_table_html)
    print(
        "✅ Searchable scores table saved to 'output/visualizations/searchable_scores.html'"
    )

    # Create iteration progression charts (one per organelle, if multiple iterations exist)
    iteration_figs = create_iteration_progression(df)
    if iteration_figs:
        for organelle, fig in iteration_figs:
            filename = f"output/visualizations/iteration_progression_{organelle}.html"
            fig.write_html(filename)
            print(f"✅ {organelle.upper()} progression saved to '{filename}'")

        # Create summary page linking to all progression charts
        prog_html = create_iteration_progression_summary(df, iteration_figs)
        with open("output/visualizations/iteration_progression.html", "w") as f:
            f.write(prog_html)
        print(
            "✅ Iteration progression summary saved to 'output/visualizations/iteration_progression.html'"
        )
    else:
        print("⚠️  No iteration progression data (need multiple checkpoints per setup)")

    print("\n🎉 All score visualizations generated successfully!")
    print("📁 Main page: output/visualizations/scores_by_organelle.html")

    return stats


if __name__ == "__main__":
    stats = main()
