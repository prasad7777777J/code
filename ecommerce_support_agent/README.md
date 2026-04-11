# 🛒 ShopBot — AI E-commerce Support Agent

> **Ask questions in plain English. Get instant support for your orders, returns, and tracking.**
> No SQL. No tickets. Fully local. Completely free.

![ShopBot](https://img.shields.io/badge/ShopBot-AI%20Support%20Agent-1d9e75?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-7c3aed?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge)
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
- [Test Order IDs](#-test-order-ids)
- [Security](#-security)
- [Future Improvements](#-future-improvements)

---

## 🎯 Overview

**ShopBot** is a fully local, open-source AI-powered customer support agent that handles e-commerce queries using plain English — no SQL, no manual lookups, no API keys needed.

Built with **LangGraph** for multi-step agent logic, **FastAPI** as the backend, **Streamlit** as the chat UI, and **Ollama** for running the LLM completely on your machine.

### The Problem It Solves

```
Customer: "Where is my order?"      → wait for support agent
Customer: "Can I return this?"      → read policy docs manually
Customer: "What's my tracking no?"  → dig through emails
```

**ShopBot eliminates this.** Customers type a question and get an instant, accurate, personalised answer — powered by a local LLM and real order data.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Natural Language Chat** | Ask "where is my order?" and get a real answer |
| 🔀 **Intent Routing** | Automatically classifies and routes to the right handler |
| 📦 **Order Status** | Looks up live order data and responds with delivery info |
| ↩️ **Return Eligibility** | Checks 30-day return window and refund amount |
| 🚚 **Shipment Tracking** | Returns carrier, tracking number, and current location |
| 🏠 **Fully Local** | Runs on your machine — no API keys, no cloud, no cost |
| 🎨 **Beautiful UI** | Streamlit chat UI with intent badges and sidebar tools |
| 🔌 **FastAPI Backend** | Clean REST API with session management |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                        │
│              http://localhost:8501                       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│               Streamlit UI (app.py)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  💬 Chat Tab                                     │   │
│  │  - Message input                                 │   │
│  │  - Intent badge (order/returns/tracking/general) │   │
│  │  - Order ID extracted display                    │   │
│  │  - Sidebar: sample questions, session info       │   │
│  └────────────────────┬─────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP POST /chat
┌───────────────────────▼─────────────────────────────────┐
│               FastAPI Backend (main.py)                  │
│  - POST /chat        → run agent, return reply           │
│  - GET  /history/:id → get session history               │
│  - DELETE /history/:id → clear session                   │
│  - GET  /health      → health check                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              LangGraph Agent (agent.py)                  │
│                                                          │
│  Node 1: classify_intent                                 │
│  ┌─────────────┬──────────────┬───────────────────┐     │
│  │order_status │   returns    │     tracking      │     │
│  └──────┬──────┴──────┬───────┴─────────┬─────────┘     │
│         │             │                 │                │
│  Node 2: extract_order_id (regex → LLM fallback)         │
│         │             │                 │                │
│  Node 3: Specialist handlers                             │
│  ┌──────▼──────┐ ┌────▼───────┐ ┌──────▼──────┐        │
│  │handle_order │ │handle_     │ │handle_      │        │
│  │             │ │returns     │ │tracking     │        │
│  └─────────────┘ └────────────┘ └─────────────┘        │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Ollama (Local LLM)                          │
│              Model: qwen2.5:14b                          │
│              http://localhost:11434                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Mock Order Database (tools.py)              │
│              lookup_order()                              │
│              check_return_eligibility()                  │
│              get_tracking_info()                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **UI** | Streamlit | Chat interface |
| **Backend** | FastAPI + Uvicorn | REST API + session management |
| **Agent** | LangGraph | Multi-node stateful agent graph |
| **LLM** | Ollama + Qwen2.5:14b | Local AI model |
| **Data** | Mock DB (tools.py) | Order/return/tracking data |
| **Language** | Python 3.10+ | Backend logic |

### Why Qwen2.5:14b?

| Model | Instruction Following | RAM Needed |
|---|---|---|
| `qwen2.5:14b` ⭐ | Excellent | 9GB |
| `llama3.1` | Very Good | 8GB |
| `mistral` | Good | 4GB |
| `gemma3` | Good | 5GB |

Qwen2.5:14b was chosen for its superior instruction-following and classification accuracy.

---

## 📁 Project Structure

```
ecommerce_agent/
├── agent.py          # LangGraph graph — state, nodes, routing
├── app.py            # Streamlit chat UI
├── main.py           # FastAPI — endpoints, session store
├── models.py         # Pydantic request/response models
├── tools.py          # Mock DB + tool functions
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

### File Responsibilities

**`tools.py`** — Data layer
- In-memory mock order database with 4 sample orders
- `lookup_order(order_id)` → returns order status and delivery info
- `check_return_eligibility(order_id)` → enforces 30-day return window
- `get_tracking_info(order_id)` → returns carrier, tracking number, location

**`agent.py`** — Brain of the system
- `classify_intent()` → classifies message into order_status / returns / tracking / general
- `extract_order_id()` → regex first, LLM fallback
- `route()` → plain Python routing function, no LLM
- `handle_order/returns/tracking/general()` → specialist nodes that call tools
- `build_graph()` → assembles and compiles the LangGraph StateGraph
- `run_agent()` → public interface called by FastAPI

**`main.py`** — API layer
- FastAPI app with CORS middleware
- In-memory session store (per session_id)
- POST `/chat` → runs agent, stores history, returns reply
- GET/DELETE `/history/:id` → session management

**`app.py`** — User interface
- Streamlit chat UI with message history
- Intent and order ID badges on each response
- Sidebar: sample question buttons, session info, test order IDs
- Live backend health check

---

## 🔄 How It Works

### Chat Flow (3 Steps)

```
User: "Can I return my order ORD-1001?"
          │
          ▼
┌─────────────────────┐
│  Step 1: Intent     │  → "returns"
│  Classification     │
│  (LLM call)         │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Step 2: Extract    │  → "ORD-1001"
│  Order ID           │     (regex match)
│  (regex → LLM)      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Step 3: Specialist │  → check_return_eligibility("ORD-1001")
│  Node               │     eligible: True
│  handle_returns()   │     days_remaining: 22
└─────────┬───────────┘     refund_amount: $89.99
          │
          ▼
"Good news! Your Wireless Headphones is eligible
 for a return. You have 22 days left.
 Refund amount: $89.99."
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-support-agent.git
cd ecommerce-support-agent
```

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Pull the AI model

```bash
ollama pull qwen2.5:14b
```

> 💡 If you have less than 9GB RAM, use `ollama pull mistral` and update `OLLAMA_MODEL` in `agent.py`

### Step 4 — Start Ollama

```bash
ollama serve
```

### Step 5 — Start the FastAPI backend (Terminal 1)

```bash
python -m uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Step 6 — Start the Streamlit frontend (Terminal 2)

```bash
python -m streamlit run app.py
```

Open → `http://localhost:8501` 🎉

---

## 💬 Usage

### Chat Tab

Type any question in the chat input or click the sample question buttons in the sidebar:

```
💬 "Where is my order ORD-1002?"
💬 "Can I return order ORD-1001?"
💬 "Track my shipment ORD-1003"
💬 "What's your return policy?"
💬 "Show me order ORD-1004 status"
```

For each message you'll see:
- 🏷️ Intent badge (order status / returns / tracking / general)
- 🔢 Extracted order ID
- 💬 Personalised AI response with real order data

---

## 💡 Sample Questions

### Order Status
```
Where is my order ORD-1002?
What is the status of ORD-1003?
Has my order ORD-1001 been delivered?
```

### Returns & Refunds
```
Can I return ORD-1001?
I want a refund for order ORD-1004
Is ORD-1002 eligible for return?
```

### Tracking
```
Track my order ORD-1002
What's the tracking number for ORD-1001?
Where is my shipment ORD-1003?
```

### General
```
What is your return policy?
How long does delivery take?
How do I contact support?
```

---

## 🧪 Test Order IDs

| Order ID | Status     | Customer      | Item                | Price   |
|----------|------------|---------------|---------------------|---------|
| ORD-1001 | Delivered  | Alice Johnson | Wireless Headphones | $89.99  |
| ORD-1002 | In transit | Bob Smith     | Running Shoes       | $124.95 |
| ORD-1003 | Processing | Carol White   | Coffee Maker        | $59.99  |
| ORD-1004 | Delivered  | David Lee     | Mechanical Keyboard | $149.00 |

---

## 🔒 Security

ShopBot's tool layer is **read-only by design**:

- ✅ Agent only reads from the mock database — no writes possible
- ✅ No customer data sent to external APIs
- ✅ Ollama runs 100% on your machine
- ✅ No API keys required

---

## 🔮 Future Improvements

- [ ] Connect to a real MySQL / PostgreSQL database
- [ ] Add Redis for persistent cross-session memory
- [ ] Support order modification and cancellation flows
- [ ] Add authentication layer for customer verification
- [ ] Docker container for easy deployment
- [ ] Support multiple languages
- [ ] Voice input for questions

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
- [LangGraph](https://langchain-ai.github.io/langgraph/) — stateful agent framework
- [Streamlit](https://streamlit.io/) — UI framework
- [FastAPI](https://fastapi.tiangolo.com/) — backend framework
- [Qwen2.5](https://huggingface.co/Qwen) — open source LLM by Alibaba 