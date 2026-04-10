# preprocessing.py
import io
import chardet
import pandas as pd
import numpy as np
from pathlib import Path


# ── CSV Loader (handles all encodings + separators) ───────────────
def load_csv(file) -> tuple[pd.DataFrame, dict]:
    """
    Smartly load any CSV file.
    Handles: encoding detection, separators, multi-headers,
             large files, Excel exports, and more.

    Returns:
        df:   loaded DataFrame
        info: dict with loading metadata
    """
    info = {
        "encoding":     "utf-8",
        "separator":    ",",
        "rows":         0,
        "columns":      0,
        "warnings":     [],
        "skipped_cols": [],
    }

    # ── Step 1: Read raw bytes ────────────────────────────────
    if hasattr(file, "read"):
        raw = file.read()
        if hasattr(file, "seek"):
            file.seek(0)
    else:
        raw = Path(file).read_bytes()

    # ── Step 2: Detect encoding ───────────────────────────────
    detected   = chardet.detect(raw)
    encoding   = detected.get("encoding") or "utf-8"
    confidence = detected.get("confidence", 0)

    # Fallback chain for common encodings
    encodings_to_try = [encoding, "utf-8", "latin-1",
                        "cp1252", "iso-8859-1", "utf-16"]
    encodings_to_try = list(dict.fromkeys(encodings_to_try))

    text = None
    for enc in encodings_to_try:
        try:
            text = raw.decode(enc)
            info["encoding"] = enc
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if text is None:
        text = raw.decode("utf-8", errors="replace")
        info["warnings"].append("Could not detect encoding — used UTF-8 with replacements")

    # ── Step 3: Detect separator ──────────────────────────────
    first_line = text.split("\n")[0]
    sep_counts = {
        ",":  first_line.count(","),
        ";":  first_line.count(";"),
        "\t": first_line.count("\t"),
        "|":  first_line.count("|"),
    }
    separator = max(sep_counts, key=sep_counts.get)
    if sep_counts[separator] == 0:
        separator = ","
    info["separator"] = separator
# ── Step 4: Load with pandas ──────────────────────────────
    try:
        df = pd.read_csv(
            io.StringIO(text),
            sep=separator,
            engine="python",
            on_bad_lines="skip",
        )
    except Exception as e:
        info["warnings"].append(f"Standard load failed: {e}. Trying fallback.")
        try:
            # Fallback — keep header row, just be more lenient
            df = pd.read_csv(
                io.StringIO(text),
                sep=separator,
                engine="python",
                on_bad_lines="skip",
                header=0,      # ← always use first row as header
            )
        except Exception as e2:
            raise ValueError(f"Could not load CSV: {e2}")

    # ── Step 5: Clean column names ────────────────────────────
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Drop unnamed columns (common in Excel exports)
    unnamed = [c for c in df.columns if c.startswith("Unnamed:")]
    if unnamed:
        df = df.drop(columns=unnamed)
        info["warnings"].append(
            f"Dropped {len(unnamed)} unnamed columns (Excel export artifact)"
        )

    # ── Step 6: Drop fully empty rows and columns ─────────────
    df = df.dropna(how="all")
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)
        info["warnings"].append(
            f"Dropped {len(empty_cols)} fully empty columns"
        )

    # ── Step 7: Handle wide CSVs (100+ columns) ───────────────
    if len(df.columns) > 100:
        info["warnings"].append(
            f"Wide CSV detected ({len(df.columns)} columns). "
            "Keeping first 60 columns for performance."
        )
        df = df.iloc[:, :60]

    # ── Step 8: Handle large files (500k+ rows) ───────────────
    if len(df) > 500_000:
        info["warnings"].append(
            f"Large file detected ({len(df):,} rows). "
            "Sampling 100,000 rows for performance."
        )
        df = df.sample(n=100_000, random_state=42).reset_index(drop=True)

    # ── Step 9: Try to parse numeric columns stored as strings
    for col in df.select_dtypes(include="object").columns:
        # Try stripping currency symbols and commas
        cleaned = (
            df[col]
            .astype(str)
            .str.replace(r"[\$,€£¥₹,\s]", "", regex=True)
            .str.strip()
        )
        converted = pd.to_numeric(cleaned, errors="coerce")
        # Only convert if >60% of values successfully converted
        if converted.notna().mean() > 0.6:
            df[col] = converted
            info["warnings"].append(
                f"Auto-converted '{col}' from string to numeric"
            )
    # ── Step 10: Drop columns that are all one unique value ───
    # Only drop numeric constant columns, keep categorical ones
    # (e.g. "Country = United States" is useful context)
    single_val_cols = [
        c for c in df.columns
        if df[c].nunique() <= 1
        and len(df) > 5
        and pd.api.types.is_numeric_dtype(df[c])  # ← only numeric
    ]
    if single_val_cols:
        # Print exactly what is being dropped and why
        print(f"🗑️ Dropping {len(single_val_cols)} constant columns:")
        for col in single_val_cols:
            unique_val = df[col].dropna().unique()
            print(f"   - '{col}': constant value = {unique_val}")

        df = df.drop(columns=single_val_cols)
        info["skipped_cols"] = single_val_cols
        info["warnings"].append(
            f"Dropped {len(single_val_cols)} constant numeric columns: "
            f"{single_val_cols[:5]}"
        )
    # ── Final: update info and return ────────────────────────
    info["rows"]    = len(df)
    info["columns"] = len(df.columns)

    return df, info  # ← add this

# ── Date preprocessor ─────────────────────────────────────────────
def preprocess_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-detect date columns and add helper columns.
    Handles multiple date formats robustly.
    """
    df = df.copy()
    date_columns = []

    for col in df.columns:
        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_columns.append(col)
            continue

        # Name hints at a date
        if any(x in col.lower() for x in
               ["date", "time", "day", "month", "year",
                "created", "updated", "timestamp", "dt"]):
            # Try multiple formats
            for fmt in [None, "%d/%m/%Y", "%m/%d/%Y",
                        "%Y-%m-%d", "%d-%m-%Y",
                        "%Y/%m/%d", "%d.%m.%Y"]:
                try:
                    parsed = pd.to_datetime(
                        df[col], format=fmt,
                        errors="coerce", dayfirst=True
                    )
                    success_rate = parsed.notna().mean()
                    if success_rate > 0.5:
                        df[col] = parsed
                        date_columns.append(col)
                        break
                except Exception:
                    continue

    # Add helper columns for each date column
    for col in date_columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[f"{col}_year"]       = df[col].dt.year
            df[f"{col}_month"]      = df[col].dt.month
            df[f"{col}_day"]        = df[col].dt.day
            df[f"{col}_quarter"]    = df[col].dt.quarter
            df[f"{col}_dayofweek"]  = df[col].dt.day_name()
            df[f"{col}_year_month"] = (
                df[col].dt.to_period("M").astype(str)
            )

    return df


# ── Schema description ────────────────────────────────────────────
def get_schema_description(df: pd.DataFrame, max_rows: int = 3) -> str:
    """
    Build a smart text description of the DataFrame.
    Handles wide CSVs, non-English columns, and mixed types.
    """
    # Identify numeric columns
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    schema_lines = [
        f"Dataset: {len(df):,} rows × {len(df.columns)} columns",
        f"Numeric columns (valid for target_column): "
        f"{', '.join(numeric_cols) if numeric_cols else 'None'}",
        "",
        "All Columns:"
    ]

    for col, dtype in df.dtypes.items():
        null_pct = df[col].isna().mean() * 100
        null_str = f" | {null_pct:.0f}% null" if null_pct > 0 else ""

        if pd.api.types.is_numeric_dtype(df[col]):
            try:
                mn  = df[col].min()
                mx  = df[col].max()
                avg = df[col].mean()
                schema_lines.append(
                    f"- {col} ({dtype}){null_str} "
                    f"[min={mn:.2f}, max={mx:.2f}, avg={avg:.2f}]"
                )
            except Exception:
                schema_lines.append(f"- {col} ({dtype}){null_str}")

        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            try:
                mn = df[col].min().strftime("%Y-%m-%d")
                mx = df[col].max().strftime("%Y-%m-%d")
                schema_lines.append(
                    f"- {col} (datetime){null_str} "
                    f"[range: {mn} to {mx}]"
                )
            except Exception:
                schema_lines.append(f"- {col} (datetime){null_str}")

        else:
            n_unique = df[col].nunique()
            if n_unique <= 20:
                vals = df[col].dropna().unique()[:6]
                sample = ", ".join(map(str, vals))
                schema_lines.append(
                    f"- {col} ({dtype}){null_str} "
                    f"[{n_unique} unique: {sample}]"
                )
            else:
                schema_lines.append(
                    f"- {col} ({dtype}){null_str} "
                    f"[{n_unique} unique values]"
                )

    # Sample rows
    sample = df.head(max_rows).to_string(index=False)
    schema_lines.append("\nSample rows:")
    schema_lines.append(sample)

    return "\n".join(schema_lines)


# ── CSV Validator ─────────────────────────────────────────────────
def validate_csv(df: pd.DataFrame) -> dict:
    """
    Run pre-analysis checks and return a validation report.
    Shows warnings in the Streamlit UI before analysis starts.
    """
    issues   = []
    warnings = []
    tips     = []

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # Check for numeric columns
    if not numeric_cols:
        issues.append(
            "No numeric columns found. "
            "The agent needs at least one numeric column to analyze "
            "(e.g. Sales, Price, Count, Score)."
        )
    elif len(numeric_cols) == 1:
        warnings.append(
            f"Only one numeric column found: '{numeric_cols[0]}'. "
            "Most questions will analyze this column."
        )

    # Check for enough rows
    if len(df) < 5:
        issues.append(
            f"Too few rows ({len(df)}). "
            "Need at least 5 rows for meaningful analysis."
        )

    # Check for high null percentage
    for col in df.columns:
        null_pct = df[col].isna().mean() * 100
        if null_pct > 80:
            warnings.append(
                f"Column '{col}' is {null_pct:.0f}% empty — "
                "may affect analysis quality."
            )

    # Check for duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        pct = dup_count / len(df) * 100
        warnings.append(
            f"{dup_count:,} duplicate rows found ({pct:.1f}%). "
            "Consider deduplicating before analysis."
        )

    # Check for date columns
    date_cols = [
        c for c in df.columns
        if any(x in c.lower() for x in
               ["date", "time", "day", "month", "year"])
    ]
    if date_cols:
        tips.append(
            f"Date columns detected: {date_cols}. "
            "You can ask time-based questions like "
            "'Show monthly trend' or 'Which year had the highest sales?'"
        )

    # Tips based on column count
    # Tips based on column count
    # Filter out likely ID/code columns from the tip
    meaningful_numeric = [
        c for c in numeric_cols
        if not any(x in c.lower() for x in
                   ["id", "code", "zip", "postal",
                    "phone", "index", "row", "key"])
    ]

    if len(meaningful_numeric) > 1:
        tips.append(
            f"Numeric columns available for analysis: "
            f"{meaningful_numeric}. "
            "Specify which one in your question for best results "
            "(e.g. 'total Sales' or 'average Price')."
        )
    elif len(meaningful_numeric) == 1:
        tips.append(
            f"Main numeric column: '{meaningful_numeric[0]}'. "
            "Most questions will analyze this column."
        )

    return {
        "valid":    len(issues) == 0,
        "issues":   issues,
        "warnings": warnings,
        "tips":     tips,
    }