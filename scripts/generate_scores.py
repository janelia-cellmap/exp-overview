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
    Create simple, clear bar charts showing F1 scores for each organelle
    One chart per organelle, sorted by F1 score
    """
    organelles = sorted(df["organelle"].unique())
    
    # Create one figure per organelle for clarity
    figs = []
    
    for organelle in organelles:
        org_data = df[df["organelle"] == organelle].copy()
        
        # Get best score per setup (in case multiple iterations exist)
        best_per_setup = org_data.loc[org_data.groupby('setup')['f1'].idxmax()]
        best_per_setup = best_per_setup.sort_values('f1', ascending=True)  # Ascending for horizontal bar
        
        # Create setup label with iteration
        best_per_setup['setup_label'] = best_per_setup.apply(
            lambda x: f"{x['setup']} (iter {int(x['iteration']) if pd.notna(x['iteration']) else 'N/A'})",
            axis=1
        )
        
        # Color by experiment group
        color_map = {
            "exp_mito": "#FF6B6B",
            "exp_pancreas": "#4ECDC4",
            "exp_cell": "#45B7D1",
            "exp_cerebellum": "#96CEB4",
            "exp_salivary": "#A78BFA",
            "exp_c-elegen": "#FECA57",
        }
        
        colors = [color_map.get(g, "#95A5A6") for g in best_per_setup['experiment_group']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=best_per_setup['setup_label'],
            x=best_per_setup['f1'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='white', width=1)
            ),
            text=best_per_setup['f1'].round(4),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                         'F1 Score: %{x:.4f}<br>' +
                         'Accuracy: %{customdata[0]:.4f}<br>' +
                         'Val Loss: %{customdata[1]:.4f}<br>' +
                         'Dataset: %{customdata[2]}<br>' +
                         'Group: %{customdata[3]}<br>' +
                         '<extra></extra>',
            customdata=best_per_setup[['accuracy', 'val_loss', 'dataset', 'experiment_group']].values
        ))
        
        fig.update_layout(
            title=dict(
                text=f"<b>{organelle.upper()}</b> - F1 Scores by Setup<br><sub>Showing best iteration for each setup</sub>",
                font=dict(size=20)
            ),
            xaxis_title="F1 Score",
            yaxis_title="Setup (Iteration)",
            height=max(400, len(best_per_setup) * 35 + 150),
            margin=dict(l=200, r=100, t=100, b=80),
            template="plotly_white",
            xaxis=dict(range=[0, 1.0]),
            font=dict(size=12)
        )
        
        figs.append((organelle, fig))
    
    return figs


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


def create_scores_summary_page(df):
    """
    Create a simple summary page with links to individual organelle pages
    """
    organelles = sorted(df['organelle'].unique())
    
    # Get best F1 for each organelle
    best_scores = df.loc[df.groupby('organelle')['f1'].idxmax()]
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Scores by Organelle</title>
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
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
    <h1>🎯 Model Performance by Organelle</h1>
    
    <div class="summary">
        <p><strong>Total Evaluations:</strong> {len(df)}</p>
        <p><strong>Unique Setups:</strong> {df['setup'].nunique()}</p>
        <p><strong>Organelles Tested:</strong> {', '.join(organelles)}</p>
    </div>
    
    <div class="organelle-grid">
"""
    
    for organelle in organelles:
        org_data = df[df['organelle'] == organelle]
        best = best_scores[best_scores['organelle'] == organelle].iloc[0]
        
        html += f"""
        <div class="organelle-card">
            <div class="organelle-name">{organelle}</div>
            <div class="best-f1">{best['f1']:.4f}</div>
            <div class="stats">
                <div><span class="stat-label">Best Setup:</span> {best['setup']}</div>
                <div><span class="stat-label">Iteration:</span> {int(best['iteration']) if pd.notna(best['iteration']) else 'N/A'}</div>
                <div><span class="stat-label">Total Evaluations:</span> {len(org_data)}</div>
                <div><span class="stat-label">Setups Tested:</span> {org_data['setup'].nunique()}</div>
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
    print("✅ Scores summary page saved to 'output/visualizations/scores_by_organelle.html'")

    # Create best scores table
    best_scores_fig = create_best_scores_table(df)
    best_scores_fig.write_html("output/visualizations/best_scores.html")
    print("✅ Best scores table saved to 'output/visualizations/best_scores.html'")

    # Create iteration progression chart (if multiple iterations exist)
    iteration_fig = create_iteration_progression(df)
    if iteration_fig:
        iteration_fig.write_html("output/visualizations/iteration_progression.html")
        print("✅ Iteration progression saved to 'output/visualizations/iteration_progression.html'")
    else:
        print("⚠️  No iteration progression data (need multiple checkpoints per setup)")

    print("\n🎉 All score visualizations generated successfully!")
    print("📁 Main page: output/visualizations/scores_by_organelle.html")

    return stats


if __name__ == "__main__":
    stats = main()
