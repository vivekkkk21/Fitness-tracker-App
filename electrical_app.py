import streamlit as st
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="Electrical Flow Viewer", layout="wide")

# -------------------------------------------------
# DEMO LOGIN USERS
# -------------------------------------------------
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "viewer"},
}

# -------------------------------------------------
# ELECTRICAL NETWORK DATA
# -------------------------------------------------
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
G.add_edges_from(EDGES)

# -------------------------------------------------
# SESSION
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
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


# -------------------------------------------------
# GRAPH HELPERS
# -------------------------------------------------
def upstream(node):
    return list(nx.ancestors(G, node))


def downstream(node):
    return list(nx.descendants(G, node))


# -------------------------------------------------
# DRAW VERTICAL FLOWCHART USING PLOTLY
# -------------------------------------------------
def draw_flowchart(center):
    up = upstream(center)
    down = downstream(center)

    sub_nodes = up + [center] + down
    subgraph = G.subgraph(sub_nodes)

    pos = {}

    # vertical layout
    for i, node in enumerate(up):
        pos[node] = (i, 2)

    pos[center] = (0, 1)

    for i, node in enumerate(down):
        pos[node] = (i, 0)

    edge_x = []
    edge_y = []

    for edge in subgraph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    labels = []
    colors = []

    for node in subgraph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        labels.append(NODES[node])

        if node == center:
            colors.append("orange")
        elif node in up:
            colors.append("lightblue")
        else:
            colors.append("lightgreen")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=labels,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(size=30, color=colors, line_width=2)
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
def app():
    st.title("⚡ Electrical Load Flow Viewer")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    selected_name = st.selectbox("Search Load / Panel", list(NODES.values()))
    selected_node = [k for k, v in NODES.items() if v == selected_name][0]

    st.subheader(f"Selected: {selected_name}")

    draw_flowchart(selected_node)

    if st.button("🚨 Show Downstream Impact"):
        affected = [NODES[d] for d in downstream(selected_node)]
        if affected:
            st.warning("Affected downstream loads:")
            st.write(affected)
        else:
            st.success("No downstream loads affected.")


# -------------------------------------------------
# ROUTING
# -------------------------------------------------
if not st.session_state.logged_in:
    login()
else:
    app()
