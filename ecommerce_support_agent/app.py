"""
Streamlit frontend for the E-commerce Support Agent.
Run with: streamlit run app.py
Requires the FastAPI backend running on http://localhost:8000
"""

import streamlit as st
import requests
import uuid

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_URL = "http://localhost:8000"

INTENT_LABELS = {
    "order_status": ("📦", "Order Status",  "#1d9e75"),
    "returns":      ("↩️",  "Return/Refund", "#ba7517"),
    "tracking":     ("🚚", "Tracking",       "#185fa5"),
    "general":      ("💬", "General",        "#534ab7"),
    "":             ("🤔", "Thinking...",    "#888780"),
}

SAMPLE_QUESTIONS = [
    "Where is my order ORD-1002?",
    "Can I return order ORD-1001?",
    "Track my shipment ORD-1003",
    "What's your return policy?",
    "Show me order ORD-1004 status",
]

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="ShopBot — Support",
    page_icon="🛒",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_intent" not in st.session_state:
    st.session_state.last_intent = ""
if "last_order_id" not in st.session_state:
    st.session_state.last_order_id = ""

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://placehold.co/200x60/1d9e75/white?text=ShopBot", width=200)
    st.markdown("### 🛒 E-commerce Support Agent")
    st.caption("Powered by LangGraph + Ollama + FastAPI + Streamlit")

    st.divider()

    # Session info
    st.markdown("**Session**")
    st.code(st.session_state.session_id, language=None)

    # Last detected intent
    if st.session_state.last_intent:
        emoji, label, color = INTENT_LABELS.get(
            st.session_state.last_intent, INTENT_LABELS[""]
        )
        st.markdown("**Last intent detected**")
        st.markdown(
            f'<span style="background:{color}22; color:{color}; '
            f'padding:4px 10px; border-radius:12px; font-size:13px; font-weight:500">'
            f'{emoji} {label}</span>',
            unsafe_allow_html=True,
        )

    # Last order ID
    if st.session_state.last_order_id:
        st.markdown("**Order ID extracted**")
        st.code(st.session_state.last_order_id, language=None)

    st.divider()

    # Sample questions
    st.markdown("**Try these questions:**")
    for q in SAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True, key=f"sample_{q}"):
            st.session_state.pending_message = q
            st.rerun()

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear conversation", use_container_width=True):
        requests.delete(f"{API_URL}/history/{st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.last_intent = ""
        st.session_state.last_order_id = ""
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.rerun()

    st.divider()

    # Test order IDs
    st.markdown("**Test order IDs**")
    st.markdown("""
| ID | Status |
|---|---|
| ORD-1001 | Delivered |
| ORD-1002 | In transit |
| ORD-1003 | Processing |
| ORD-1004 | Delivered (old) |
""")

# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------

st.markdown("## 🛒 Customer Support")
st.caption("Ask me about your orders, returns, or tracking information.")

# Check API health
try:
    health = requests.get(f"{API_URL}/health", timeout=2)
    if health.status_code == 200:
        st.success("Agent online", icon="🟢")
    else:
        st.error("API returned an error — is the backend running?", icon="🔴")
except Exception:
    st.error(
        "Cannot reach backend at http://localhost:8000 — "
        "run `uvicorn main:app --reload` in the backend folder.",
        icon="🔴",
    )

st.divider()

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
        # Show metadata badge on assistant messages
        if msg["role"] == "assistant" and msg.get("intent"):
            emoji, label, color = INTENT_LABELS.get(msg["intent"], INTENT_LABELS[""])
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(
                    f'<span style="background:{color}22; color:{color}; '
                    f'padding:2px 8px; border-radius:8px; font-size:11px">'
                    f'{emoji} {label}</span>',
                    unsafe_allow_html=True,
                )
            if msg.get("order_id"):
                with col2:
                    st.markdown(
                        f'<span style="background:#88878022; color:#888780; '
                        f'padding:2px 8px; border-radius:8px; font-size:11px">'
                        f'🔢 {msg["order_id"]}</span>',
                        unsafe_allow_html=True,
                    )

# Welcome message on empty chat
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(
            "👋 Hi! I'm your ShopBot support assistant.\n\n"
            "I can help you with:\n"
            "- 📦 **Order status** — where is my order?\n"
            "- ↩️ **Returns & refunds** — can I return this?\n"
            "- 🚚 **Tracking** — where is my shipment?\n"
            "- 💬 **General questions** — anything else!\n\n"
            "What can I help you with today?"
        )

# ---------------------------------------------------------------------------
# Handle pending message from sidebar buttons
# ---------------------------------------------------------------------------

if "pending_message" in st.session_state:
    user_input = st.session_state.pop("pending_message")
else:
    user_input = st.chat_input("Type your message here...")

# ---------------------------------------------------------------------------
# Process message
# ---------------------------------------------------------------------------

if user_input:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Call FastAPI
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": user_input,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                reply    = data["reply"]
                intent   = data.get("intent", "")
                order_id = data.get("order_id", "")

                st.markdown(reply)

                # Show intent + order ID badges
                if intent:
                    emoji, label, color = INTENT_LABELS.get(intent, INTENT_LABELS[""])
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        st.markdown(
                            f'<span style="background:{color}22; color:{color}; '
                            f'padding:2px 8px; border-radius:8px; font-size:11px">'
                            f'{emoji} {label}</span>',
                            unsafe_allow_html=True,
                        )
                    if order_id:
                        with col2:
                            st.markdown(
                                f'<span style="background:#88878022; color:#888780; '
                                f'padding:2px 8px; border-radius:8px; font-size:11px">'
                                f'🔢 {order_id}</span>',
                                unsafe_allow_html=True,
                            )

            except requests.exceptions.ConnectionError:
                reply    = "❌ Cannot reach the backend. Please start the FastAPI server."
                intent   = ""
                order_id = ""
                st.error(reply)
            except Exception as e:
                reply    = f"❌ Error: {str(e)}"
                intent   = ""
                order_id = ""
                st.error(reply)

    # Save assistant message with metadata
    st.session_state.messages.append({
        "role":     "assistant",
        "content":  reply,
        "intent":   intent,
        "order_id": order_id,
    })

    # Update sidebar state
    st.session_state.last_intent   = intent
    st.session_state.last_order_id = order_id

    st.rerun()
