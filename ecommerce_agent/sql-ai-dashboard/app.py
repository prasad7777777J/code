import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db_connector import ReadOnlyMySQL
from agent import ask_database, get_dashboard_data

st.set_page_config(
    page_title="QueryMind — AI SQL Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0a0f; color: #e8e8f0; }
.stApp {
    background: radial-gradient(ellipse at 20% 0%, #1a1040 0%, #0a0a0f 50%),
                radial-gradient(ellipse at 80% 100%, #0d2040 0%, transparent 50%);
    background-color: #0a0a0f;
}
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0f0f1a 0%,#0a0a12 100%); border-right:1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] .stTextInput input {
    background:rgba(255,255,255,0.04)!important; border:1px solid rgba(255,255,255,0.1)!important;
    border-radius:10px!important; color:#e8e8f0!important; font-family:'DM Mono',monospace!important;
    font-size:13px!important; padding:10px 14px!important;
}
.brand { padding:24px 0 32px 0; text-align:center; }
.brand-icon { font-size:42px; display:block; margin-bottom:8px; }
.brand-name {
    font-family:'Syne',sans-serif; font-size:22px; font-weight:800;
    background:linear-gradient(135deg,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-0.5px;
}
.brand-sub { font-size:11px; color:rgba(255,255,255,0.3); font-family:'DM Mono',monospace; letter-spacing:1px; text-transform:uppercase; }
.section-label { font-family:'DM Mono',monospace; font-size:10px; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.3); margin-bottom:12px; margin-top:24px; }
.stButton > button {
    background:linear-gradient(135deg,#7c3aed,#3b82f6)!important; color:white!important;
    border:none!important; border-radius:12px!important; font-family:'Syne',sans-serif!important;
    font-weight:600!important; font-size:14px!important; padding:12px 24px!important;
    width:100%!important; transition:all 0.2s ease!important;
}
.stButton > button:hover { transform:translateY(-1px)!important; box-shadow:0 8px 24px rgba(124,58,237,0.4)!important; }
.status-connected { background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:10px 14px; font-family:'DM Mono',monospace; font-size:12px; color:#10b981; text-align:center; }
.status-disconnected { background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2); border-radius:10px; padding:10px 14px; font-family:'DM Mono',monospace; font-size:12px; color:#f87171; text-align:center; }
.page-title { font-family:'Syne',sans-serif; font-size:48px; font-weight:800; background:linear-gradient(135deg,#ffffff 0%,#a78bfa 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1.1; letter-spacing:-2px; margin-bottom:8px; }
.page-subtitle { font-size:15px; color:rgba(255,255,255,0.4); font-weight:300; }
.stTabs [data-baseweb="tab-list"] { background:rgba(255,255,255,0.03); border-radius:14px; padding:4px; gap:4px; border:1px solid rgba(255,255,255,0.06); width:fit-content; }
.stTabs [data-baseweb="tab"] { border-radius:10px!important; font-family:'Syne',sans-serif!important; font-weight:600!important; font-size:14px!important; color:rgba(255,255,255,0.4)!important; padding:8px 20px!important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,rgba(124,58,237,0.3),rgba(59,130,246,0.3))!important; color:white!important; border:1px solid rgba(124,58,237,0.4)!important; }
[data-testid="stChatMessage"] { background:rgba(255,255,255,0.03)!important; border:1px solid rgba(255,255,255,0.06)!important; border-radius:16px!important; padding:16px 20px!important; margin-bottom:12px!important; }
.metric-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:20px 24px; margin-bottom:16px; }
.metric-value { font-family:'Syne',sans-serif; font-size:32px; font-weight:800; background:linear-gradient(135deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.metric-label { font-size:12px; color:rgba(255,255,255,0.4); font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:1px; margin-top:4px; }
.count-badge { background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(59,130,246,0.15)); border:1px solid rgba(124,58,237,0.3); border-radius:16px; padding:24px; margin-bottom:16px; text-align:center; }
.count-number { font-family:'Syne',sans-serif; font-size:64px; font-weight:800; background:linear-gradient(135deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1; }
.count-label { font-size:13px; color:rgba(255,255,255,0.4); font-family:'DM Mono',monospace; margin-top:8px; text-transform:uppercase; letter-spacing:1px; }
.insight-card { background:rgba(255,255,255,0.03); border-left:3px solid #7c3aed; border-radius:0 12px 12px 0; padding:16px 20px; margin:12px 0; }
.chart-card { background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.07); border-radius:20px; padding:8px; margin-bottom:20px; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:0!important; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <span class="brand-icon">🧠</span>
        <div class="brand-name">QueryMind</div>
        <div class="brand-sub">AI · SQL · Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Database Connection</div>', unsafe_allow_html=True)
    db_host     = st.text_input("Host",     value="localhost")
    db_user     = st.text_input("User",     value="root")
    db_password = st.text_input("Password", value="", type="password")
    db_name     = st.text_input("Database", value="ecommerce_demo")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ Connect to Database", type="primary"):
        try:
            db = ReadOnlyMySQL(db_host, db_user, db_password, db_name)
            db.get_schema()
            st.session_state["db"]      = db
            st.session_state["db_name"] = db_name
            st.success("✅ Connected successfully!")
        except Exception as e:
            st.error(f"❌ {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    if "db" in st.session_state:
        st.markdown(f'<div class="status-connected">🟢 &nbsp; Connected to <strong>{st.session_state.get("db_name","")}</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-disconnected">🔴 &nbsp; Not connected</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:rgba(255,255,255,0.2);text-align:center;line-height:1.8;">Qwen2.5:14b · Ollama · XAMPP<br>Read-only · Secure · Local</div>', unsafe_allow_html=True)

# ── Not connected landing ──
if "db" not in st.session_state:
    st.markdown('<div style="padding:40px 0 32px 0;"><div class="page-title">QueryMind</div><div class="page-subtitle">Connect your database from the sidebar to get started</div></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, icon, title, desc in [
        (col1,"💬","Natural Language Chat","Ask in plain English, get instant SQL-powered answers"),
        (col2,"📊","Auto Dashboards","One click generates beautiful charts from your data"),
        (col3,"🔒","Secure by Design","Read-only — AI can never modify your data"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;margin-bottom:12px;">{icon}</div><div style="font-family:\'Syne\',sans-serif;font-size:16px;font-weight:700;color:white;margin-bottom:6px;">{title}</div><div style="font-size:13px;color:rgba(255,255,255,0.4);">{desc}</div></div>', unsafe_allow_html=True)
    st.stop()

# ── Header ──
st.markdown('<div style="padding:40px 0 32px 0;"><div class="page-title">QueryMind</div><div class="page-subtitle">Ask anything. Get instant insights from your database.</div></div>', unsafe_allow_html=True)

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#e8e8f0", size=12),
    title_font=dict(family="Syne", size=16, color="white"),
    colorway=["#7c3aed","#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)"),
    margin=dict(t=50, b=40, l=40, r=20),
)

tab1, tab2 = st.tabs(["💬  Chat with Database", "📊  Dashboard"])

# ══ CHAT TAB ══
with tab1:
    st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)
    examples = [
        "🏆 who spent the most",        "📦 how many orders in 2024",
        "📈 monthly revenue",            "🌍 customers from USA",
        "🛍️ top products",              "📋 show all delivered orders",
        "💰 total revenue",              "⚡ best selling category",
    ]
    cols = st.columns(4)
    for i, ex in enumerate(examples):
        with cols[i % 4]:
            if st.button(ex, key=f"chip_{i}", use_container_width=True):
                st.session_state["prefill"] = ex.split(" ", 1)[1]

    st.markdown("---")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prefill    = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Ask anything about your data...") or prefill

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    sql_display, count_df, detail_df, summary = ask_database(
                        user_input, st.session_state["db"]
                    )

                    # SQL
                    st.markdown("**📝 Generated SQL**")
                    st.code(sql_display, language="sql")

                    # Count badge
                    if not count_df.empty and "error" not in count_df.columns:
                        first_val = count_df.iloc[0, 0]
                        first_col = count_df.columns[0].replace("_", " ").title()
                        st.markdown(f'<div class="count-badge"><div class="count-number">{first_val}</div><div class="count-label">{first_col}</div></div>', unsafe_allow_html=True)

                    # Insight
                    st.markdown(f'<div class="insight-card"><div style="font-size:11px;font-family:\'DM Mono\',monospace;color:rgba(255,255,255,0.3);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">💡 Insight</div><div style="font-size:14px;line-height:1.7;color:rgba(255,255,255,0.85);">{summary}</div></div>', unsafe_allow_html=True)

                    # Detail table
                    if not detail_df.empty and "error" not in detail_df.columns:
                        st.markdown("**📊 Details**")
                        st.dataframe(detail_df, use_container_width=True, height=min(400, 55 + len(detail_df) * 35))

                        if len(detail_df.columns) == 2:
                            num_cols = detail_df.select_dtypes(include="number").columns.tolist()
                            cat_cols = detail_df.select_dtypes(exclude="number").columns.tolist()
                            if num_cols and cat_cols:
                                fig = px.bar(detail_df, x=cat_cols[0], y=num_cols[0])
                                fig.update_layout(**CHART_THEME)
                                fig.update_traces(marker_color="#7c3aed", marker_line_width=0)
                                st.plotly_chart(fig, use_container_width=True)

                    elif not count_df.empty and "error" not in count_df.columns and len(count_df.columns) > 1:
                        st.dataframe(count_df, use_container_width=True)

                    st.session_state.messages.append({"role": "assistant", "content": summary or "Done!"})

                except Exception as e:
                    st.error(f"⚠️ {e}")

# ══ DASHBOARD TAB ══
with tab2:
    st.markdown('<div class="section-label">Auto-Generated Analytics</div>', unsafe_allow_html=True)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        gen_btn = st.button("🚀 Generate Dashboard", type="primary", use_container_width=True)
    with col_info:
        st.markdown('<div style="padding-top:10px;font-size:13px;color:rgba(255,255,255,0.4);">Analyzes your database and builds 5 live charts automatically</div>', unsafe_allow_html=True)

    if gen_btn:
        with st.spinner("Analyzing your database..."):
            try:
                data = get_dashboard_data(st.session_state["db"])
                st.session_state["dashboard_data"] = data
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "dashboard_data" in st.session_state:
        data = st.session_state["dashboard_data"]
        st.markdown("<br>", unsafe_allow_html=True)

        # KPI cards
        if not data["sales_by_category"].empty and not data["orders_by_status"].empty:
            total_rev = data["sales_by_category"]["total_sales"].sum()
            total_ord = data["orders_by_status"]["total_orders"].sum()
            top_cat   = data["sales_by_category"].iloc[0]["category"]
            delivered = 0
            d_row = data["orders_by_status"][data["orders_by_status"]["status"] == "delivered"]
            if not d_row.empty:
                delivered = d_row["total_orders"].values[0]

            k1, k2, k3, k4 = st.columns(4)
            for col, val, label, icon in [
                (k1, f"${total_rev:,.2f}", "Total Revenue",    "💰"),
                (k2, f"{int(total_ord)}",  "Total Orders",     "📦"),
                (k3, top_cat,              "Top Category",     "🏆"),
                (k4, f"{int(delivered)}",  "Delivered Orders", "✅"),
            ]:
                with col:
                    st.markdown(f'<div class="metric-card" style="text-align:center;"><div style="font-size:24px;margin-bottom:8px;">{icon}</div><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if not data["sales_by_category"].empty:
                fig = px.bar(data["sales_by_category"], x="category", y="total_sales",
                             title="Sales by Category", color="total_sales",
                             color_continuous_scale=["#3b82f6","#7c3aed"])
                fig.update_layout(**CHART_THEME, showlegend=False)
                fig.update_coloraxes(showscale=False)
                fig.update_traces(marker_line_width=0)
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            if not data["orders_by_status"].empty:
                fig = go.Figure(data=[go.Pie(
                    labels=data["orders_by_status"]["status"],
                    values=data["orders_by_status"]["total_orders"],
                    hole=0.55,
                    marker=dict(colors=["#7c3aed","#3b82f6","#10b981","#f59e0b"]),
                    textfont=dict(family="DM Sans", color="white"),
                )])
                fig.update_layout(**CHART_THEME, title="Orders by Status",
                    annotations=[dict(text="Orders", x=0.5, y=0.5,
                                      font=dict(size=14, family="Syne", color="white"), showarrow=False)])
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if not data["monthly_revenue"].empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data["monthly_revenue"]["month"], y=data["monthly_revenue"]["revenue"],
                mode="lines+markers", line=dict(color="#7c3aed", width=3),
                marker=dict(size=8, color="#a78bfa", line=dict(color="#7c3aed", width=2)),
                fill="tozeroy", fillcolor="rgba(124,58,237,0.08)",
            ))
            fig.update_layout(**CHART_THEME, title="Monthly Revenue Trend")
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            if not data["top_products"].empty:
                fig = px.bar(data["top_products"], x="revenue", y="product_name",
                             orientation="h", title="Top Products by Revenue",
                             color="revenue", color_continuous_scale=["#3b82f6","#7c3aed"])
                fig.update_layout(**CHART_THEME, showlegend=False)
                fig.update_coloraxes(showscale=False)
                fig.update_traces(marker_line_width=0)
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            if not data["customers_by_country"].empty:
                fig = px.bar(data["customers_by_country"], x="country", y="total_customers",
                             title="Customers by Country", color="total_customers",
                             color_continuous_scale=["#10b981","#3b82f6"])
                fig.update_layout(**CHART_THEME, showlegend=False)
                fig.update_coloraxes(showscale=False)
                fig.update_traces(marker_line_width=0)
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)