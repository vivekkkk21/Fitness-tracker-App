import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# ---------------- LOGIN USERS ----------------
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "viewer"},
}

# ---------------- NETWORK DATA ----------------
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

G = nx.DiGraph()
G.add_nodes_from(NODES.keys())
G.add_edges_from(EDGES)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None


# ---------------- LOGIN SCREEN ----------------
def login():
    st.title("🔌 Electrical Network Login")

    uid = st.text_input("User ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if uid in USERS and USERS[uid]["password"] == pwd:
            st.session_state.logged_in = True
            st.session_state.role = USERS[uid]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")


# ---------------- GRAPH FUNCTIONS ----------------
def upstream(node):
    return list(nx.ancestors(G, node))


def downstream(node):
    return list(nx.descendants(G, node))


def draw_flowchart(center):
    up = upstream(center)
    down = downstream(center)

    net = Network(height="700px", directed=True, layout=False)

    # ---- Add nodes with vertical levels ----
    for u in up:
        net.add_node(u, label=NODES[u], color="lightblue", level=0)

    net.add_node(center, label=NODES[center], color="orange", level=1)

    for d in down:
        net.add_node(d, label=NODES[d], color="lightgreen", level=2)

    # ---- Add edges only relevant to subtree ----
    for a, b in EDGES:
        if a in up + [center] and b in up + [center] + down:
            net.add_edge(a, b)

    # hierarchical top → bottom
    net.set_options("""
    var options = {
      "layout": {
        "hierarchical": {
          "direction": "UD",
          "sortMethod": "directed",
          "levelSeparation": 120,
          "nodeSpacing": 180
        }
      },
      "physics": false
    }
    """)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp.name)

    with open(tmp.name, "r", encoding="utf-8") as f:
        html = f.read()

    components.html(html, height=700)


# ---------------- MAIN APP ----------------
def app():
    st.title("⚡ Electrical Load Flow Viewer")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---- Search bar ----
    selected_name = st.selectbox(
        "Search Load / Panel",
        list(NODES.values())
    )

    selected_node = [k for k, v in NODES.items() if v == selected_name][0]

    st.subheader(f"Selected: {selected_name}")

    # ---- Draw vertical flowchart ----
    draw_flowchart(selected_node)

    # ---- Emergency impact ----
    if st.button("🚨 Show Downstream Impact"):
        st.warning("Highlighted downstream loads affected")
        st.write([NODES[d] for d in downstream(selected_node)])


# ---------------- ROUTING ----------------
if not st.session_state.logged_in:
    login()
else:
    app()
