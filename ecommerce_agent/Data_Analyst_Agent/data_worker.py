# data_worker.py
import pandas as pd


# ── Special: Null value checker ───────────────────────────────────
def check_null_values(df: pd.DataFrame) -> pd.DataFrame:
    """Check null/missing values across all columns."""
    null_counts   = df.isnull().sum()
    total_rows    = len(df)
    null_pct      = (null_counts / total_rows * 100).round(2)

    result = pd.DataFrame({
        "Column":        null_counts.index,
        "Null_Count":    null_counts.values,
        "Total_Rows":    total_rows,
        "Null_Percent":  null_pct.values,
        "Complete_Rows": total_rows - null_counts.values,
    })

    # Show columns with nulls first, then complete columns
    result = pd.concat([
        result[result["Null_Count"] > 0].sort_values(
            "Null_Count", ascending=False),
        result[result["Null_Count"] == 0]
    ]).reset_index(drop=True)

    return result


# ── Filter applier ────────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, filters: list) -> pd.DataFrame:
    """Apply a list of filters — handles both dict and string formats."""
    if not filters:
        return df

    filtered = df.copy()
    for f in filters:

        # ── Handle string format e.g. "Region == 'West'" ──────
        if isinstance(f, str):
            import re
            # Try to parse "Column op 'Value'" or "Column op Value"
            match = re.match(
                r"([A-Za-z\s\-]+)\s*(==|!=|>=|<=|>|<)\s*['\"]?([^'\"]+)['\"]?",
                f.strip()
            )
            if match:
                col = match.group(1).strip()
                op  = match.group(2).strip()
                val = match.group(3).strip()
                f   = {"column": col, "op": op, "value": val}
            else:
                print(f"⚠️ Could not parse filter string: '{f}', skipping.")
                continue

        # ── Handle dict format (normal) ───────────────────────
        col = f.get("column")
        op  = f.get("op")
        val = f.get("value")

        if col not in filtered.columns:
            print(f"⚠️ Filter column '{col}' not found, skipping.")
            continue

        try:
            val_cast = pd.to_numeric(val)
        except:
            val_cast = val

        if op == "==":
            filtered = filtered[filtered[col] == val_cast]
        elif op == "!=":
            filtered = filtered[filtered[col] != val_cast]
        elif op == ">":
            filtered = filtered[filtered[col] > val_cast]
        elif op == "<":
            filtered = filtered[filtered[col] < val_cast]
        elif op == ">=":
            filtered = filtered[filtered[col] >= val_cast]
        elif op == "<=":
            filtered = filtered[filtered[col] <= val_cast]
        elif op == "contains":
            filtered = filtered[filtered[col].astype(str).str.contains(
                str(val_cast), case=False, na=False)]
        elif op == "startswith":
            filtered = filtered[filtered[col].astype(str).str.startswith(
                str(val_cast))]
        elif op == "endswith":
            filtered = filtered[filtered[col].astype(str).str.endswith(
                str(val_cast))]
        elif op == "not_contains":
            filtered = filtered[~filtered[col].astype(str).str.contains(
                str(val_cast), case=False, na=False)]
        elif op == "isnull":
            filtered = filtered[filtered[col].isnull()]
        elif op == "notnull":
            filtered = filtered[filtered[col].notnull()]
        elif op == "isin":
            val_list = val if isinstance(val, list) else [val]
            filtered = filtered[filtered[col].isin(val_list)]
        elif op == "notin":
            val_list = val if isinstance(val, list) else [val]
            filtered = filtered[~filtered[col].isin(val_list)]
        elif op == "between":
            if isinstance(val, list) and len(val) == 2:
                filtered = filtered[filtered[col].between(val[0], val[1])]

    return filtered

# ── Main analysis runner ──────────────────────────────────────────
def run_analysis_plan(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    """Execute the analysis plan on the DataFrame and return results."""

    op         = plan.get("operation")
    target_col = plan.get("target_column")
    group_by   = plan.get("group_by") or []
    filters    = plan.get("filters") or []
    metric     = plan.get("metric", "sum")
    top_n      = plan.get("top_n", None)
    sort_asc   = plan.get("sort_ascending", False)

    # ── Special case: null/missing value check ────────────────
    null_keywords = [
        "null", "missing", "nan", "empty",
        "incomplete", "na value", "null value",
        "how many null", "any null", "check null"
    ]
    question_hint = plan.get("question_hint", "").lower()
    if any(k in question_hint for k in null_keywords):
        print("🔍 Null check detected — running check_null_values()")
        return check_null_values(df)

    # ── Step 1: Apply filters ─────────────────────────────────
    if filters:
        df = apply_filters(df, filters)

    # ── Step 2: Validate target column ───────────────────────
    if not target_col or target_col not in df.columns:
        print(f"⚠️ Target column '{target_col}' not found. Returning preview.")
        return df.head(10)

    # ── Step 2b: Check target column is numeric ───────────────
    if not pd.api.types.is_numeric_dtype(df[target_col]):
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            print(f"⚠️ '{target_col}' is not numeric. "
                  f"Switching to '{numeric_cols[0]}'")
            target_col = numeric_cols[0]
            plan["target_column"] = target_col
        else:
            print("⚠️ No numeric columns found. Returning preview.")
            return df.head(10)

    # ── Step 3: No group_by — single aggregation ─────────────
    if not group_by:
        try:
            agg_funcs = {
                "sum":     df[target_col].sum(),
                "mean":    df[target_col].mean(),
                "count":   df[target_col].count(),
                "max":     df[target_col].max(),
                "min":     df[target_col].min(),
                "median":  df[target_col].median(),
                "std":     df[target_col].std(),
                "var":     df[target_col].var(),
                "nunique": df[target_col].nunique(),
                "first":   df[target_col].iloc[0] if len(df) > 0 else None,
                "last":    df[target_col].iloc[-1] if len(df) > 0 else None,
            }
            value = agg_funcs.get(metric, df[target_col].sum())
        except Exception as e:
            print(f"⚠️ Aggregation failed: {e}. Returning count instead.")
            value = df[target_col].count()
        return pd.DataFrame({f"{metric}_{target_col}": [value]})

    # ── Step 4: Group by + aggregation ───────────────────────
    agg_map = {
        "sum":     "sum",
        "mean":    "mean",
        "count":   "count",
        "max":     "max",
        "min":     "min",
        "median":  "median",
        "std":     "std",
        "var":     "var",
        "nunique": "nunique",
        "first":   "first",
        "last":    "last",
    }

    agg_df = (
        df.groupby(group_by)[target_col]
        .agg(agg_map.get(metric, "sum"))
        .reset_index()
        .sort_values(by=target_col, ascending=sort_asc)
    )

    # ── Step 5: Top N filter ──────────────────────────────────
    if top_n and isinstance(top_n, int):
        agg_df = agg_df.head(top_n)

    # ── Step 6: Add percentage column ────────────────────────
    if metric in ("sum", "count", "mean") and len(agg_df) > 1:
        total = agg_df[target_col].sum()
        if total > 0:
            agg_df[f"{target_col}_pct"] = (
                (agg_df[target_col] / total * 100).round(2)
            )

    return agg_df