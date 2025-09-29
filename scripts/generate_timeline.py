#!/usr/bin/env python3
"""
Experiment Timeline Visualization
Generates an interactive timeline graph from the experiment overview CSV
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np


def parse_dates(df):
    """Parse and clean creation dates"""
    # Handle missing dates for mitochondria experiments (no creation date)
    # Assume they started around the same time as other experiments
    df = df.copy()

    # Fill missing dates for mito experiments (likely started around 2025-09-15 based on job info)
    mito_mask = (df["Group"] == "exp_mito") & (
        df["Creation Date"].isna() | (df["Creation Date"] == "")
    )
    df.loc[mito_mask, "Creation Date"] = "2025-09-15"

    # Handle date ranges like "2025-07-25/08-06"
    df.loc[df["Creation Date"] == "2025-07-25/08-06", "Creation Date"] = "2025-07-25"

    # Remove entries without proper dates
    df = df[
        df["Creation Date"].notna()
        & (df["Creation Date"] != "")
        & (df["Creation Date"] != "-")
    ]

    # Convert to datetime
    df["Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    return df


def create_timeline_graph():
    """Create interactive timeline visualization"""

    # Read CSV data
    df = pd.read_csv("overview.csv")

    # Parse dates
    df = parse_dates(df)

    # Extract setup numbers for sorting (handle non-setup entries)
    def extract_setup_num(setup):
        if "setup_" in str(setup):
            try:
                return int(setup.split("_")[1])
            except:
                return 999
        else:
            return 1000  # Put non-setup entries at the end

    df["setup_num"] = df["Setup"].apply(extract_setup_num)
    df = df.sort_values(["Date", "setup_num"])

    # Create color mapping for experiment groups
    group_colors = {
        "exp_mito": "#FF6B6B",  # Red for mitochondria
        "exp_pancreas": "#4ECDC4",  # Teal for pancreas
        "exp_cell": "#45B7D1",  # Blue for cell
        "exp_cerebellum": "#96CEB4",  # Green for cerebellum
        "exp_c-elegen_v2": "#FECA57",  # Yellow for C. elegans v2
        "exp_c-elegen_v3": "#FF9FF3",  # Pink for C. elegans v3
        "exp_c-elegen_v4": "#54A0FF",  # Light blue for C. elegans v4
    }

    # Create status symbols
    df["Symbol"] = df["Still Running"].map({"YES": "circle", "NO": "square"})
    df["Status"] = df["Still Running"].map({"YES": "Running", "NO": "Completed"})

    # Create the main timeline figure
    fig = go.Figure()

    # Add traces for each group
    for group in df["Group"].unique():
        group_data = df[df["Group"] == group]

        fig.add_trace(
            go.Scatter(
                x=group_data["Date"],
                y=group_data["Setup"],
                mode="markers+text",
                name=group.replace("exp_", "").replace("_", " ").title(),
                marker=dict(
                    size=12,
                    color=group_colors.get(group, "#95A5A6"),
                    symbol=group_data["Symbol"],
                    line=dict(width=2, color="white"),
                ),
                text=group_data["Setup"],
                textposition="middle right",
                textfont=dict(size=10),
                hovertemplate="<b>%{text}</b><br>"
                + "Group: "
                + group
                + "<br>"
                + "Target: %{customdata[0]}<br>"
                + "Model: %{customdata[1]}<br>"
                + "Status: %{customdata[2]}<br>"
                + "Date: %{x}<br>"
                + "<extra></extra>",
                customdata=group_data[["Target", "Model Type", "Status"]].values,
            )
        )

    # Update layout
    fig.update_layout(
        title={
            "text": "🧪 Machine Learning Experiment Timeline<br><sub>Model Training Experiments Across Different Biological Groups</sub>",
            "x": 0.5,
            "font": {"size": 20},
        },
        xaxis_title="Creation Date",
        yaxis_title="Experiment Setup",
        height=800,
        width=1200,
        hovermode="closest",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(r=200),
        template="plotly_white",
    )

    # Add annotations for running vs completed
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text="● Running | ■ Completed",
        showarrow=False,
        font=dict(size=12),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
    )

    return fig


def create_gantt_chart():
    """Create a Gantt-style chart showing experiment duration"""

    df = pd.read_csv("overview.csv")
    df = parse_dates(df)

    # Estimate end dates for completed experiments (assume 30-90 days duration)
    # For running experiments, use current date
    current_date = datetime(2025, 9, 29)

    df["Start"] = df["Date"]
    df["End"] = df.apply(
        lambda row: (
            current_date
            if row["Still Running"] == "YES"
            else row["Date"] + timedelta(days=60)
        ),
        axis=1,
    )

    # Create Gantt chart
    fig = go.Figure()

    group_colors = {
        "exp_mito": "#FF6B6B",
        "exp_pancreas": "#4ECDC4",
        "exp_cell": "#45B7D1",
        "exp_cerebellum": "#96CEB4",
        "exp_c-elegen_v2": "#FECA57",
        "exp_c-elegen_v3": "#FF9FF3",
        "exp_c-elegen_v4": "#54A0FF",
    }

    y_pos = 0
    for _, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["Start"], row["End"]],
                y=[y_pos, y_pos],
                mode="lines+markers",
                line=dict(width=8, color=group_colors.get(row["Group"], "#95A5A6")),
                marker=dict(size=8),
                name=f"{row['Setup']} ({row['Group'].replace('exp_', '')})",
                hovertemplate=f"<b>{row['Setup']}</b><br>"
                + f"Group: {row['Group']}<br>"
                + f"Target: {row['Target']}<br>"
                + f"Status: {row['Still Running']}<br>"
                + "Start: %{x[0]}<br>"
                + "End: %{x[1]}<br>"
                + "<extra></extra>",
                showlegend=False,
            )
        )
        y_pos += 1

    # Update layout
    fig.update_layout(
        title="🗓️ Experiment Duration Timeline (Gantt Chart)",
        xaxis_title="Timeline",
        yaxis_title="Experiments",
        height=max(600, len(df) * 25),
        yaxis=dict(tickvals=list(range(len(df))), ticktext=df["Setup"].tolist()),
        template="plotly_white",
    )

    return fig


def create_summary_stats():
    """Create summary statistics visualization"""

    df = pd.read_csv("overview.csv")
    df = parse_dates(df)

    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Experiments by Group",
            "Running vs Completed",
            "Model Types",
            "Target Distribution",
        ),
        specs=[[{"type": "bar"}, {"type": "pie"}], [{"type": "bar"}, {"type": "pie"}]],
    )

    # 1. Experiments by group
    group_counts = df["Group"].value_counts()
    fig.add_trace(
        go.Bar(x=group_counts.index, y=group_counts.values, name="By Group"),
        row=1,
        col=1,
    )

    # 2. Running vs Completed
    status_counts = df["Still Running"].value_counts()
    fig.add_trace(
        go.Pie(labels=status_counts.index, values=status_counts.values, name="Status"),
        row=1,
        col=2,
    )

    # 3. Model types
    model_counts = df["Model Type"].value_counts()
    fig.add_trace(
        go.Bar(x=model_counts.index, y=model_counts.values, name="Models"), row=2, col=1
    )

    # 4. Target distribution
    target_counts = df["Target"].value_counts()
    fig.add_trace(
        go.Pie(labels=target_counts.index, values=target_counts.values, name="Targets"),
        row=2,
        col=2,
    )

    fig.update_layout(
        height=800, title_text="📊 Experiment Overview Statistics", showlegend=False
    )

    return fig


def create_main_page():
    """Create the main landing page for GitHub Pages"""

    # Read CSV to get latest stats
    df = pd.read_csv("overview.csv")
    df = parse_dates(df)

    total_experiments = len(df)
    running_experiments = len(df[df["Still Running"] == "YES"])
    completed_experiments = len(df[df["Still Running"] == "NO"])
    unique_groups = len(df["Group"].unique())

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experiment Timeline Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 3rem;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .stat-number {{
            font-size: 3rem;
            font-weight: bold;
            display: block;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .visualizations {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .viz-card {{
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .viz-card:hover {{
            transform: translateY(-5px);
        }}
        
        .viz-card h2 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .viz-card p {{
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }}
        
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 3rem;
            color: white;
            opacity: 0.8;
        }}
        
        .github-link {{
            color: white;
            text-decoration: none;
            margin-top: 1rem;
            display: inline-block;
        }}
        
        .github-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Experiment Timeline Dashboard</h1>
            <p>Machine Learning Model Training Experiments Across Biological Groups</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{total_experiments}</span>
                <span class="stat-label">Total Experiments</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{running_experiments}</span>
                <span class="stat-label">Currently Running</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{completed_experiments}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{unique_groups}</span>
                <span class="stat-label">Experiment Groups</span>
            </div>
        </div>
        
        <div class="visualizations">
            <div class="viz-card">
                <h2>📅 Interactive Timeline</h2>
                <p>Explore the chronological progression of all experiments with detailed hover information and group-based color coding.</p>
                <a href="experiment_timeline.html" class="btn">View Timeline</a>
            </div>
            
            <div class="viz-card">
                <h2>📊 Gantt Chart</h2>
                <p>Visualize experiment durations and overlaps in a comprehensive Gantt chart format.</p>
                <a href="experiment_gantt.html" class="btn">View Gantt Chart</a>
            </div>
            
            <div class="viz-card">
                <h2>📈 Statistics Dashboard</h2>
                <p>Comprehensive statistics and breakdowns by experiment group, model type, and targets.</p>
                <a href="experiment_stats.html" class="btn">View Statistics</a>
            </div>
            
            <div class="viz-card">
                <h2>📋 Raw Data</h2>
                <p>Access the complete experiment data in CSV format for further analysis.</p>
                <a href="overview.csv" class="btn">Download CSV</a>
            </div>
            
            <div class="viz-card">
                <h2>📖 Documentation</h2>
                <p>Detailed documentation about all experiments, configurations, and model architectures.</p>
                <a href="README.md" class="btn">Read Documentation</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}</p>
            <a href="https://github.com/mzouink/guided_net" class="github-link">
                🔗 View on GitHub
            </a>
        </div>
    </div>
</body>
</html>
"""

    with open("index.html", "w") as f:
        f.write(html_content)


if __name__ == "__main__":
    print("🚀 Generating experiment timeline visualizations...")

    # Generate main landing page
    create_main_page()
    print("✅ Main page saved as 'index.html'")

    # Generate timeline
    timeline_fig = create_timeline_graph()
    timeline_fig.write_html("experiment_timeline.html")
    print("✅ Timeline saved as 'experiment_timeline.html'")

    # Generate Gantt chart
    gantt_fig = create_gantt_chart()
    gantt_fig.write_html("experiment_gantt.html")
    print("✅ Gantt chart saved as 'experiment_gantt.html'")

    # Generate summary stats
    stats_fig = create_summary_stats()
    stats_fig.write_html("experiment_stats.html")
    print("✅ Statistics saved as 'experiment_stats.html'")

    print("\n📈 All visualizations generated successfully!")
    print("🌐 Website ready for GitHub Pages deployment!")
    print(
        "Files: index.html, experiment_timeline.html, experiment_gantt.html, experiment_stats.html"
    )
