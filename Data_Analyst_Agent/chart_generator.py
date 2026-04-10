# chart_generator.py
import matplotlib
matplotlib.use('Agg')  # ← must be BEFORE any other matplotlib import
import io
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def generate_chart(df: pd.DataFrame, plan: dict) -> io.BytesIO | None:
    """Generate a chart from the result DataFrame and plan. Returns a PNG buffer."""

    if not plan.get("need_chart") or df.empty:
        return None

    chart_type = plan.get("chart_type", "bar")
    group_by   = plan.get("group_by") or []
    target_col = plan.get("target_column")
    metric     = plan.get("metric", "sum")

    if not target_col or target_col not in df.columns:
        return None

    # ── Only keep top 15 rows for readability ─────────────────
    plot_df = df.head(15).copy()

    fig, ax = plt.subplots(figsize=(11, 6))

    if group_by and len(group_by) > 0:
        x_col  = group_by[0]

        if x_col not in plot_df.columns:
            return None

        x_labels = plot_df[x_col].astype(str).tolist()
        y_values = plot_df[target_col].tolist()
        colors   = sns.color_palette("husl", len(plot_df))

        # ── Bar chart ─────────────────────────────────────────
        if chart_type == "bar":
            bars = ax.bar(range(len(plot_df)), y_values, color=colors, edgecolor='white', linewidth=0.5)
            ax.set_xticks(range(len(plot_df)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
            ax.set_ylabel(f"{metric.upper()} of {target_col}", fontsize=12)
            ax.set_xlabel(x_col, fontsize=12)
            # Value labels on top of each bar
            for bar, val in zip(bars, y_values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(y_values) * 0.01,
                    f'{val:,.2f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold'
                )

        # ── Horizontal bar chart ──────────────────────────────
        elif chart_type == "barh":
            bars = ax.barh(range(len(plot_df)), y_values, color=colors, edgecolor='white', linewidth=0.5)
            ax.set_yticks(range(len(plot_df)))
            ax.set_yticklabels(x_labels, fontsize=10)
            ax.set_xlabel(f"{metric.upper()} of {target_col}", fontsize=12)
            ax.set_ylabel(x_col, fontsize=12)
            ax.invert_yaxis()
            for bar, val in zip(bars, y_values):
                ax.text(
                    bar.get_width() + max(y_values) * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    f'{val:,.2f}',
                    va='center', fontsize=9, fontweight='bold'
                )

        # ── Line chart ────────────────────────────────────────
        elif chart_type == "line":
            ax.plot(range(len(plot_df)), y_values,
                    marker='o', linewidth=2.5, markersize=8,
                    color=colors[0], markerfacecolor='white',
                    markeredgewidth=2)
            ax.fill_between(range(len(plot_df)), y_values, alpha=0.1, color=colors[0])
            ax.set_xticks(range(len(plot_df)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
            ax.set_ylabel(f"{metric.upper()} of {target_col}", fontsize=12)
            ax.set_xlabel(x_col, fontsize=12)
            # Value labels on each point
            for i, val in enumerate(y_values):
                ax.text(i, val + max(y_values) * 0.02, f'{val:,.2f}',
                        ha='center', fontsize=9, fontweight='bold')

        # ── Area chart ────────────────────────────────────────
        elif chart_type == "area":
            ax.fill_between(range(len(plot_df)), y_values, alpha=0.4, color=colors[0])
            ax.plot(range(len(plot_df)), y_values, color=colors[0], linewidth=2)
            ax.set_xticks(range(len(plot_df)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
            ax.set_ylabel(f"{metric.upper()} of {target_col}", fontsize=12)
            ax.set_xlabel(x_col, fontsize=12)

        # ── Pie chart ─────────────────────────────────────────
        elif chart_type == "pie":
            pie_df = plot_df.head(8)  # max 8 slices for readability
            wedges, texts, autotexts = ax.pie(
                pie_df[target_col],
                labels=pie_df[x_col].astype(str),
                autopct='%1.1f%%',
                startangle=90,
                colors=sns.color_palette("husl", len(pie_df)),
                wedgeprops=dict(edgecolor='white', linewidth=1.5)
            )
            for text in autotexts:
                text.set_fontsize(9)
                text.set_fontweight('bold')
            ax.axis('equal')

        # ── Scatter chart ─────────────────────────────────────
        elif chart_type == "scatter":
            ax.scatter(range(len(plot_df)), y_values,
                       c=colors, s=150, edgecolors='white', linewidth=1.5, zorder=3)
            ax.set_xticks(range(len(plot_df)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
            ax.set_ylabel(f"{metric.upper()} of {target_col}", fontsize=12)
            ax.set_xlabel(x_col, fontsize=12)

        # ── Fallback → bar ────────────────────────────────────
        else:
            bars = ax.bar(range(len(plot_df)), y_values, color=colors)
            ax.set_xticks(range(len(plot_df)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)

        title = f"{metric.upper()} of {target_col} by {x_col}"

    # ── No group_by — single value bar ───────────────────────
    else:
        val = df[target_col].iloc[0]
        ax.bar([target_col], [val], color=sns.color_palette("husl", 1))
        ax.text(0, val + val * 0.01, f'{val:,.2f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
        title = f"{metric.upper()} of {target_col}"

    # ── Formatting ────────────────────────────────────────────
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    fig.tight_layout()

    # ── Save to buffer ────────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf