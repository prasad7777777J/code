# app.py
import io
import pandas as pd
import streamlit as st
from pipeline import run_pipeline, ConversationMemory

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .sub-header {
        font-size: 1rem;
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #1a3a2a;
        border-left: 4px solid #2ecc71;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        color: #e0ffe0 !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .error-box {
        background-color: #3a1a1a;
        border-left: 4px solid #e74c3c;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        color: #ffe0e0 !important;
    }
    .memory-box {
        background-color: #f0f4ff;
        border-left: 4px solid #3498db;
        padding: 0.8rem 1.2rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────
st.markdown("<div class='main-header'>📊 AI Data Analyst Agent</div>",
            unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload any CSV and ask questions in plain English</div>",
            unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_turns=5)

if "history" not in st.session_state:
    st.session_state.history = []

if "df" not in st.session_state:
    st.session_state.df = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    # Tone selector
    tone = st.selectbox(
        "Response tone",
        options=["technical", "executive", "casual"],
        index=0,
        help="technical = detailed stats | executive = short & sharp | casual = simple language"
    )

    # Language selector
    language = st.selectbox(
        "Response language",
        options=["auto", "English", "Spanish", "French",
                 "German", "Telugu", "Hindi", "Japanese"],
        index=0,
        help="Auto detects language from your question"
    )

    st.markdown("---")

    # Chart type override
    st.markdown("## 📊 Chart settings")
    chart_override = st.selectbox(
        "Force chart type (optional)",
        options=[
            "auto (let AI decide)",
            "bar", "barh", "line", "area",
            "pie", "donut", "scatter", "bubble",
            "histogram", "box", "violin",
            "heatmap", "waterfall", "funnel",
            "cumulative", "step", "multiline",
            "stacked_bar", "grouped_bar", "kde"
        ],
        index=0
    )

    st.markdown("---")

    # Memory status
    st.markdown("## 🧠 Conversation memory")
    if st.session_state.memory.is_empty():
        st.info("No memory yet — ask your first question!")
    else:
        st.success(st.session_state.memory.summary())
        if st.button("🗑️ Clear memory"):
            st.session_state.memory.clear()
            st.success("Memory cleared!")
            st.rerun()

    st.markdown("---")
    st.markdown("## 📁 Session info")
    if st.session_state.file_name:
        st.info(f"File: **{st.session_state.file_name}**")
        if st.session_state.df is not None:
            st.info(f"Rows: **{len(st.session_state.df):,}**")
            st.info(f"Columns: **{len(st.session_state.df.columns)}**")

# ── File upload ───────────────────────────────────────────────────
st.markdown("### 📂 Upload your CSV file")
uploaded_file = st.file_uploader(
    "Drag and drop or click to browse",
    type=["csv"],
    help="Upload any CSV file to get started"
)

if uploaded_file is not None:
    if uploaded_file.name != st.session_state.file_name:
        st.session_state.memory.clear()
        st.session_state.history = []
        st.session_state.file_name = uploaded_file.name

        try:
            from preprocessing import load_csv, validate_csv
            df, load_info = load_csv(uploaded_file)
            st.session_state.df = df

            # ── Show loading info ─────────────────────────
            st.success(
                f"✅ Loaded **{uploaded_file.name}** — "
                f"{load_info['rows']:,} rows × "
                f"{load_info['columns']} columns | "
                f"Encoding: `{load_info['encoding']}` | "
                f"Separator: `{repr(load_info['separator'])}`"
            )

            # ── Show load warnings ────────────────────────
            for w in load_info["warnings"]:
                st.warning(f"⚠️ {w}")

            # ── Run validator ─────────────────────────────
            validation = validate_csv(df)

            for issue in validation["issues"]:
                st.error(f"❌ {issue}")

            for warn in validation["warnings"]:
                st.warning(f"⚠️ {warn}")

            for tip in validation["tips"]:
                st.info(f"💡 {tip}")

            if not validation["valid"]:
                st.stop()

        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            st.stop()
    # ── Safety check before using df ─────────────────────────
    df = st.session_state.df
    if df is None:
        st.warning("⚠️ No data loaded yet. Please upload a CSV file.")
        st.stop()
    # ── Data preview ──────────────────────────────────────────
    with st.expander("🔍 Preview data", expanded=False):
        col1, col2, col3 = st.columns(3)
        col1.metric("Total rows",    f"{len(df):,}")
        col2.metric("Total columns", len(df.columns))
        col3.metric("Memory usage",
                    f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        st.dataframe(df.head(100), use_container_width=True, height=300)

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            st.markdown("**Numeric column summary:**")
            st.dataframe(df[numeric_cols].describe(),
                         use_container_width=True)

    st.markdown("---")

    # ── Question input ────────────────────────────────────────
    st.markdown("### 💬 Ask a question about your data")

    # Show example questions
    with st.expander("💡 Example questions", expanded=False):
        examples = [
            "Which category had the highest total sales?",
            "What were the monthly sales trends in 2023?",
            "Which product had the highest average sales?",
            "Show me the top 5 products by revenue",
            "What is the total sales by region?",
            "Compare sales between 2022 and 2023",
            "Which month had the lowest sales?",
            "Show the sales distribution by category as a pie chart",
        ]
        for ex in examples:
            if st.button(ex, key=ex):
                st.session_state["question_input"] = ex

    col1, col2 = st.columns([5, 1])
    with col1:
        question = st.text_input(
            "Your question",
            key="question_input",
            placeholder="e.g. Which category had the highest total sales?",
            label_visibility="collapsed"
        )
    with col2:
        analyze = st.button("🔍 Analyze", type="primary",
                            use_container_width=True)

    # ── Run pipeline ──────────────────────────────────────────
    if analyze and question.strip():
        with st.spinner("🤖 Agents working on it..."):

            # Apply chart type override if selected
            def run_with_override(df, question, memory, tone, language):
                result = run_pipeline(
                    df=df,
                    question=question,
                    memory=memory,
                    tone=tone,
                    language=language,
                    verbose=False
                )
                # Only override chart if everything succeeded
                if (
                    chart_override != "auto (let AI decide)"
                    and result["plan"] is not None
                    and result["result_df"] is not None  # ← key fix
                    and not result["result_df"].empty    # ← key fix
                    and result["error"] is None          # ← key fix
                ):
                    result["plan"]["chart_type"] = chart_override
                    from chart_generator import generate_chart
                    result["chart_buf"] = generate_chart(
                        result["result_df"], result["plan"]
                    )
                return result

            result = run_with_override(
                df=df,
                question=question,
                memory=st.session_state.memory,
                tone=tone,
                language=language
            )

        # ── Error handling ────────────────────────────────────
        if result["error"]:
            st.markdown(
                f"<div class='error-box'>❌ {result['error']}</div>",
                unsafe_allow_html=True
            )
        else:
            # ── Save to history ───────────────────────────────
            st.session_state.history.append({
                "question":    question,
                "plan":        result["plan"],
                "result_df":   result["result_df"],
                "chart_buf":   result["chart_buf"],
                "explanation": result["explanation"],
            })

            # ── Results section ───────────────────────────────
            st.markdown("---")
            st.markdown("## 📊 Results")

            # Chart + metrics side by side
            if result["chart_buf"] is not None:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.image(result["chart_buf"],
                             use_container_width=True)
                with col2:
                    st.markdown("### Key metrics")
                    target_col = result["plan"].get("target_column")
                    res_df     = result["result_df"]
                    if target_col and target_col in res_df.columns:
                        st.metric("Total",
                                  f"{res_df[target_col].sum():,.2f}")
                        st.metric("Average",
                                  f"{res_df[target_col].mean():,.2f}")
                        st.metric("Max",
                                  f"{res_df[target_col].max():,.2f}")
                        st.metric("Min",
                                  f"{res_df[target_col].min():,.2f}")
                        st.metric("Rows returned",
                                  f"{len(res_df):,}")
            else:
                st.info("No chart generated for this query.")

            # ── Analysis plan expander ────────────────────────
            with st.expander("🗂️ Analysis plan (JSON)", expanded=False):
                st.json(result["plan"])

            # ── Results table ─────────────────────────────────
            with st.expander("📋 Results table", expanded=True):
                st.dataframe(result["result_df"],
                             use_container_width=True,
                             height=350)
                csv_bytes = result["result_df"].to_csv(index=False).encode()
                st.download_button(
                    label="⬇️ Download results as CSV",
                    data=csv_bytes,
                    file_name="analysis_results.csv",
                    mime="text/csv"
                )

            # ── AI insights ───────────────────────────────────
            st.markdown("---")
            st.markdown("## 💡 AI Insights")
            st.markdown(
                f"<div class='insight-box'>{result['explanation']}</div>",
                unsafe_allow_html=True
            )

    # ── Conversation history ──────────────────────────────────
    if st.session_state.history:
        st.markdown("---")
        st.markdown("## 🕘 Conversation history")
        for i, turn in enumerate(
                reversed(st.session_state.history), 1):
            with st.expander(
                    f"[{len(st.session_state.history) - i + 1}] {turn['question']}",
                    expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if turn["chart_buf"] is not None:
                        turn["chart_buf"].seek(0)
                        st.image(turn["chart_buf"],
                                 use_container_width=True)
                with col2:
                    st.json(turn["plan"])
                st.markdown(
                    f"<div class='insight-box'>{turn['explanation']}</div>",
                    unsafe_allow_html=True
                )

else:
    # ── Empty state ───────────────────────────────────────────
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📂 **Step 1**\nUpload any CSV file above")
    with col2:
        st.info("💬 **Step 2**\nType a question in plain English")
    with col3:
        st.info("📊 **Step 3**\nGet charts + AI insights instantly")