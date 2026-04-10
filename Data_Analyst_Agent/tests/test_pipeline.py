# tests/test_pipeline.py
import pytest
import pandas as pd
from pipeline import run_pipeline, ConversationMemory


# ── Helper ────────────────────────────────────────────────────────
def assert_valid_output(result, question):
    """Check all required output keys are present and valid."""
    assert result["error"] is None, \
        f"Pipeline error for '{question}': {result['error']}"
    assert result["plan"] is not None, \
        f"Plan is None for '{question}'"
    assert result["result_df"] is not None, \
        f"result_df is None for '{question}'"
    assert isinstance(result["result_df"], pd.DataFrame), \
        f"result_df is not a DataFrame for '{question}'"
    assert not result["result_df"].empty, \
        f"result_df is empty for '{question}'"
    assert result["explanation"] is not None, \
        f"Explanation is None for '{question}'"
    assert len(result["explanation"]) > 10, \
        f"Explanation too short for '{question}'"


# ═══════════════════════════════════════════════════════════════════
# GROUP 1 — Basic aggregations
# ═══════════════════════════════════════════════════════════════════
class TestBasicAggregations:

    def test_highest_sales_by_category(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "highest sales by category")
        assert "Category" in result["result_df"].columns
        assert "Sales" in result["result_df"].columns

    def test_average_sales_by_region(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What is the average sales by region?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "average sales by region")
        assert result["plan"]["metric"] == "mean"

    def test_total_sales_by_segment(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What is the total sales by segment?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "total sales by segment")
        assert "Segment" in result["result_df"].columns

    def test_max_sales_value(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What is the maximum sales value?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "max sales value")

    def test_min_sales_value(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What is the minimum sales value?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "min sales value")

    def test_top5_products_by_sales(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Show top 5 products by total sales?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "top 5 products")

    def test_sales_by_subcategory(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What is the total sales by sub-category?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "sales by sub-category")
        assert "Sub-Category" in result["result_df"].columns


# ═══════════════════════════════════════════════════════════════════
# GROUP 2 — Time based
# ═══════════════════════════════════════════════════════════════════
class TestTimeBased:

    def test_sales_per_year(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What were the total sales per year?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "sales per year")

    def test_monthly_sales_trend(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Show monthly sales trend in 2017",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "monthly sales trend 2017")

    def test_highest_sales_year(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Which year had the highest sales?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "highest sales year")


# ═══════════════════════════════════════════════════════════════════
# GROUP 3 — Filter based
# ═══════════════════════════════════════════════════════════════════
class TestFilters:

    def test_filter_by_region(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What are the total sales in the West region?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "filter west region")

    def test_filter_by_category(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Show sales by sub-category for Furniture only",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "filter furniture")

    def test_filter_by_segment(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Show total sales for Corporate segment only",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "filter corporate segment")

    def test_filter_by_state(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "What is the total sales in California?",
            fresh_memory, verbose=False
        )
        assert_valid_output(result, "filter california")


# ═══════════════════════════════════════════════════════════════════
# GROUP 4 — Null detection
# ═══════════════════════════════════════════════════════════════════
class TestNullDetection:

    def test_null_values_check(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "How many null values are there?",
            fresh_memory, verbose=False
        )
        assert result["error"] is None
        assert result["result_df"] is not None
        assert "Null_Count" in result["result_df"].columns
        assert "Column" in result["result_df"].columns

    def test_missing_data_check(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Which columns have missing data?",
            fresh_memory, verbose=False
        )
        assert result["error"] is None
        assert "Null_Count" in result["result_df"].columns

    def test_nan_check(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "Are there any NaN values?",
            fresh_memory, verbose=False
        )
        assert result["error"] is None
        assert "Null_Count" in result["result_df"].columns


# ═══════════════════════════════════════════════════════════════════
# GROUP 5 — Count questions
# ═══════════════════════════════════════════════════════════════════
class TestCountQuestions:

    def test_count_first_class(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df,
            "How many orders were shipped via First Class?",
            fresh_memory, verbose=False
        )
        assert result["error"] is None
        assert result["result_df"] is not None
        assert not result["result_df"].empty

    def test_count_by_region(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "How many orders are in each region?",
            fresh_memory, verbose=False
        )
        assert result["error"] is None
        assert result["result_df"] is not None

    def test_count_by_segment(self, real_df, fresh_memory):
        result = run_pipeline(
            real_df, "How many orders per segment?",
            fresh_memory, verbose=False
        )
        assert result["error"] is None
        assert result["result_df"] is not None


# ═══════════════════════════════════════════════════════════════════
# GROUP 6 — Conversation memory
# ═══════════════════════════════════════════════════════════════════
class TestConversationMemory:

    def test_memory_stores_turns(self, real_df, fresh_memory):
        """Memory should store each turn correctly."""
        run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        assert not fresh_memory.is_empty()
        assert len(fresh_memory.turns) == 1

    def test_memory_follow_up(self, real_df, fresh_memory):
        """Follow-up question should work using memory context."""
        run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        result2 = run_pipeline(
            real_df, "Now show me just 2017",
            fresh_memory, verbose=False
        )
        assert result2["error"] is None
        assert len(fresh_memory.turns) == 2

    def test_memory_three_turns(self, real_df, fresh_memory):
        """Three sequential follow-ups should all work."""
        questions = [
            "Which category had the highest total sales?",
            "Now show me just 2017",
            "Break that down by sub-category",
        ]
        for q in questions:
            result = run_pipeline(
                real_df, q, fresh_memory, verbose=False
            )
            assert result["error"] is None
        assert len(fresh_memory.turns) == 3

    def test_memory_clears(self, real_df, fresh_memory):
        """Memory should be empty after clear()."""
        run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        fresh_memory.clear()
        assert fresh_memory.is_empty()

    def test_memory_max_turns(self, real_df):
        """Memory should not exceed max_turns."""
        memory = ConversationMemory(max_turns=3)
        questions = [
            "Which category had the highest total sales?",
            "What is the average sales by region?",
            "Show top 5 products by sales",
            "What is the total sales by segment?",
            "Show monthly sales trend in 2017",
        ]
        for q in questions:
            run_pipeline(real_df, q, memory, verbose=False)
        assert len(memory.turns) == 3  # max_turns=3


# ═══════════════════════════════════════════════════════════════════
# GROUP 7 — Plan validation
# ═══════════════════════════════════════════════════════════════════
class TestPlanValidation:

    def test_plan_has_required_fields(self, real_df, fresh_memory):
        """Plan must always have operation, target_column, metric."""
        result = run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        plan = result["plan"]
        assert "operation"     in plan
        assert "target_column" in plan
        assert "metric"        in plan

    def test_plan_target_is_numeric(self, real_df, fresh_memory):
        """target_column must always be numeric."""
        result = run_pipeline(
            real_df, "Which region had the highest total sales?",
            fresh_memory, verbose=False
        )
        target = result["plan"]["target_column"]
        assert pd.api.types.is_numeric_dtype(
            real_df[target]
        ), f"target_column '{target}' is not numeric"

    def test_chart_type_is_valid(self, real_df, fresh_memory):
        """chart_type must be one of the supported types."""
        valid_types = [
            "bar", "barh", "line", "area", "pie", "donut",
            "scatter", "bubble", "histogram", "box", "violin",
            "heatmap", "step", "waterfall", "funnel",
            "cumulative", "multiline", "stacked_bar",
            "grouped_bar", "kde"
        ]
        result = run_pipeline(
            real_df, "Show sales by category as a pie chart",
            fresh_memory, verbose=False
        )
        chart_type = result["plan"].get("chart_type", "bar")
        assert chart_type in valid_types, \
            f"Invalid chart_type: {chart_type}"


# ═══════════════════════════════════════════════════════════════════
# GROUP 8 — Output validation
# ═══════════════════════════════════════════════════════════════════
class TestOutputValidation:

    def test_chart_buffer_is_bytes(self, real_df, fresh_memory):
        """Chart buffer should be a BytesIO object."""
        import io
        result = run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        if result["chart_buf"] is not None:
            assert isinstance(result["chart_buf"], io.BytesIO)

    def test_explanation_is_string(self, real_df, fresh_memory):
        """Explanation should be a non-empty string."""
        result = run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 20

    def test_schema_text_is_string(self, real_df, fresh_memory):
        """Schema text should be a non-empty string."""
        result = run_pipeline(
            real_df, "Which category had the highest total sales?",
            fresh_memory, verbose=False
        )
        assert isinstance(result["schema_text"], str)
        assert "Columns:" in result["schema_text"]

    def test_no_error_on_valid_question(self, real_df, fresh_memory):
        """Valid questions should never return an error."""
        questions = [
            "Which category had the highest total sales?",
            "What is the average sales by region?",
            "Show top 5 products by total sales",
            "How many null values are there?",
            "How many orders were shipped via First Class?",
        ]
        for q in questions:
            result = run_pipeline(
                real_df, q,
                ConversationMemory(), verbose=False
            )
            assert result["error"] is None, \
                f"Unexpected error for '{q}': {result['error']}"