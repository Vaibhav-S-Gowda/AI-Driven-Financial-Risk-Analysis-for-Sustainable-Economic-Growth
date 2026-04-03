SUSTAINABLE_INDICATORS = [
    "GDP growth (annual %)",
    "Inflation, consumer prices (annual %)",
    "Unemployment, total (% of total labor force) (modeled ILO estimate)",
    "Energy use (kg of oil equivalent per capita)",
    "CO2 emissions (metric tons per capita)",
    "Access to electricity (% of population)",
    "Foreign direct investment, net inflows (% of GDP)",
    "Individuals using the Internet (% of population)"
]

# ─── Plotly dark theme (2D only — do NOT spread into 3D layouts) ──────────────
PLOT_THEME_2D = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Sans', sans-serif", color="#7c84a0"),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(gridcolor="#1e2030", linecolor="#1e2030", zerolinecolor="#1e2030"),
    yaxis=dict(gridcolor="#1e2030", linecolor="#1e2030", zerolinecolor="#1e2030"),
    colorway=["#7c6cf0", "#0ecfab", "#fbbf24", "#f87171", "#4ade80"]
)

# Separate theme for 3D — no axis keys that would conflict with scene
PLOT_THEME_3D = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Sans', sans-serif", color="#7c84a0"),
    colorway=["#7c6cf0", "#0ecfab", "#fbbf24", "#f87171", "#4ade80"]
)

CLUSTER_COLORS = ["#7c6cf0", "#0ecfab", "#fbbf24", "#f87171", "#4ade80"]

SCENE_AXIS = dict(color="#7c84a0", showbackground=True,
                  backgroundcolor="rgba(255,255,255,0.02)", gridcolor="#1e2030")
