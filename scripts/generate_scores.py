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
    Create interactive charts showing F1 scores grouped by organelle
    """

    # Get unique organelles
    organelles = sorted(df["organelle"].unique())

    # Create a subplot for each organelle
    num_organelles = len(organelles)
    rows = (num_organelles + 1) // 2  # 2 columns

    fig = make_subplots(
        rows=rows,
        cols=2,
        subplot_titles=[f"{org.upper()}" for org in organelles],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
    )

    # Color palette for different experiment groups
    color_map = {
        "exp_mito": "#FF6B6B",
        "exp_pancreas": "#4ECDC4",
        "exp_cell": "#45B7D1",
        "exp_cerebellum": "#96CEB4",
        "exp_salivary": "#A78BFA",
        "exp_c-elegen": "#FECA57",
        "exp_c-elegen_v2": "#FECA57",
        "exp_c-elegen_v3": "#FF9FF3",
        "exp_c-elegen_v4": "#54A0FF",
    }

    for idx, organelle in enumerate(organelles):
        row = (idx // 2) + 1
        col = (idx % 2) + 1

        # Filter data for this organelle
        org_data = df[df["organelle"] == organelle].copy()
        org_data = org_data.sort_values("f1", ascending=False)

        # Create hover text with iteration info
        org_data["hover_text"] = org_data.apply(
            lambda x: f"<b>{x['setup']}</b><br>"
            f"Group: {x['experiment_group']}<br>"
            f"Iteration: {x['iteration'] if pd.notna(x['iteration']) else 'N/A'}<br>"
            f"Dataset: {x['dataset']}<br>"
            f"Crop: {x['crop']}<br>"
            f"F1: {x['f1']:.4f}<br>"
            f"Accuracy: {x['accuracy']:.4f}<br>"
            f"Val Loss: {x['val_loss']:.4f}<br>"
            f"Checkpoint: {x['checkpoint']}",
            axis=1,
        )

        # Add bars for each experiment group
        for exp_group in org_data["experiment_group"].unique():
            group_data = org_data[org_data["experiment_group"] == exp_group]

            fig.add_trace(
                go.Bar(
                    x=group_data["setup"],
                    y=group_data["f1"],
                    name=exp_group.replace("exp_", ""),
                    marker_color=color_map.get(exp_group, "#95A5A6"),
                    hovertext=group_data["hover_text"],
                    hoverinfo="text",
                    showlegend=(idx == 0),  # Only show legend for first subplot
                ),
                row=row,
                col=col,
            )

        # Update axes
        fig.update_xaxes(title_text="Setup", tickangle=-45, row=row, col=col)
        fig.update_yaxes(title_text="F1 Score", row=row, col=col)

    fig.update_layout(
        height=400 * rows,
        title_text="🎯 Model Performance by Organelle (F1 Score)<br><sub>Comparison across all experiments and setups</sub>",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="closest",
    )

    return fig


def create_best_scores_table(df):
    """
    Create a table showing the best F1 score for each organelle
    """

    # Get best score for each organelle
    best_scores = df.loc[df.groupby("organelle")["f1"].idxmax()]
    best_scores = best_scores.sort_values("f1", ascending=False)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "<b>Organelle</b>",
                        "<b>Best F1</b>",
                        "<b>Accuracy</b>",
                        "<b>Val Loss</b>",
                        "<b>Iteration</b>",
                        "<b>Setup</b>",
                        "<b>Experiment</b>",
                        "<b>Dataset</b>",
                    ],
                    fill_color="#2b6cb0",
                    font=dict(color="white", size=12),
                    align="left",
                ),
                cells=dict(
                    values=[
                        best_scores["organelle"],
                        best_scores["f1"].round(4),
                        best_scores["accuracy"].round(4),
                        best_scores["val_loss"].round(4),
                        best_scores["iteration"].fillna("N/A").astype(str),
                        best_scores["setup"],
                        best_scores["experiment_group"].str.replace("exp_", ""),
                        best_scores["dataset"],
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
        title_text="🏆 Best Performing Models per Organelle",
        height=max(400, len(best_scores) * 40 + 100),
    )

    return fig


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
    Create line charts showing score progression by iteration for each setup
    """
    # Filter to only records with iteration info
    df_iter = df[df["iteration"].notna()].copy()

    if df_iter.empty:
        return None

    # Get unique organelles
    organelles = sorted(df_iter["organelle"].unique())

    if len(organelles) == 0:
        return None

    # Create subplots for each organelle
    num_organelles = len(organelles)
    rows = (num_organelles + 1) // 2

    fig = make_subplots(
        rows=rows,
        cols=2,
        subplot_titles=[f"{org.upper()} - F1 Score by Iteration" for org in organelles],
        vertical_spacing=0.15,
        horizontal_spacing=0.12,
    )

    color_map = {
        "exp_mito": "#FF6B6B",
        "exp_pancreas": "#4ECDC4",
        "exp_cell": "#45B7D1",
        "exp_cerebellum": "#96CEB4",
        "exp_salivary": "#A78BFA",
        "exp_c-elegen": "#FECA57",
        "exp_c-elegen_v2": "#FECA57",
        "exp_c-elegen_v3": "#FF9FF3",
        "exp_c-elegen_v4": "#54A0FF",
    }

    for idx, organelle in enumerate(organelles):
        row = (idx // 2) + 1
        col = (idx % 2) + 1

        org_data = df_iter[df_iter["organelle"] == organelle].copy()

        # Group by setup and plot each setup's progression
        for setup in org_data["setup"].unique():
            setup_data = org_data[org_data["setup"] == setup].sort_values("iteration")
            exp_group = setup_data["experiment_group"].iloc[0]

            fig.add_trace(
                go.Scatter(
                    x=setup_data["iteration"],
                    y=setup_data["f1"],
                    mode="lines+markers",
                    name=f"{setup} ({exp_group.replace('exp_', '')})",
                    marker=dict(size=8, color=color_map.get(exp_group, "#95A5A6")),
                    line=dict(width=2, color=color_map.get(exp_group, "#95A5A6")),
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Iteration: %{x}<br>"
                    + "F1 Score: %{y:.4f}<br>"
                    + "<extra></extra>",
                    showlegend=(idx == 0),
                ),
                row=row,
                col=col,
            )

        fig.update_xaxes(title_text="Iteration", row=row, col=col)
        fig.update_yaxes(title_text="F1 Score", row=row, col=col)

    fig.update_layout(
        height=400 * rows,
        title_text="📈 Model Performance Progression by Training Iteration<br><sub>Track how F1 scores improve with more training</sub>",
        hovermode="closest",
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
    )

    return fig


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

    # Create organelle comparison charts
    organelle_fig = create_organelle_comparison_charts(df)
    organelle_fig.write_html("output/visualizations/scores_by_organelle.html")
    print(
        "✅ Organelle comparison saved to 'output/visualizations/scores_by_organelle.html'"
    )

    # Create best scores table
    best_scores_fig = create_best_scores_table(df)
    best_scores_fig.write_html("output/visualizations/best_scores.html")
    print("✅ Best scores table saved to 'output/visualizations/best_scores.html'")

    # Create metrics scatter
    metrics_fig = create_metrics_scatter(df)
    metrics_fig.write_html("output/visualizations/metrics_correlation.html")
    print(
        "✅ Metrics correlation saved to 'output/visualizations/metrics_correlation.html'"
    )

    # Create experiment group comparison
    group_fig = create_experiment_group_comparison(df)
    group_fig.write_html("output/visualizations/group_comparison.html")
    print("✅ Group comparison saved to 'output/visualizations/group_comparison.html'")

    # Create iteration progression chart
    iteration_fig = create_iteration_progression(df)
    if iteration_fig:
        iteration_fig.write_html("output/visualizations/iteration_progression.html")
        print(
            "✅ Iteration progression saved to 'output/visualizations/iteration_progression.html'"
        )
    else:
        print("⚠️ No iteration data available for progression chart")

    print("\n🎉 All score visualizations generated successfully!")

    return stats


if __name__ == "__main__":
    stats = main()
