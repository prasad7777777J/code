# planner.py
import json
import re
from config import client, MODEL


def call_planner_llm(schema_text: str, question: str) -> dict:
    """Send schema + question to LLM and get back a structured JSON analysis plan."""

    system_prompt = """
    You are a data analysis planner. Convert user questions into JSON plans.

    JSON Structure (REQUIRED - output ONLY this JSON, nothing else):
    {
    "operation": "group_by_summary",
    "group_by": ["column_name"],
    "filters": [],
    "target_column": "numeric_column_only",
    "metric": "sum",
    "need_chart": true,
    "chart_type": "bar"
    }

    STRICT RULES — follow these exactly:
    1. target_column MUST be a numeric column (int64, float64) — NEVER a date, string, or object column
    2. NEVER use these as target_column: Order Date, Ship Date, or ANY date/time column
    3. NEVER use Customer Name, Product Name, Category, Region, or ANY text column as target_column
    4. For target_column always prefer: Sales, Profit, Quantity, Discount, or any float64/int64 column
    5. group_by columns should be categorical (object/str) or date helper columns like Order Date_year
    6. For questions about null/missing values, use metric=count and target_column=the most relevant NUMERIC column
    7. For questions about counts or how many, use metric=count on a numeric column
    8. For questions about trends over time, use group_by=[Order Date_year_month] or [Order Date_year]
    9. chart_type must be one of: bar, barh, line, area, pie, donut, scatter, histogram, box, waterfall, funnel, cumulative
    10. Output ONLY raw JSON — no markdown, no explanation, no extra text
    11. For questions about null, missing, NaN, or empty values — still return valid JSON 
    with operation=group_by_summary, metric=count, target_column=Sales (or any numeric column).
    The pipeline will handle null detection automatically.
    COLUMN TYPE GUIDE:
    - numeric columns (OK for target_column): any column with dtype float64 or int64
    - date columns (NEVER use as target_column): any column with date, time, day in name
    - text columns (NEVER use as target_column): any column with dtype object or str
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Dataset:\n{schema_text}\n\nQuestion:\n{question}"
        },
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=512,
        temperature=0,
    )

    content = resp.choices[0].message.content.strip()

    def extract_json(text: str) -> dict:
        # Try direct parse
        try:
            return json.loads(text)
        except:
            pass
        # Try extracting from code block
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        # Try finding first { ... }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        raise ValueError(f"Could not extract JSON from:\n{text}")

    return extract_json(content)