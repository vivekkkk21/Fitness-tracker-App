import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# -------------------------------
# SIMPLE LOGIN DATA (DEMO ONLY)
# -------------------------------
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "viewer"},
}

# -------------------------------
# ELECTRICAL NETWORK DATA
# -------------------------------
NODES = {
    "TOB6": "TOB No. 6",
    "TOB9": "TOB No. 9",
    "KAV1001": "KAV 10-01",
    "X1": "X1 Feeder",
    "X2": "X2 Feeder",
    "KV4501": "KV 45-01",
    "KV4502": "KV 45-02",
    "LVP02": "LV Panel-02",
    "LVP03": "LV Panel-03",
    "QLEROOM": "QLE Room",
    "LVDB06": "LV DB 06",
    "UV1A": "UV Panel 01-A",
    "UV0": "UV Panel 0",
    "UV1B": "UV Panel 01-B",
    "S1": "S1", "S2": "S2", "S3": "S3", "S4": "S4", "S5": "S5", "S6": "S6",
    "SW1": "SW1", "SW2": "SW2", "SW3": "SW3", "SW4": "SW4",
    "SE1": "SE1", "SE2": "SE2",
}

EDGES = [
    ("TOB6", "KAV1001"), ("TOB9", "KAV1001"),
    ("KAV1001", "X1"), ("KAV1001", "X2"),
    ("X1", "KV4501"), ("X2", "KV4502"),
    ("KV4501", "LVP02"), ("KV4501", "LVP03"),
    ("KV4501", "QLEROOM"), ("KV4501", "LVDB06"),
    ("LVP02", "UV1A"), ("LVP03", "UV0"), ("QLEROOM", "UV1B"),
    ("UV1A", "S1"), ("UV1A", "S2"), ("UV1A", "S3"),
    ("UV1A", "S4"), ("UV1A", "S5"), ("UV1A", "S6"),
    ("UV0", "SW1"), ("UV0", "SW2"), ("UV0", "SW3"), ("UV0", "SW4"),
    ("UV1B", "SE1"), ("UV1B", "SE2"),
]

# -------------------------------
# BUILD GRAPH
# -------------------------------
G = nx.DiGraph()
G.add_nodes_from(NODES.keys())
G.add_edges_from(EDGES)

# -------------------------------
# LOGIN STATE
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None


# -------------------------------
# LOGIN SCREEN
# -------------------------------
def login_screen():
    st.title("🔌 Electrical Network Navigation – Demo Login")

    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if user_id in USERS and USERS[user_id]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[user_id]["role"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


# -------------------------------
# GRAPH UTILITIES
# -------------------------------
def get_upstream(node):
    return nx.ancestors(G, node)


def get_downstream(node):
    return nx.descendants(G, node)


def draw_graph(center_node=None, highlight_nodes=None):
    net = Network(height="600px", directed=True)

    for node in G.nodes():
        color = "#97C2FC"

        if highlight_nodes and node in highlight_nodes:
            color = "red"

        if node == center_node:
            color = "orange"

        net.add_node(node, label=NODES[node], color=color)

    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp_file.name)

    with open(tmp_file.name, "r", encoding="utf-8") as f:
        html = f.read()

    st.components.v1.html(html, height=600)


# -------------------------------
# MAIN APP
# -------------------------------
def main_app():
    st.title("⚡ Electrical Network Navigator")

    st.sidebar.write(f"**Logged in as:** {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # SEARCH
    selected_name = st.selectbox(
        "Search Panel / Switch / Load",
        options=list(NODES.values())
    )

    selected_node = [k for k, v in NODES.items() if v == selected_name][0]

    st.subheader(f"Selected: {selected_name}")

    upstream = get_upstream(selected_node)
    downstream = get_downstream(selected_node)

    col1, col2 = st.columns(2)

    with col1:
        st.write("### ⬆ Upstream to Source")
        if upstream:
            for u in upstream:
                st.write("-", NODES[u])
        else:
            st.write("No upstream (Source node)")

    with col2:
        st.write("### ⬇ Downstream Impact")
        if downstream:
            for d in downstream:
                st.write("-", NODES[d])
        else:
            st.write("No downstream (End load)")

    # EMERGENCY IMPACT
    if st.button("🚨 If this is turned OFF"):
        st.warning("Affected downstream loads highlighted in RED")
        draw_graph(center_node=selected_node, highlight_nodes=downstream)
    else:
        draw_graph(center_node=selected_node)


# -------------------------------
# APP ROUTING
# -------------------------------
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()

