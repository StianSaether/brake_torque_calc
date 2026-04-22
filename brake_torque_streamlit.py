"""
AMR Brake Force Calculator  —  Fix Slope mode
----------------------------------------------
Streamlit version — matches original matplotlib layout.

Usage:
    pip install streamlit matplotlib numpy
    streamlit run brake_torque_streamlit.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st

G = 9.81
WEIGHT_MIN, WEIGHT_MAX = 10.0, 2000.0

st.set_page_config(page_title="AMR Brake Force Calculator", layout="wide")

# ── Physics ───────────────────────────────────────────────────────────────────
def calc_force(mass, slope_deg):
    return mass * G * np.sin(np.radians(slope_deg))

def calc_dfdm(slope_deg):
    return G * np.sin(np.radians(slope_deg))

# ── Sidebar / inputs ──────────────────────────────────────────────────────────
st.sidebar.title("Controls")
slope_deg = st.sidebar.number_input(
    "Fixed slope (°)", min_value=0.1, max_value=89.9,
    value=5.0, step=0.1, format="%.2f"
)
dot_mass = st.sidebar.slider(
    "Drag dot — Robot weight (kg)",
    min_value=int(WEIGHT_MIN), max_value=int(WEIGHT_MAX),
    value=400, step=1
)

# ── Compute ───────────────────────────────────────────────────────────────────
masses    = np.linspace(WEIGHT_MIN, WEIGHT_MAX, 500)
forces    = calc_force(masses, slope_deg)
dot_force = calc_force(dot_mass, slope_deg)
k         = calc_dfdm(slope_deg)
y_top     = forces.max() * 1.4

# ── Figure — matches original layout exactly ──────────────────────────────────
fig = plt.figure(figsize=(13, 8.5))
fig.patch.set_facecolor("#F4F4F2")
fig.suptitle("AMR Brake Force Calculator", fontsize=14, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 1, left=0.08, right=0.97, top=0.94, bottom=0.05,
                       hspace=0.48, height_ratios=[3.4, 1.1])

ax_main = fig.add_subplot(gs[0])
ax_main.set_facecolor("#FFFFFF")
for sp in ["top", "right"]:
    ax_main.spines[sp].set_visible(False)
ax_main.spines["left"].set_color("#CCCCCC")
ax_main.spines["bottom"].set_color("#CCCCCC")
ax_main.tick_params(colors="#555555")
ax_main.grid(True, color="#EEEEEE", linewidth=0.8)

# ── Control row ───────────────────────────────────────────────────────────────
gs_ctrl = gridspec.GridSpecFromSubplotSpec(
    2, 3, subplot_spec=gs[1],
    hspace=0.12, wspace=0.35,
    height_ratios=[0.35, 0.65],
)

ax_hdr = [fig.add_subplot(gs_ctrl[0, i]) for i in range(3)]
ax_inp = [fig.add_subplot(gs_ctrl[1, i]) for i in range(3)]

for ax in ax_hdr + ax_inp:
    ax.set_facecolor("#F4F4F2")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

# Col 0 — slope display
ax_hdr[0].text(0.5, 0.5, "Fixed slope (°)", ha="center", va="center",
               fontsize=10, fontweight="bold", color="#0F6E56",
               transform=ax_hdr[0].transAxes)
ax_inp[0].text(0.5, 0.5, f"{slope_deg:.2f}", ha="center", va="center",
               fontsize=18, fontweight="bold", color="#0F6E56",
               transform=ax_inp[0].transAxes)

# Col 1 — dot readout (purple panel)
ax_hdr[1].text(0.5, 0.5, "drag the dot  ●", ha="center", va="center",
               fontsize=9, color="#8880C0", style="italic",
               transform=ax_hdr[1].transAxes)
ax_inp[1].set_facecolor("#EEEDFE")
for s in ax_inp[1].spines.values():
    s.set_visible(True); s.set_color("#AFA9EC"); s.set_linewidth(1.2)
ax_inp[1].text(0.5, 0.5,
               f"Weight: {dot_mass:.0f} kg\nForce:  {dot_force:.1f} N",
               ha="center", va="center",
               fontsize=11, fontweight="bold", color="#3C3089",
               transform=ax_inp[1].transAxes)

# Col 2 — dF/dm box (teal panel)
ax_hdr[2].text(0.5, 0.5, "dF/dm  (force per kg added)", ha="center", va="center",
               fontsize=10, fontweight="bold", color="#085041",
               transform=ax_hdr[2].transAxes)
ax_inp[2].set_facecolor("#E1F5EE")
for s in ax_inp[2].spines.values():
    s.set_visible(True); s.set_color("#5DCAA5"); s.set_linewidth(1.2)
ax_inp[2].text(0.5, 0.65, f"{k:.4f} N/kg", ha="center", va="center",
               fontsize=13, fontweight="bold", color="#085041",
               transform=ax_inp[2].transAxes)
ax_inp[2].text(0.5, 0.22,
               f"+1 kg  →  +{k:.3f} N     |     +10 kg  →  +{k*10:.2f} N",
               ha="center", va="center",
               fontsize=8.5, color="#0F6E56", style="italic",
               transform=ax_inp[2].transAxes)

# ── Main plot ─────────────────────────────────────────────────────────────────
ax_main.plot(masses, forces, color="#1D9E75", linewidth=2.5, zorder=2)

ax_main.fill_between(masses, 0,     forces, alpha=0.08, color="#1D9E75", zorder=1)
ax_main.fill_between(masses, forces, y_top,  alpha=0.05, color="#E24B4A", zorder=1)

xi = masses[int(len(masses) * 0.25)]
yi = calc_force(xi, slope_deg)
ax_main.text(xi, yi * 0.38, "▲ brake exceeds requirement",
             fontsize=8.5, style="italic", color="#0F6E56", alpha=0.8,
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7))
ax_main.text(xi, yi * 1.65, "▼ brake too weak",
             fontsize=8.5, style="italic", color="#A32D2D", alpha=0.8,
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7))

ax_main.scatter([dot_mass], [dot_force], s=130, color="#534AB7", zorder=6)
ax_main.axvline(x=dot_mass, color="#534AB7", linewidth=0.8, linestyle=":", alpha=0.5, zorder=3)
ax_main.axhline(y=dot_force, color="#534AB7", linewidth=0.8, linestyle=":", alpha=0.5, zorder=3)

ax_main.set_xlim(WEIGHT_MIN, WEIGHT_MAX)
ax_main.set_ylim(0, y_top)
ax_main.set_xlabel("Robot weight (kg)", color="#555555")
ax_main.set_ylabel("Required brake force (N)", color="#555555")
ax_main.set_title(
    f"Brake force vs weight  |  Slope = {slope_deg:.2f}°   "
    f"(dF/dm = {calc_dfdm(slope_deg):.4f} N/kg)",
    fontsize=11)

# ── Hint ──────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.005,
         "Set slope and weight using the controls in the sidebar.",
         ha="center", fontsize=8, color="#888888", style="italic")

st.pyplot(fig)
plt.close(fig)