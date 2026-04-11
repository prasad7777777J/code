from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from db_connector import ReadOnlyMySQL
import pandas as pd
import re
from datetime import datetime

llm    = OllamaLLM(model="qwen2.5:14b", temperature=0)
parser = StrOutputParser()

# ─────────────────────────────────────────
# PROMPT 1 — Detect question intent
# ─────────────────────────────────────────
INTENT_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""Classify this database question into one of these intents:
Question: "{question}"

Intents:
- COUNT_ONLY       → user wants just a number (e.g. "how many orders", "count of customers")
- DETAIL_ONLY      → user wants rows/list (e.g. "show me", "list all", "top products")
- COUNT_AND_DETAIL → user wants both a count AND the actual rows (e.g. "how many orders were placed in 2024")

Output ONLY one of: COUNT_ONLY, DETAIL_ONLY, COUNT_AND_DETAIL
No explanation. No punctuation. Just the intent label.
"""
)

# ─────────────────────────────────────────
# PROMPT 2 — Generate COUNT query
# ─────────────────────────────────────────
COUNT_SQL_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "current_date"],
    template="""You are an expert MySQL query writer.
Today's date is {current_date}.

Database schema:
{schema}

Write a MySQL SELECT query that returns ONLY the count/aggregate for:
"{question}"

Rules:
- Output ONLY raw SQL, nothing else
- No markdown, no backticks, no comments, no explanations
- Must start with SELECT
- Use COUNT(*) AS total or SUM() AS total with a clear alias
- NEVER filter by date/year UNLESS the user explicitly mentions a time period
- If user mentions a year (e.g. 2024), filter by that year
- If user mentions a month name, use MONTH() and YEAR()
- Keep it simple — just return the single aggregate number
"""
)

# ─────────────────────────────────────────
# PROMPT 3 — Generate DETAIL query
# ─────────────────────────────────────────
DETAIL_SQL_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "current_date"],
    template="""You are an expert MySQL query writer.
Today's date is {current_date}.

Database schema:
{schema}

Write a MySQL SELECT query that returns the actual rows/details for:
"{question}"

Rules:
- Output ONLY raw SQL, nothing else
- No markdown, no backticks, no comments, no explanations
- Must start with SELECT
- ALWAYS JOIN tables to show human-readable names, never raw IDs
- ALWAYS use meaningful column aliases
- NEVER use COUNT() or GROUP BY unless the question is specifically about grouping/ranking
- NEVER filter by date/year UNLESS the user explicitly mentions a time period
- If user mentions a specific year (e.g. 2024), use WHERE YEAR(column) = that_year
- If user mentions "top N", use ORDER BY + LIMIT N
- If user says "top" with no number, LIMIT 10
- If no time period mentioned, return ALL matching rows
- Limit results to 50 rows max
"""
)

# ─────────────────────────────────────────
# PROMPT 4 — Human summary
# ─────────────────────────────────────────
SUMMARY_PROMPT = PromptTemplate(
    input_variables=["question", "count_data", "detail_data"],
    template="""A business user asked: "{question}"

Count result: {count_data}
Detail results (first 10 rows): {detail_data}

Write a clear, friendly 2-3 sentence summary.
- Use actual numbers and names from the data
- Be specific (mention names, amounts, dates if available)
- No SQL jargon, no bullet points
- Sound like a helpful analyst explaining to a manager
"""
)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def clean_sql(raw: str) -> str:
    raw = re.sub(r"```sql|```", "", raw)
    raw = re.sub(
        r"(?i)^(here is|here's|the query is|sure|certainly|below is)[^\n]*\n",
        "", raw
    )
    raw = raw.strip().rstrip(";")
    lines = [l for l in raw.strip().splitlines() if l.strip()]
    for i, line in enumerate(lines):
        if line.strip().upper().startswith("SELECT"):
            return "\n".join(lines[i:]).strip()
    return raw.strip()


def safe_run_query(db: ReadOnlyMySQL, query: str) -> pd.DataFrame:
    try:
        results = db.run_query(query)
        return pd.DataFrame(results)
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})


def detect_intent(question: str) -> str:
    chain  = INTENT_PROMPT | llm | parser
    result = chain.invoke({"question": question}).strip().upper()
    if "COUNT_AND_DETAIL" in result:
        return "COUNT_AND_DETAIL"
    elif "COUNT_ONLY" in result:
        return "COUNT_ONLY"
    else:
        return "DETAIL_ONLY"


# ─────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────
def ask_database(user_question: str, db: ReadOnlyMySQL):
    schema       = db.get_schema()
    current_date = datetime.now().strftime("%Y-%m-%d")
    intent       = detect_intent(user_question)

    count_sql  = ""
    detail_sql = ""
    count_df   = pd.DataFrame()
    detail_df  = pd.DataFrame()

    # ── COUNT query ──
    if intent in ("COUNT_ONLY", "COUNT_AND_DETAIL"):
        raw       = (COUNT_SQL_PROMPT | llm | parser).invoke({
            "schema": schema, "question": user_question, "current_date": current_date
        })
        count_sql = clean_sql(raw)
        count_df  = safe_run_query(db, count_sql)

    # ── DETAIL query ──
    if intent in ("DETAIL_ONLY", "COUNT_AND_DETAIL"):
        raw        = (DETAIL_SQL_PROMPT | llm | parser).invoke({
            "schema": schema, "question": user_question, "current_date": current_date
        })
        detail_sql = clean_sql(raw)
        detail_df  = safe_run_query(db, detail_sql)

    # ── Summary ──
    count_str  = count_df.head(5).to_string()   if not count_df.empty  else "No count data"
    detail_str = detail_df.head(10).to_string() if not detail_df.empty else "No detail data"

    summary = ""
    if not count_df.empty or not detail_df.empty:
        summary = (SUMMARY_PROMPT | llm | parser).invoke({
            "question":    user_question,
            "count_data":  count_str,
            "detail_data": detail_str,
        })
    else:
        summary = "No results found. Try rephrasing your question or check if the data exists."

    # ── Build SQL display ──
    sql_display = ""
    if count_sql:
        sql_display += f"-- Count Query\n{count_sql}"
    if detail_sql:
        sql_display += f"\n\n-- Detail Query\n{detail_sql}" if sql_display else detail_sql

    return sql_display, count_df, detail_df, summary


# ─────────────────────────────────────────
# DASHBOARD DATA
# ─────────────────────────────────────────
def get_dashboard_data(db: ReadOnlyMySQL):
    queries = {
        "sales_by_category": """
            SELECT p.category AS category,
                   ROUND(SUM(o.total_amount), 2) AS total_sales
            FROM orders o JOIN products p ON o.product_id = p.id
            GROUP BY p.category ORDER BY total_sales DESC
        """,
        "orders_by_status": """
            SELECT status, COUNT(*) AS total_orders
            FROM orders GROUP BY status
        """,
        "monthly_revenue": """
            SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
                   ROUND(SUM(total_amount), 2) AS revenue
            FROM orders GROUP BY month ORDER BY month
        """,
        "top_products": """
            SELECT p.name AS product_name,
                   SUM(o.quantity) AS units_sold,
                   ROUND(SUM(o.total_amount), 2) AS revenue
            FROM orders o JOIN products p ON o.product_id = p.id
            GROUP BY p.name ORDER BY revenue DESC LIMIT 5
        """,
        "customers_by_country": """
            SELECT country, COUNT(*) AS total_customers
            FROM customers GROUP BY country ORDER BY total_customers DESC
        """
    }
    data = {}
    for key, query in queries.items():
        data[key] = safe_run_query(db, query)
    return data