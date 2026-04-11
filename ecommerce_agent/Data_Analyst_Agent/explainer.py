# explainer.py
import json
import pandas as pd
from config import client, MODEL

TONE_PROMPTS = {
    "executive": """
CRITICAL: Only describe what is in the Results table below.
If results show months → talk about months.
If results show regions → talk about regions.
If results show categories → talk about categories.
NEVER mix topics or mention things not in the results.

You are a C-suite data advisor. Be extremely concise and focus only on
business impact and bottom-line numbers. No technical details.

Structure:
1. BOTTOM LINE (1 sentence) — Name the #1 performer and its EXACT value
   FIRST. Never bury the answer. Example: "The West region led total sales
   at $725,457 — 31.6% of all revenue."
2. TOP 3 INSIGHTS (3 bullet points) — business impact only, specific numbers.
3. ACTION (1 sentence) — one immediate recommendation.

Rules:
- Always name the top performer in the very first sentence
- Always include the exact number in the first sentence
- Never say "based on the data" or "the analysis shows"
- Keep total response under 100 words.
""",

    "technical": """
CRITICAL: Only describe what is in the Results table below.
If results show months → talk about months.
If results show regions → talk about regions.
If results show categories → talk about categories.
NEVER mix topics or mention things not in the results.

You are a senior data scientist presenting findings to a technical team.

Structure:
1. DIRECT ANSWER (1 sentence) — State EXACTLY which item ranked #1
   and its precise value. Example: "The West region achieved the highest
   total sales at $710,219.68, representing 31.4% of total revenue."
2. SUPPORTING INSIGHTS (3 bullet points max) — only include stats that
   DIRECTLY support the answer. Do NOT include information about other
   items unless directly comparing to the #1 performer.
3. NEXT ANALYSIS (1 sentence) — one specific follow-up suggestion.

Rules:
- Maximum 3 bullet points — quality over quantity
- Every bullet must relate directly to the question asked
- Never include stats about bottom performers unless asked
- Keep total response under 150 words.
""",

    "casual": """
CRITICAL: Only describe what is in the Results table below.
If results show months → talk about months.
If results show regions → talk about regions.
If results show categories → talk about categories.
NEVER mix topics or mention things not in the results.

You are a friendly data analyst explaining results to a non-technical team.
Use simple everyday language, analogies, and avoid all jargon.

Structure:
1. QUICK ANSWER (1 sentence) — Lead with who won and the exact number,
   in plain simple language. Example: "The West region sold the most —
   $725K which is about 32% of all sales!"
2. INTERESTING FINDINGS (3-5 bullet points) — fun and easy to understand,
   use analogies where helpful.
3. SUGGESTION (1 sentence) — one simple next step.

Rules:
- First sentence must clearly name the top performer with a number
- Never start with "So," or "Well," without naming the winner
- Use plain English — no technical jargon at all
- Keep total response under 150 words.
"""
}
# ── Language instruction ──────────────────────────────────────────
LANGUAGE_INSTRUCTION = """
IMPORTANT: Detect the language of the user's question and respond 
in that SAME language. If the question is in Spanish, respond in Spanish.
If in French, respond in French. If in Telugu, respond in Telugu. And so on.
"""


def _compute_stats(result_df: pd.DataFrame, target_col: str) -> str:
    """Compute quick stats to help the LLM reason better."""
    if target_col not in result_df.columns:
        return ""

    col_data  = result_df[target_col]
    total     = col_data.sum()
    average   = col_data.mean()
    maximum   = col_data.max()
    minimum   = col_data.min()
    std       = col_data.std()
    top_row   = result_df.iloc[0]
    bottom_row = result_df.iloc[-1]

    # Percentage share of top performer
    top_pct = (maximum / total * 100) if total > 0 else 0

    return f"""
Pre-computed stats (use these directly — do not recalculate):
- Total:              {total:,.2f}
- Average:            {average:,.2f}
- Maximum:            {maximum:,.2f}  ({top_pct:.1f}% of total)
- Minimum:            {minimum:,.2f}
- Std deviation:      {std:,.2f}
- Top performer:      {top_row.to_dict()}
- Bottom performer:   {bottom_row.to_dict()}
- Gap (max - min):    {maximum - minimum:,.2f}
- Number of groups:   {len(result_df)}
""".strip()


def _clean_dataframe(result_df: pd.DataFrame) -> pd.DataFrame:
    """Convert datetime/period columns to string for safe serialization."""
    df = result_df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
        elif hasattr(df[col], 'dt'):
            df[col] = df[col].astype(str)
    return df


def _build_few_shot_examples() -> str:
    """Few-shot examples to guide the LLM toward better responses."""
    return """
EXAMPLE OF A GOOD RESPONSE (executive tone):
---
BOTTOM LINE: Technology drives 62% of total revenue at $2,699.97 — 
nearly double Furniture's $1,520.00.

- Technology: $2,699.97 (62.4% of total revenue)
- Furniture: $1,520.00 (35.2%) — strong second place
- Office Supplies: $39.98 — severely underperforming at under 1%

ACTION: Prioritize Technology inventory and investigate 
why Office Supplies is lagging so far behind.
---
Follow this structure and quality for your response.
"""


def call_explainer_llm(
    question: str,
    plan: dict,
    result_df: pd.DataFrame,
    tone: str = "technical",
    language: str = "auto"
) -> str:
    """
    Generate a plain-English insight summary from the analysis results.

    Args:
        question:   The original user question
        plan:       The JSON analysis plan that was executed
        result_df:  The result DataFrame from the Data Worker
        tone:       One of 'executive', 'technical', 'casual'
        language:   'auto' to detect from question, or e.g. 'Spanish', 'French'

    Returns:
        A formatted insight summary string
    """

    # ── Step 1: Clean DataFrame ───────────────────────────────
    clean_df = _clean_dataframe(result_df)
    result_summary = clean_df.head(20).to_string(index=False)

    # ── Step 2: Compute stats ─────────────────────────────────
    target_col = plan.get("target_column", "")
    stats_text = _compute_stats(result_df, target_col)

    # ── Step 3: Pick tone prompt ──────────────────────────────
    tone = tone.lower()
    if tone not in TONE_PROMPTS:
        tone = "technical"
    tone_instruction = TONE_PROMPTS[tone]

    # ── Step 4: Language instruction ─────────────────────────
    if language == "auto":
        lang_instruction = LANGUAGE_INSTRUCTION
    else:
        lang_instruction = f"IMPORTANT: Always respond in {language}, regardless of the question language."

    # ── Step 5: Few-shot examples ─────────────────────────────
    few_shot = _build_few_shot_examples()

    # ── Step 6: Build system prompt ───────────────────────────
    system_prompt = f"""
{tone_instruction}

{lang_instruction}

{few_shot}

Additional rules:
- Always use specific numbers from the results
- Never say "the data shows" or "based on the analysis"
- Never repeat the question back to the user
- If results are empty or unclear, say so honestly
""".strip()

# ── Step 7: Build user message ────────────────────────────
    result_columns = list(result_df.columns)
    group_by       = plan.get("group_by", [])
    target_col_name = plan.get("target_column", "")

    user_content = f"""
Question asked: {question}

Analysis plan executed:
{json.dumps(plan, indent=2)}

Result columns: {result_columns}
Grouped by: {group_by}
Metric column: {target_col_name}

ACTUAL RESULTS (use ONLY these numbers — nothing else):
{result_summary}

{stats_text}

REMINDER: The results are grouped by {group_by}.
Your response must ONLY discuss {group_by} — not anything else.
""".strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_content},
    ]

    # ── Step 8: Call LLM ──────────────────────────────────────
    resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=600,
            temperature=0.5,  # ← changed from 0.3 to 0.5
        )

    explanation = resp.choices[0].message.content.strip()

    if not explanation:
        explanation = "Unable to generate insights. Please try rephrasing your question."

    return explanation