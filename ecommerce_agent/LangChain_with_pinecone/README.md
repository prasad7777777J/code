# 📄 RAG Pipeline — LangChain + Pinecone + Open-Source LLM

A **Retrieval-Augmented Generation (RAG)** system that lets you query private PDF documents using natural language — built entirely with free, open-source tools. No OpenAI. No paid APIs beyond Pinecone's free tier.

---

## 💡 What It Does

Point it at a folder of PDF documents, ask a question in plain English, and get a precise answer drawn directly from those documents — with source citations showing exactly which file and page the answer came from.

**Built for:** Internal knowledge bases, HR policy Q&A, legal document search, research paper querying — any scenario where you need to ask questions over private documents without sending data to OpenAI.

**Example:**
```
Q: What is covered under the group medical insurance plan?

A: The group medical insurance plan covers hospitalization expenses,
   pre and post hospitalization costs, day care procedures...

Sources:
  - GMC benefit manual (2022-2023).pdf, page 4
```

---

## 🧱 How It Works

```
PDF Documents  →  Split into chunks  →  HuggingFace Embeddings  →  Pinecone Vector DB
                                                                           │
                                                               User Question (at query time)
                                                                           │
                                                               Retrieve top 3 relevant chunks
                                                                           │
                                                               Groq LLaMA 3.1 generates answer
```

| Component | Tool |
|---|---|
| Embeddings | HuggingFace `all-MiniLM-L6-v2` — free, runs locally |
| Vector Store | Pinecone Serverless — free tier |
| LLM | Groq `llama-3.1-8b-instant` — free API |
| Framework | LangChain LCEL |

---

## 🔒 Privacy First

- Documents never leave your machine (only their vector embeddings are stored in Pinecone)
- API keys managed via `.env` file — never hardcoded
- Private documents excluded from this repository via `.gitignore`

---

## 👤 Author

**Kommineni Sai Prasad**  
Data Scientist | Gen AI Engineer  
[LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/your-username)
