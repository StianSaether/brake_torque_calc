"""
AMR Brake Force Calculator — Streamlit version
-----------------------------------------------
Fixes the slope angle and plots brake force vs robot weight.
F = m * g * sin(θ)

Usage:
    pip install streamlit matplotlib numpy
    streamlit run brake_torque_streamlit.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st

G = 9.81
WEIGHT_MIN, WEIGHT_MAX = 10.0, 2000.0

st.set_page_config(page_title="AMR Brake Force Calculator", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans', sans-serif;
        }
        .main { background-color: #F4F4F2; }
        .metric-box {
            background: #E1F5EE;
            border: 1.5px solid #5DCAA5;
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }
        .metric-box .label {
            font-size: 12px;
            font-weight: 600;
            color: #085041;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-box .value {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 26px;
            font-weight: 600;
            color: #085041;
            margin: 4px 0;
        }
        .metric-box .sub {
            font-size: 11px;
            color: #0F6E56;
            font-style: italic;
        }
        .readout-box {
            background: #EEEDFE;
            border: 1.5px solid #AFA9EC;
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }
        .readout-box .label {
            font-size: 12px;
            font-weight: 600;
            color: #3C3089;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .readout-box .value {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 22px;
            font-weight: 600;
            color: #3C3089;
            margin: 4px 0;
        }
        h1 {
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 600;
            color: #0F2620;
        }
        .stSlider > div > div > div > div {
            background-color: #1D9E75;
        }
    </style>
""", unsafe_allow_html=True)

# ── Physics ───────────────────────────────────────────────────────────────────
def calc_force(mass, slope_deg):
    return mass * G * np.sin(np.radians(slope_deg))

def calc_dfdm(slope_deg):
    return G * np.sin(np.radians(slope_deg))

# ── Header ────────────────────────────────────────────────────────────────────
st.title("AMR Brake Force Calculator")
st.caption("Required brake force as a function of robot weight at a fixed slope angle. F = m · g · sin(θ)")

st.divider()

# ── Controls ──────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 1])

with col_ctrl1:
    slope_deg = st.number_input(
        "Fixed slope (°)",
        min_value=0.1,
        max_value=89.9,
        value=5.0,
        step=0.1,
        format="%.2f",
        help="Enter the slope angle in degrees"
    )

with col_ctrl2:
    dot_mass = st.slider(
        "Robot weight (kg)",
        min_value=int(WEIGHT_MIN),
        max_value=int(WEIGHT_MAX),
        value=400,
        step=1,
        help="Drag to read off force at a specific weight"
    )

with col_ctrl3:
    st.write("")  # spacer

# ── Compute ───────────────────────────────────────────────────────────────────
masses = np.linspace(WEIGHT_MIN, WEIGHT_MAX, 500)
forces = calc_force(masses, slope_deg)
dot_force = calc_force(dot_mass, slope_deg)
k = calc_dfdm(slope_deg)
y_top = forces.max() * 1.4

# ── Metric panels ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""
        <div class="readout-box">
            <div class="label">At selected weight</div>
            <div class="value">{dot_mass} kg → {dot_force:.1f} N</div>
            <div class="sub">Required brake force at {slope_deg:.2f}°</div>
        </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
        <div class="metric-box">
            <div class="label">dF/dm — Force per kg added</div>
            <div class="value">{k:.4f} N/kg</div>
            <div class="sub">+1 kg → +{k:.3f} N &nbsp;|&nbsp; +10 kg → +{k*10:.2f} N</div>
        </div>
    """, unsafe_allow_html=True)

with m3:
    slope_pct = np.tan(np.radians(slope_deg)) * 100
    st.markdown(f"""
        <div class="metric-box">
            <div class="label">Slope</div>
            <div class="value">{slope_deg:.2f}° = {slope_pct:.1f}%</div>
            <div class="sub">sin({slope_deg:.2f}°) = {np.sin(np.radians(slope_deg)):.5f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor("#F4F4F2")
ax.set_facecolor("#FFFFFF")

for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color("#CCCCCC")
ax.spines["bottom"].set_color("#CCCCCC")
ax.tick_params(colors="#555555")
ax.grid(True, color="#EEEEEE", linewidth=0.8)

# Curve
ax.plot(masses, forces, color="#1D9E75", linewidth=2.5, zorder=2)

# Fill regions
ax.fill_between(masses, 0, forces, alpha=0.08, color="#1D9E75", zorder=1)
ax.fill_between(masses, forces, y_top, alpha=0.05, color="#E24B4A", zorder=1)

# Region labels
xi = masses[int(len(masses) * 0.25)]
yi = calc_force(xi, slope_deg)
ax.text(xi, yi * 0.38, "▲ brake exceeds requirement",
        fontsize=8.5, style="italic", color="#0F6E56", alpha=0.8,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7))
ax.text(xi, yi * 1.65, "▼ brake too weak",
        fontsize=8.5, style="italic", color="#A32D2D", alpha=0.8,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7))

# Dot + crosshairs
ax.scatter([dot_mass], [dot_force], s=130, color="#534AB7", zorder=6)
ax.axvline(x=dot_mass, color="#534AB7", linewidth=0.8, linestyle=":", alpha=0.5, zorder=3)
ax.axhline(y=dot_force, color="#534AB7", linewidth=0.8, linestyle=":", alpha=0.5, zorder=3)
ax.annotate(f"  {dot_mass} kg\n  {dot_force:.1f} N",
            (dot_mass, dot_force), fontsize=9, color="#534AB7",
            xytext=(10, 10), textcoords="offset points")

ax.set_xlim(WEIGHT_MIN, WEIGHT_MAX)
ax.set_ylim(0, y_top)
ax.set_xlabel("Robot weight (kg)", color="#555555")
ax.set_ylabel("Required brake force (N)", color="#555555")
ax.set_title(
    f"Brake force vs weight  |  Slope = {slope_deg:.2f}°   "
    f"(dF/dm = {k:.4f} N/kg)",
    fontsize=11, color="#222222"
)

st.pyplot(fig)
plt.close(fig)

st.caption("Use the slope input and weight slider above to explore the relationship. "
           "The purple dot marks the selected weight/force pair.")