# pipeline.py
import json
import pandas as pd
from collections import deque
from preprocessing import load_csv, validate_csv, preprocess_dates, get_schema_description
from planner import call_planner_llm
from data_worker import run_analysis_plan, check_null_values
from chart_generator import generate_chart
from explainer import call_explainer_llm


# ── Keywords ──────────────────────────────────────────────────────
NULL_KEYWORDS = [
    "null", "missing", "nan", "empty",
    "incomplete", "na value", "null value",
    "how many null", "any null", "check null",
    "missing value", "missing data"
]

COUNT_KEYWORDS = [
    "how many orders", "how many records",
    "count of orders", "number of orders",
    "how many times", "how many rows",
    "how many customers", "how many products",
    "how many shipments", "how many items"
]


# ── Conversation Memory ───────────────────────────────────────────
class ConversationMemory:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.turns = deque(maxlen=max_turns)

    def add_turn(self, question, plan, result_summary, explanation):
        self.turns.append({
            "question":       question,
            "plan":           plan,
            "result_summary": result_summary,
            "explanation":    explanation,
        })

    def get_context(self) -> str:
        if not self.turns:
            return ""
        lines = ["Previous questions and analysis in this session:"]
        for i, turn in enumerate(self.turns, 1):
            lines.append(f"\n[Turn {i}]")
            lines.append(f"  Question:    {turn['question']}")
            lines.append(f"  Plan:        {json.dumps(turn['plan'])}")
            lines.append(f"  Top results: {turn['result_summary']}")
            lines.append(f"  Insight:     {turn['explanation'][:150]}...")
        lines.append(
            "\nUse this history to understand follow-up questions. "
            "If the user says 'now filter by X' or 'show me just Y', "
            "build on the previous plan accordingly."
        )
        return "\n".join(lines)

    def clear(self):
        self.turns.clear()

    def is_empty(self) -> bool:
        return len(self.turns) == 0

    def last_plan(self) -> dict | None:
        if self.turns:
            return self.turns[-1]["plan"]
        return None

    def summary(self) -> str:
        if self.is_empty():
            return "Memory is empty."
        lines = [f"Memory has {len(self.turns)} turn(s):"]
        for i, turn in enumerate(self.turns, 1):
            lines.append(f"  [{i}] {turn['question']}")
        return "\n".join(lines)


# ── Planner with memory ───────────────────────────────────────────
def call_planner_with_memory(
    schema_text: str,
    question: str,
    memory: ConversationMemory
) -> dict:
    context = memory.get_context()
    enriched_schema = (
        f"{schema_text}\n\n{context}" if context else schema_text
    )
    return call_planner_llm(enriched_schema, question)


# ── Shared: finish pipeline after result_df is ready ─────────────
def _finish_pipeline(
    df: pd.DataFrame,
    question: str,
    plan: dict,
    result_df: pd.DataFrame,
    memory: ConversationMemory,
    tone: str,
    language: str,
    verbose: bool,
    output: dict,
    label: str = "Pipeline"
) -> dict:
    """Generate chart, explanation, save to memory, return output."""

    output["plan"]      = plan
    output["result_df"] = result_df

    # Chart
    if verbose:
        print("📊 Generating chart...")
    chart_buf = generate_chart(result_df, plan)
    output["chart_buf"] = chart_buf
    if verbose:
        print("✅ Chart generated\n" if chart_buf else "⚠️ No chart\n")

    # Explainer
    if verbose:
        print("💡 Explainer Agent generating insights...")
    explanation = call_explainer_llm(
        question=question,
        plan=plan,
        result_df=result_df,
        tone=tone,
        language=language,
    )
    output["explanation"] = explanation

    if verbose:
        print(f"\nAI Insights:\n{explanation}")

    # Memory
    memory.add_turn(
        question=question,
        plan=plan,
        result_summary=result_df.head(5).to_string(index=False),
        explanation=explanation,
    )

    if verbose:
        print(f"🧠 Memory updated — {len(memory.turns)} turn(s) stored")
        print("=" * 60)
        print(f"✅ {label} completed successfully!")
        print("=" * 60)

    return output


# ── Null pipeline ─────────────────────────────────────────────────
def run_null_pipeline(
    df, question, memory, tone, language, verbose, output
) -> dict:
    if verbose:
        print("🔍 Null question detected — bypassing planner...")

    result_df = check_null_values(df)

    null_plan = {
        "operation":     "null_check",
        "target_column": "Null_Count",
        "metric":        "count",
        "need_chart":    True,
        "chart_type":    "barh",
        "group_by":      ["Column"],
        "filters":       [],
    }

    if verbose:
        print(result_df.to_string(index=False))

    # Only chart columns that have nulls
    null_only_df = result_df[result_df["Null_Count"] > 0]
    chart_df = null_only_df if not null_only_df.empty else result_df

    return _finish_pipeline(
        df=df,
        question=question,
        plan=null_plan,
        result_df=result_df,
        memory=memory,
        tone=tone,
        language=language,
        verbose=verbose,
        output=output,
        label="Null pipeline"
    )


# ── Count pipeline ────────────────────────────────────────────────
def run_count_pipeline(
    df, question, memory, tone, language, verbose, output
) -> dict:
    if verbose:
        print("🔢 Count question detected — bypassing planner...")

    # Detect which column to group by from the question
    group_col  = None
    filter_val = None
    filters    = []

    categorical_cols = [
        "Ship Mode", "Segment", "Category",
        "Region", "Sub-Category", "State",
        "City", "Country", "Customer Name"
    ]

    for col in categorical_cols:
        if col in df.columns:
            for val in df[col].dropna().unique():
                if str(val).lower() in question.lower():
                    group_col  = col
                    filter_val = val
                    filters    = [{
                        "column": col,
                        "op":     "==",
                        "value":  val
                    }]
                    break
        if group_col:
            break

    # Build plan
    count_plan = {
        "operation":     "group_by_summary",
        "target_column": "Row ID",
        "metric":        "count",
        "need_chart":    True,
        "chart_type":    "bar",
        "group_by":      [group_col] if group_col else [],
        "filters":       filters,
        "question_hint": question,
    }

    result_df = run_analysis_plan(df, count_plan)

    if verbose:
        print(result_df.to_string(index=False))

    return _finish_pipeline(
        df=df,
        question=question,
        plan=count_plan,
        result_df=result_df,
        memory=memory,
        tone=tone,
        language=language,
        verbose=verbose,
        output=output,
        label="Count pipeline"
    )


# ── Main pipeline ─────────────────────────────────────────────────
def run_pipeline(
    df: pd.DataFrame,
    question: str,
    memory: ConversationMemory,
    tone: str = "technical",
    language: str = "auto",
    verbose: bool = True
) -> dict:

    output = {
        "plan":        None,
        "result_df":   None,
        "chart_buf":   None,
        "explanation": None,
        "schema_text": None,
        "error":       None,
    }

    try:
        # ── Step 1: Preprocess dates ──────────────────────────
        if verbose:
            print("🔄 Step 1/5 — Preprocessing dates...")
        df = preprocess_dates(df)

        # ── Step 2: Build schema ──────────────────────────────
        if verbose:
            print("📋 Step 2/5 — Building schema description...")
        schema_text = get_schema_description(df)
        output["schema_text"] = schema_text

        if verbose:
            print(f"\nSchema:\n{schema_text}\n")
            if not memory.is_empty():
                print(f"🧠 Memory context:\n{memory.summary()}\n")

        # ── Step 3a: Null question check ──────────────────────
        if any(k in question.lower() for k in NULL_KEYWORDS):
            return run_null_pipeline(
                df=df, question=question, memory=memory,
                tone=tone, language=language,
                verbose=verbose, output=output
            )

        # ── Step 3b: Count question check ────────────────────
        if any(k in question.lower() for k in COUNT_KEYWORDS):
            return run_count_pipeline(
                df=df, question=question, memory=memory,
                tone=tone, language=language,
                verbose=verbose, output=output
            )

        # ── Step 4: Planner Agent ─────────────────────────────
        if verbose:
            print("🤖 Step 3/5 — Planner Agent thinking...")
        plan = call_planner_with_memory(schema_text, question, memory)
        plan["question_hint"] = question
        output["plan"] = plan

        if verbose:
            print(f"Plan:\n{json.dumps(plan, indent=2)}\n")

        # ── Validate plan ─────────────────────────────────────
        required_fields = ["operation", "target_column", "metric"]
        missing = [f for f in required_fields if f not in plan]
        if missing:
            raise ValueError(
                f"Planner returned incomplete plan. Missing: {missing}"
            )

        # ── Step 5: Data Worker ───────────────────────────────
        if verbose:
            print("🔧 Step 4/5 — Data Worker executing plan...")
        result_df = run_analysis_plan(df, plan)
        output["result_df"] = result_df

        if verbose:
            print(f"Result ({len(result_df)} rows):")
            print(result_df.to_string(index=False))
            print()

        if result_df.empty:
            raise ValueError(
                "Data Worker returned empty results. "
                "Try a different question or check your filters."
            )

        # ── Step 6 — 8: Chart, Explainer, Memory ─────────────
        return _finish_pipeline(
            df=df,
            question=question,
            plan=plan,
            result_df=result_df,
            memory=memory,
            tone=tone,
            language=language,
            verbose=verbose,
            output=output,
            label="Pipeline"
        )

    except Exception as e:
        output["error"] = str(e)
        if verbose:
            print(f"\n❌ Pipeline error: {e}")

    return output