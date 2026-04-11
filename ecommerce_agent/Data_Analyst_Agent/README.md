# 📊 AI Data Analyst Agent

A production-ready, multi-agent AI system that turns any CSV file into an interactive analytics assistant. Ask questions in plain English and get charts, data tables, and AI-generated business insights instantly.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gen-ai-ik8uyaxlkwy72cemexsszs.streamlit.app)

> 🚀 **Live Demo:** https://gen-ai-ik8uyaxlkwy72cemexsszs.streamlit.app
---

## 🎯 What it does

Upload any CSV file, type a question like *"Which category had the highest total sales?"* and the agent:

1. **Plans** — converts your question into a structured JSON analysis plan
2. **Executes** — runs the plan using pandas (no LLM touching your data directly)
3. **Visualizes** — generates the right chart automatically
4. **Explains** — translates numbers into plain-English business insights

---

## 🏗️ Architecture

```
User Question
      ↓
Planner Agent (LLM) → JSON Plan
      ↓
Data Worker (pandas) → Result Table
      ↓
Chart Generator (matplotlib) → PNG Chart
      ↓
Explainer Agent (LLM) → Business Insights
```

The key design principle is **LLM decides, Python executes** — the model never touches your raw data directly, which keeps analysis reproducible, debuggable, and auditable.

---

## 🚀 Features

| Feature | Details |
|---|---|
| **Smart CSV loader** | Auto-detects encoding (UTF-8, Latin-1, UTF-16), separator (`,` `;` `\t` `|`), handles wide files (100+ cols) and large files (500k+ rows) |
| **Date preprocessing** | Auto-detects date columns, adds `_year`, `_month`, `_quarter`, `_dayofweek`, `_year_month` helper columns |
| **CSV validator** | Pre-analysis checks — shows issues, warnings, and tips before analysis starts |
| **Planner Agent** | Converts natural language questions to structured JSON plans with group_by, filters, metrics, and chart types |
| **Data Worker** | 20+ pandas operations — sum, mean, count, max, min, median, std, var, nunique, first, last |
| **Filter engine** | 12 filter operators — `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `startswith`, `isin`, `between`, `isnull`, `notnull` |
| **20 chart types** | bar, barh, line, area, pie, donut, scatter, bubble, histogram, box, violin, heatmap, waterfall, funnel, cumulative, step, multiline, stacked_bar, grouped_bar, kde |
| **3 response tones** | Executive (concise), Technical (detailed stats), Casual (plain English) |
| **Multi-language** | Auto-detects question language, responds in same language |
| **Conversation memory** | Remembers last 5 turns — supports follow-up questions like "now show me just 2023" |
| **Null detection** | Special pipeline that bypasses the planner and checks all columns for missing values |
| **Count questions** | Special pipeline for "how many orders..." questions |
| **43 tests** | 32 integration tests + 11 DeepEval accuracy tests |

---

## 📁 Project structure

```
Data_Analyst_Agent/
│
├── .env                    ← API keys (never commit this)
├── requirements.txt        ← all dependencies
│
├── config.py               ← LLM client + model setup
├── preprocessing.py        ← smart CSV loader + date preprocessor + validator
├── planner.py              ← Planner Agent (LLM → JSON plan)
├── data_worker.py          ← pandas execution engine
├── chart_generator.py      ← 20 chart types
├── explainer.py            ← Explainer Agent (3 tones + multi-language)
├── pipeline.py             ← full pipeline + conversation memory
├── app.py                  ← Streamlit UI
│
└── tests/
    ├── __init__.py
    ├── conftest.py          ← shared fixtures + rate limit delay
    ├── train.csv            ← test dataset
    ├── test_pipeline.py     ← 32 integration tests
    ├── deepeval_config.py   ← Ollama local evaluator setup
    └── test_deepeval.py     ← 11 DeepEval accuracy tests
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/data-analyst-agent.git
cd data-analyst-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your Groq API key

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up for free → Create API key
3. Copy the key (starts with `gsk_...`)

### 4. Create your `.env` file

```
GROQ_API_KEY=gsk_yourKeyHere
```

### 5. Run the app

```bash
python -m streamlit run app.py
```

Open your browser at [http://localhost:8501](http://localhost:8501)

---

## 🧪 Running tests

### Integration tests

```bash
python -m pytest tests/test_pipeline.py -v --html=tests/report.html
```

### Accuracy tests (DeepEval)

Requires [Ollama](https://ollama.com/download) installed locally:

```bash
# Pull the evaluation model
ollama pull qwen2.5:14b

# Run accuracy tests
export TEST_MODE=true
python -m pytest tests/test_deepeval.py -v --html=tests/deepeval_report.html
```

### Test results

| Suite | Tests | Status |
|---|---|---|
| Integration (`test_pipeline.py`) | 32 | ✅ All passing |
| Accuracy (`test_deepeval.py`) | 11 | ✅ All passing |
| **Total** | **43** | **✅ 43/43** |

---

## 💬 Example questions

### Basic analysis
```
Which category had the highest total sales?
What is the average sales by region?
Show top 5 products by revenue
What is the minimum sales value?
```

### Time-based
```
What were the total sales per year?
Show monthly sales trend in 2017
Which month had the highest sales?
Show cumulative sales over time
```

### Filtered
```
What are the total sales in the West region?
Show sales by sub-category for Furniture only
What is the total sales in California?
Show sales for Standard Class shipping only
```

### Chart type control
```
Show sales by category as a pie chart
Show profit by region as a donut chart
Show monthly trend as a line chart
Show sales distribution as a histogram
```

### Data quality
```
How many null values are there?
Which columns have missing data?
Are there any NaN values?
```

### Follow-up questions (memory)
```
Which category had the highest total sales?
→ Now show me just 2017
→ Break that down by sub-category
→ Show it as a pie chart
```

### Multi-language
```
¿Qué categoría tuvo las mayores ventas?          (Spanish)
Quelle région a les ventes les plus élevées?      (French)
ఏ కేటగిరీలో అత్యధిక విక్రయాలు జరిగాయి?           (Telugu)
सबसे ज्यादा बिक्री किस क्षेत్రలో हुई?             (Hindi)
```

---

## 🛠️ Tech stack

| Component | Technology |
|---|---|
| LLM | Llama 3.3 70B via Groq API |
| UI | Streamlit |
| Data processing | pandas, numpy |
| Visualization | matplotlib, seaborn |
| CSV handling | chardet (encoding detection) |
| Testing | pytest, pytest-html |
| Accuracy evaluation | DeepEval + Ollama (qwen2.5:14b) |
| Local inference | Ollama (NVIDIA GPU support) |

---

## 📊 Supported CSV types

| CSV type | Supported |
|---|---|
| UTF-8 encoding | ✅ |
| Latin-1 / cp1252 encoding | ✅ Auto-detected |
| UTF-16 encoding | ✅ Auto-detected |
| Semicolon separated | ✅ Auto-detected |
| Tab separated | ✅ Auto-detected |
| Pipe separated | ✅ Auto-detected |
| Excel exports (unnamed columns) | ✅ Auto-cleaned |
| Wide files (100+ columns) | ✅ Trimmed to 60 |
| Large files (500k+ rows) | ✅ Sampled to 100k |
| Currency strings ($1,234) | ✅ Auto-converted to numeric |
| Multiple date formats | ✅ Tries 7 formats |

---

## 🔑 Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key for LLM inference |
| `TEST_MODE` | ⚙️ Optional | Set to `true` to use smaller model during testing |

---

## 📈 DeepEval accuracy metrics

The agent was evaluated using DeepEval with a local Ollama judge (qwen2.5:14b on NVIDIA RTX 5070 Ti):

| Metric | Score | Threshold | Result |
|---|---|---|---|
| Answer Relevancy — category | 0.71 | 0.50 | ✅ |
| Answer Relevancy — region | 0.50 | 0.45 | ✅ |
| Answer Relevancy — monthly trend | 0.67 | 0.65 | ✅ |
| Faithfulness — category | 0.33 | 0.30 | ✅ |
| Faithfulness — segment | 0.75 | 0.70 | ✅ |
| Faithfulness — null check | 0.67 | 0.60 | ✅ |
| Contains Specific Numbers | 0.90 | 0.70 | ✅ |
| Has Actionable Recommendation | 0.85 | 0.60 | ✅ |
| Business Language | 0.80 | 0.50 | ✅ |
| Appropriate Length | 0.75 | 0.30 | ✅ |
| Plan Quality (JSON) | 0.90 | 0.70 | ✅ |

---

## 🗺️ Roadmap

- [ ] SQL database connector (replace CSV loader)
- [ ] Multi-file support (join two CSVs)
- [ ] PDF export of analysis reports
- [ ] Email reports via SMTP
- [ ] Scheduled analysis (run every day at 9am)
- [ ] Deploy to Streamlit Cloud

---

## 🐛 Known limitations

- Only one numeric target column can be aggregated per question
- Very complex multi-step questions may need to be broken into simpler ones
- Chart types requiring two numeric columns (e.g. scatter with X and Y) need both columns specified explicitly
- Groq free tier has a 100k token/day limit — run tests with `TEST_MODE=true` to use the smaller model

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — ultra-fast LLM inference
- [DeepEval](https://github.com/confident-ai/deepeval) — LLM evaluation framework
- [Ollama](https://ollama.com) — local model inference
- [Streamlit](https://streamlit.io) — rapid UI development
- [DataCamp](https://www.datacamp.com/tutorial/deepseek-v3-2-speciale-tutorial) — original project inspiration
