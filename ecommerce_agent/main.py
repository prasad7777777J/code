"""
FastAPI backend for the e-commerce support agent.

Endpoints:
  POST /chat          — send a message, get a reply
  GET  /history/{id}  — get conversation history for a session
  DELETE /history/{id}— clear a session
  GET  /health        — health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict

from models import ChatRequest, ChatResponse
from agent import run_agent

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="E-commerce Support Agent API",
    description="LangGraph-powered customer support agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: { session_id: [{"role": ..., "content": ...}] }
sessions: dict[str, list] = defaultdict(list)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "ecommerce-support-agent"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or "default"
    history = sessions[session_id]

    try:
        result = run_agent(
            user_message=request.message,
            history=history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Persist this turn to session history
    sessions[session_id].append({"role": "user",      "content": request.message})
    sessions[session_id].append({"role": "assistant",  "content": result["reply"]})

    return ChatResponse(
        reply=result["reply"],
        intent=result.get("intent"),
        order_id=result.get("order_id"),
        resolved=result.get("resolved", False),
        session_id=session_id,
    )


@app.get("/history/{session_id}")
def get_history(session_id: str):
    return {
        "session_id": session_id,
        "messages": sessions.get(session_id, []),
    }


@app.delete("/history/{session_id}")
def clear_history(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"session_id": session_id, "cleared": True}
