# 🧠 QueryMind — AI SQL Dashboard

> **Ask questions in plain English. Get instant insights from your SQL database.**
> No SQL knowledge required. Fully local. Completely free.

![QueryMind Banner](https://img.shields.io/badge/QueryMind-AI%20SQL%20Dashboard-7c3aed?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4=)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-XAMPP-4479a1?style=for-the-badge&logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [Sample Questions](#-sample-questions)
- [Before vs After](#-before-vs-after)
- [Security](#-security)
- [Future Improvements](#-future-improvements)

---

## 🎯 Overview

**QueryMind** is a fully local, open-source AI-powered SQL dashboard that lets anyone — technical or not — query a MySQL database using plain English and get instant visual results.

Inspired by the [article by Vivek Singh Pathania](https://viveksinghpathania.medium.com/build-an-ai-agent-that-turns-sql-databases-into-dashboards-no-queries-needed-ea78571b2475), this project replaces paid LLM APIs (Claude/GPT) with **Ollama running locally**, making it completely free, private, and offline-capable.

### The Problem It Solves

```
Marketing: "Submit a ticket to analytics"
Sales:     "Wait for next month's dashboard"  
CEO:       "Do we have that number yet?"
```

**QueryMind eliminates this bottleneck.** Anyone can type a question and get an answer instantly — no SQL, no tickets, no waiting.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Natural Language Chat** | Ask questions like "who spent the most?" and get accurate SQL-powered answers |
| 📊 **Auto Dashboard** | One-click generates 5 live charts from your database |
| 🧠 **Intent Detection** | Automatically detects if you want a count, details, or both |
| 🔒 **Read-Only Security** | AI can only run SELECT queries — your data is safe |
| 🏠 **Fully Local** | Runs on your machine — no API keys, no cloud, no cost |
| 🎨 **Beautiful UI** | Dark premium theme with custom fonts and animations |
| 📈 **Smart Charts** | Auto-generates bar, pie, line charts based on data type |
| 🔌 **Easy Connection** | Connect to any MySQL database from the sidebar UI |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                        │
│              http://localhost:8501                       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 Streamlit UI (app.py)                    │
│  ┌─────────────────┐    ┌──────────────────────────┐    │
│  │  💬 Chat Tab    │    │    📊 Dashboard Tab       │    │
│  │  - Question     │    │    - KPI Cards            │    │
│  │  - SQL display  │    │    - Bar / Pie / Line     │    │
│  │  - Count badge  │    │    - Auto-generated       │    │
│  │  - Data table   │    │      charts               │    │
│  └────────┬────────┘    └──────────────┬───────────┘    │
└───────────┼─────────────────────────────┼───────────────┘
            │                             │
┌───────────▼─────────────────────────────▼───────────────┐
│                  Agent Layer (agent.py)                  │
│                                                          │
│  Step 1: Intent Detection                                │
│  ┌─────────────┬─────────────┬──────────────────┐       │
│  │ COUNT_ONLY  │ DETAIL_ONLY │ COUNT_AND_DETAIL  │       │
│  └──────┬──────┴──────┬──────┴────────┬─────────┘       │
│         │             │               │                  │
│  Step 2: SQL Generation (separate prompts)               │
│  ┌──────▼──────┐ ┌────▼────────┐                        │
│  │ Count Prompt│ │Detail Prompt│                         │
│  └──────┬──────┘ └────┬────────┘                        │
│         │             │                                  │
│  Step 3: Summary Generation                              │
│  ┌───────────────────────┐                               │
│  │    Summary Prompt     │                               │
│  └───────────┬───────────┘                              │
└──────────────┼──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│              Ollama (Local LLM)                          │
│              Model: qwen2.5:14b                          │
│              http://localhost:11434                      │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│           ReadOnlyMySQL (db_connector.py)                │
│           Security Layer — SELECT only                   │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│           MySQL Database (XAMPP)                         │
│           localhost:3306                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **UI** | Streamlit | Web interface |
| **LLM** | Ollama + Qwen2.5:14b | Local AI model |
| **Agent** | LangChain Core | Prompt chaining |
| **Database** | MySQL (XAMPP) | Data storage |
| **Charts** | Plotly | Data visualization |
| **Security** | Custom ReadOnlyMySQL | SELECT-only enforcement |
| **Language** | Python 3.10+ | Backend logic |

### Why Qwen2.5:14b?

| Model | SQL Accuracy | RAM Needed |
|---|---|---|
| `qwen2.5:14b` ⭐ | Excellent | 9GB |
| `codellama` | Very Good | 8GB |
| `llama3` | Good | 8GB |
| `mistral` | Moderate | 4GB |

Qwen2.5:14b was chosen for its superior understanding of SQL schemas and JOIN logic.

---

## 📁 Project Structure

```
sql-ai-dashboard/
│
├── app.py              # Streamlit UI — frontend, tabs, styling
├── agent.py            # LangChain agent — intent detection, SQL generation
├── db_connector.py     # MySQL connector — read-only security layer
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

### File Responsibilities

**`db_connector.py`** — Security layer
- Connects to MySQL via XAMPP
- Exposes `get_schema()` → returns table/column structure as JSON
- Exposes `run_query()` → validates query starts with SELECT before executing
- Raises `ValueError` if any non-SELECT query is attempted

**`agent.py`** — Brain of the system
- `detect_intent()` → classifies question into COUNT_ONLY / DETAIL_ONLY / COUNT_AND_DETAIL
- `ask_database()` → orchestrates the full pipeline: intent → SQL → query → summary
- `get_dashboard_data()` → runs 5 hardcoded analytical queries for the dashboard
- Uses 4 specialized LangChain prompts (Intent, Count SQL, Detail SQL, Summary)

**`app.py`** — User interface
- Sidebar database connection form
- Chat tab with example question chips
- Dashboard tab with KPI cards + 5 Plotly charts
- Full dark theme with custom CSS

---

## 🔄 How It Works

### Chat Flow (3 Steps)

```
User: "how many orders were placed in 2024?"
          │
          ▼
┌─────────────────────┐
│  Step 1: Intent     │  → COUNT_AND_DETAIL
│  Detection          │     (user wants both the
│  (INTENT_PROMPT)    │      number AND the rows)
└─────────┬───────────┘
          │
    ┌─────┴──────┐
    ▼            ▼
┌───────┐   ┌──────────┐
│ COUNT │   │  DETAIL  │
│ Query │   │  Query   │
└───┬───┘   └────┬─────┘
    │             │
    ▼             ▼
SELECT         SELECT o.id,
COUNT(*) AS      c.name,
total_orders     p.name ...
FROM orders    FROM orders o
WHERE          JOIN customers c
YEAR(...) = 2024  JOIN products p
                WHERE YEAR(...)=2024
    │             │
    ▼             ▼
  Result:10    Result: 10 rows
    │             │
    └──────┬───────┘
           ▼
    ┌─────────────┐
    │  Summary    │  → "In 2024, there were 10 orders
    │  Generation │     totaling $3,869.83. The most
    └─────────────┘     expensive was Alice Johnson's
                        Laptop Pro 15 at $1,299.99."
```

### Dashboard Flow

```
Click "Generate Dashboard"
          │
          ▼
    5 hardcoded SQL queries run in parallel:
    1. Sales by Category   → Bar Chart
    2. Orders by Status    → Donut Chart
    3. Monthly Revenue     → Area Line Chart
    4. Top Products        → Horizontal Bar Chart
    5. Customers by Country → Bar Chart
          │
          ▼
    4 KPI metric cards computed:
    - Total Revenue
    - Total Orders
    - Top Category
    - Delivered Orders
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [XAMPP](https://www.apachefriends.org/) installed and MySQL running
- [Ollama](https://ollama.com/) installed

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/sql-ai-dashboard.git
cd sql-ai-dashboard
```

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Pull the AI model

```bash
ollama pull qwen2.5:14b
```

> 💡 If you have less than 9GB RAM, use `ollama pull mistral` instead and update `model` in `agent.py`

### Step 4 — Start XAMPP MySQL

Open XAMPP Control Panel → Start **MySQL** (and Apache)

### Step 5 — Create sample database

Open `http://localhost/phpmyadmin` → SQL tab → paste and run:

```sql
CREATE DATABASE IF NOT EXISTS ecommerce_demo;
USE ecommerce_demo;

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100), email VARCHAR(100),
    city VARCHAR(50), country VARCHAR(50), joined_date DATE
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100), category VARCHAR(50),
    price DECIMAL(10,2), stock INT
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT, product_id INT,
    quantity INT, total_amount DECIMAL(10,2),
    order_date DATE, status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO customers (name, email, city, country, joined_date) VALUES
('Alice Johnson','alice@email.com','New York','USA','2023-01-15'),
('Bob Smith','bob@email.com','London','UK','2023-02-20'),
('Carol White','carol@email.com','Toronto','Canada','2023-03-10'),
('David Brown','david@email.com','Sydney','Australia','2023-04-05'),
('Eva Martinez','eva@email.com','Chicago','USA','2023-05-18'),
('Frank Lee','frank@email.com','Mumbai','India','2023-06-22'),
('Grace Kim','grace@email.com','Seoul','South Korea','2023-07-30'),
('Henry Wilson','henry@email.com','Berlin','Germany','2023-08-14');

INSERT INTO products (name, category, price, stock) VALUES
('Laptop Pro 15','Electronics',1299.99,50),
('Wireless Headphones','Electronics',199.99,120),
('Running Shoes','Sports',89.99,200),
('Coffee Maker','Kitchen',59.99,80),
('Python Programming Book','Books',39.99,150),
('Yoga Mat','Sports',29.99,300),
('Smart Watch','Electronics',349.99,75),
('Blender Pro','Kitchen',79.99,60);

INSERT INTO orders (customer_id, product_id, quantity, total_amount, order_date, status) VALUES
(1,1,1,1299.99,'2024-01-10','delivered'),
(2,2,2,399.98,'2024-01-15','delivered'),
(3,3,1,89.99,'2024-02-01','delivered'),
(4,7,1,349.99,'2024-02-14','delivered'),
(5,4,2,119.98,'2024-03-05','shipped'),
(6,5,3,119.97,'2024-03-20','delivered'),
(7,6,2,59.98,'2024-04-01','processing'),
(8,8,1,79.99,'2024-04-10','delivered'),
(1,2,1,199.99,'2024-04-15','shipped'),
(3,7,1,349.99,'2024-05-01','delivered');
```

### Step 6 — Run the app

```bash
python -m streamlit run app.py
```

Open → `http://localhost:8501` 🎉

---

## 💬 Usage

### Connecting to Database

1. Fill in the sidebar connection form (default XAMPP: host=`localhost`, user=`root`, password=`""`)
2. Click **⚡ Connect to Database**
3. You'll see 🟢 Connected status

### Chat Tab

Type any question in the chat input or click the example chips:

```
💬 "how many orders were placed in 2024?"
💬 "which customer spent the most money?"
💬 "top products by revenue"
💬 "customers from USA"
💬 "monthly revenue trend"
```

For each question you'll see:
- ✅ Generated SQL (transparent)
- 🔢 Count badge (when applicable)
- 💡 AI-generated insight summary
- 📊 Data table with results
- 📈 Auto chart (for 2-column results)

### Dashboard Tab

Click **🚀 Generate Dashboard** to auto-generate:
- 4 KPI metric cards
- Sales by Category bar chart
- Orders by Status donut chart
- Monthly Revenue area chart
- Top Products horizontal bar chart
- Customers by Country bar chart

---

## 💡 Sample Questions

### Simple
```
show all customers
how many products do we have
show all orders
```

### Revenue & Sales
```
what is the total revenue
which category has the highest sales
what is the average order value
```

### Top / Best
```
top products
best selling product
which customer spent the most
top 5 customers by spending
```

### Orders
```
how many orders are delivered
how many orders in 2024
orders by status
show all shipped orders
```

### Customers
```
customers from USA
which country has the most customers
list all customers and their cities
```

### Date Based
```
orders in January 2024
monthly revenue
which month had the highest sales
```

### Advanced (JOINs)
```
which customer bought the most products
show customer names with their order totals
what is the total revenue per country
show me electronics products and their stock
```

---

## 🔄 Before vs After

### Single Query Approach (Old)

```python
# ONE prompt tried to do everything
sql = llm.invoke("write SQL for: " + question)
df  = db.run_query(sql)
# ❌ "how many orders" → COUNT mixed with rows → wrong result
```

### Intent-Based Dual Query Approach (New)

```python
# Step 1: Understand what the user wants
intent = detect_intent(question)
# → COUNT_AND_DETAIL

# Step 2: Generate separate focused queries
count_sql  = count_prompt  | llm  # → SELECT COUNT(*) ...
detail_sql = detail_prompt | llm  # → SELECT o.id, c.name ...

# Step 3: Summarize both
summary = summary_prompt | llm
# ✅ Accurate count + all rows returned correctly
```

| | Before | After |
|---|---|---|
| Prompts | 1 generic | 4 specialized |
| Queries per question | 1 (confused) | 1 or 2 (focused) |
| "how many" questions | ❌ Wrong | ✅ Correct |
| Date assumptions | Added current year | Only when asked |
| Error handling | Basic | `safe_run_query` never crashes |
| Result display | Plain table | Count badge + table + chart |

---

## 🔒 Security

QueryMind is **read-only by design**:

```python
def run_query(self, query: str):
    # Hard block on any non-SELECT query
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed!")
    # Safe to execute
    cursor.execute(query)
```

- ✅ AI can only READ data
- ✅ No INSERT, UPDATE, DELETE, DROP ever possible
- ✅ Database credentials stored locally only
- ✅ No data sent to external APIs
- ✅ Ollama runs 100% on your machine

---

## 🔮 Future Improvements

- [ ] Support PostgreSQL and SQLite
- [ ] Export chat history as PDF report
- [ ] Upload CSV/Excel files as temporary tables
- [ ] Voice input for questions
- [ ] Multi-database support (switch between DBs)
- [ ] Save and share dashboards
- [ ] User authentication layer
- [ ] Docker container for easy deployment

---

## 👨‍💻 Author

Built by **Kommineni** — Data Scientist & Gen AI Instructor

- 🎓 MS Data Analytics — University of Illinois Springfield
- 💼 Data Science & Gen AI Instructor at J-Monk DevOps
- 🏅 NVIDIA Certified: Generative AI LLMs

---

## 📄 License

MIT License — feel free to use, modify, and share.

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.com/) — local LLM runtime
- [Streamlit](https://streamlit.io/) — UI framework
- [LangChain](https://langchain.com/) — LLM orchestration
- [Qwen2.5](https://huggingface.co/Qwen) — open source LLM by Alibaba