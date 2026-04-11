"""
E-commerce Customer Support Agent built with LangGraph.

Graph flow:
  START → classify_intent → extract_order_id → [route] → specialist → END

Specialist nodes: handle_order | handle_returns | handle_tracking | handle_general
"""

import re
import os
from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from tools import lookup_order, check_return_eligibility, get_tracking_info

# ---------------------------------------------------------------------------
# LLM — Ollama (must be running: `ollama serve`)
# ---------------------------------------------------------------------------

# Change to:
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")

llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0,
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # full conversation history
    intent: str                                # classified intent
    order_id: str                              # extracted order ID
    order_data: dict                           # result from tool call
    customer_name: str                         # for personalised replies
    resolved: bool                             # True → route to END


# ---------------------------------------------------------------------------
# Node 1 — classify intent
# ---------------------------------------------------------------------------

def classify_intent(state: AgentState) -> dict:
    last_message = state["messages"][-1].content

    prompt = f"""You are an e-commerce support classifier.

Classify the customer message into exactly one of these intents:
- order_status   → asking about order progress, status, or delivery date
- returns        → wants to return, refund, or exchange a product
- tracking       → asking for tracking number or current shipment location
- general        → anything else (greetings, complaints, other questions)

Customer message: "{last_message}"

Respond with ONLY the intent label, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()

    valid = {"order_status", "returns", "tracking", "general"}
    if intent not in valid:
        intent = "general"

    return {"intent": intent}


# ---------------------------------------------------------------------------
# Node 2 — extract order ID
# ---------------------------------------------------------------------------

def extract_order_id(state: AgentState) -> dict:
    last_message = state["messages"][-1].content

    # Fast path: regex
    match = re.search(r'\bORD-\d+\b', last_message, re.IGNORECASE)
    if match:
        return {"order_id": match.group(0).upper()}

    # Slow path: LLM extraction
    prompt = f"""Extract the order ID from this message.
Return ONLY the order ID in format ORD-XXXX, or 'NOT_FOUND' if there isn't one.

Message: "{last_message}" """

    response = llm.invoke([HumanMessage(content=prompt)])
    extracted = response.content.strip().upper()

    return {"order_id": extracted if extracted != "NOT_FOUND" else ""}


# ---------------------------------------------------------------------------
# Route function
# ---------------------------------------------------------------------------

def route(state: AgentState) -> str:
    intent_map = {
        "order_status": "handle_order",
        "returns":       "handle_returns",
        "tracking":      "handle_tracking",
        "general":       "handle_general",
    }
    return intent_map.get(state["intent"], "handle_general")


# ---------------------------------------------------------------------------
# Specialist nodes
# ---------------------------------------------------------------------------

def handle_order(state: AgentState) -> dict:
    order_id = state.get("order_id", "")

    if not order_id:
        return {
            "messages": [AIMessage(content="I'd be happy to check your order status! "
                                           "Could you share your order ID? (format: ORD-XXXX)")],
            "resolved": False,
        }

    data = lookup_order(order_id)

    if not data["found"]:
        reply = f"I couldn't find an order with ID **{order_id}**. Please double-check and try again."
    else:
        status_map = {
            "processing": "currently being prepared at our warehouse 📦",
            "in_transit": "on its way to you 🚚",
            "delivered":  "delivered ✅",
        }
        friendly = status_map.get(data["status"], data["status"])
        reply = (
            f"Hi **{data['customer_name']}**! Your order for "
            f"**{data['item']}** (#{order_id}) is {friendly}.\n\n"
            f"📅 Expected delivery: **{data['delivery_date']}**"
        )

    return {
        "messages": [AIMessage(content=reply)],
        "order_data": data,
        "customer_name": data.get("customer_name", ""),
        "resolved": True,
    }


def handle_returns(state: AgentState) -> dict:
    order_id = state.get("order_id", "")

    if not order_id:
        return {
            "messages": [AIMessage(content="I can help with a return! "
                                           "What's your order ID? (format: ORD-XXXX)")],
            "resolved": False,
        }

    data = check_return_eligibility(order_id)

    if not data["found"]:
        reply = f"I couldn't find order **{order_id}**. Please check the ID and try again."
    elif not data["eligible"]:
        reply = f"Unfortunately, this order isn't eligible for a return. ❌\n\n**Reason:** {data['reason']}"
    else:
        reply = (
            f"Good news! Your **{data['item']}** is eligible for a return. ✅\n\n"
            f"⏳ You have **{data['days_remaining']} days** left in the return window.\n"
            f"💰 Refund amount: **${data['refund_amount']:.2f}**\n\n"
            f"Reply **'confirm return'** to proceed."
        )

    return {
        "messages": [AIMessage(content=reply)],
        "order_data": data,
        "resolved": True,
    }


def handle_tracking(state: AgentState) -> dict:
    order_id = state.get("order_id", "")

    if not order_id:
        return {
            "messages": [AIMessage(content="Sure! Which order would you like to track? (format: ORD-XXXX)")],
            "resolved": False,
        }

    data = get_tracking_info(order_id)

    if not data["found"]:
        reply = f"I couldn't find a shipment for order **{order_id}**."
    else:
        status_emoji = {"delivered": "✅", "in_transit": "🚚", "processing": "📦"}
        emoji = status_emoji.get(data["status"], "📦")
        reply = (
            f"{emoji} **Tracking info for {data['item']}** (#{order_id})\n\n"
            f"🚛 Carrier: **{data['carrier']}**\n"
            f"🔢 Tracking #: **{data['tracking_number']}**\n"
            f"📍 Current location: **{data['current_location']}**\n"
            f"📅 Estimated delivery: **{data['estimated_delivery']}**"
        )

    return {
        "messages": [AIMessage(content=reply)],
        "order_data": data,
        "resolved": True,
    }


def handle_general(state: AgentState) -> dict:
    system = SystemMessage(content="""You are a friendly e-commerce customer support agent.
Help with orders, returns, tracking, and general questions.
Keep responses concise, warm, and professional.
If the customer needs help with a specific order, ask for their order ID.""")

    response = llm.invoke([system] + state["messages"])

    return {
        "messages": [AIMessage(content=response.content)],
        "resolved": True,
    }


# ---------------------------------------------------------------------------
# Build and compile the graph
# ---------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent",  classify_intent)
    graph.add_node("extract_order_id", extract_order_id)
    graph.add_node("handle_order",     handle_order)
    graph.add_node("handle_returns",   handle_returns)
    graph.add_node("handle_tracking",  handle_tracking)
    graph.add_node("handle_general",   handle_general)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "extract_order_id")
    graph.add_conditional_edges("extract_order_id", route)

    graph.add_edge("handle_order",    END)
    graph.add_edge("handle_returns",  END)
    graph.add_edge("handle_tracking", END)
    graph.add_edge("handle_general",  END)

    return graph.compile()


app = build_graph()


# ---------------------------------------------------------------------------
# Public interface used by FastAPI
# ---------------------------------------------------------------------------

def run_agent(user_message: str, history: list[dict]) -> dict:
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))

    result = app.invoke({
        "messages":      messages,
        "intent":        "",
        "order_id":      "",
        "order_data":    {},
        "customer_name": "",
        "resolved":      False,
    })

    return {
        "reply":    result["messages"][-1].content,
        "intent":   result.get("intent", ""),
        "order_id": result.get("order_id", ""),
        "resolved": result.get("resolved", False),
    }