"""
AMR Brake Force Calculator  —  Fix Slope mode
----------------------------------------------
Fixes the slope angle and plots brake force vs robot weight.
The relationship is perfectly linear: F = m * g * sin(θ)

The derivative dF/dm = g * sin(θ) is constant for a fixed slope,
giving the force increase per kg of added weight.

A draggable dot on the curve lets you read off exact values.

Usage:
    pip install matplotlib numpy
    python brake_force_calculator.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import TextBox

G = 9.81

# ── Reference robots ──────────────────────────────────────────────────────────
ROBOTS = {
    "Arnold (600 kg, 5°)":      {"mass": 600, "slope_deg": 5.0,                        "color": "#E24B4A"},
    "Mecanum AMR (400 kg, 3%)": {"mass": 400, "slope_deg": np.degrees(np.arctan(0.03)), "color": "#BA7517"},
}

# ── Physics ───────────────────────────────────────────────────────────────────
def calc_force(mass, slope_deg):
    return mass * G * np.sin(np.radians(slope_deg))

def calc_dfdm(slope_deg):
    """Force increase per kg: dF/dm = g * sin(θ)"""
    return G * np.sin(np.radians(slope_deg))

# ── State ─────────────────────────────────────────────────────────────────────
state = {
    "slope_deg": 5.0,
    "dot_mass":  400.0,
    "dragging":  False,
    "updating":  False,
}

WEIGHT_MIN, WEIGHT_MAX = 10.0, 2000.0

# ── Figure ────────────────────────────────────────────────────────────────────
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

# ── Control row: slope input | dot readout | dF/dm box ───────────────────────
gs_ctrl = gridspec.GridSpecFromSubplotSpec(
    2, 3, subplot_spec=gs[1],
    hspace=0.12, wspace=0.35,
    height_ratios=[0.35, 0.65],
)

ax_hdr  = [fig.add_subplot(gs_ctrl[0, i]) for i in range(3)]
ax_inp  = [fig.add_subplot(gs_ctrl[1, i]) for i in range(3)]

for ax in ax_hdr + ax_inp:
    ax.set_facecolor("#F4F4F2")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

# Col 0 — slope input
ax_hdr[0].text(0.5, 0.5, "Fixed slope (°)", ha="center", va="center",
               fontsize=10, fontweight="bold", color="#0F6E56",
               transform=ax_hdr[0].transAxes)
slope_box = TextBox(ax_inp[0], "", initial="5.00")
slope_box.text_disp.set_fontsize(13)

# Col 1 — dot readout (purple panel)
ax_hdr[1].text(0.5, 0.5, "drag the dot  ●", ha="center", va="center",
               fontsize=9, color="#8880C0", style="italic",
               transform=ax_hdr[1].transAxes)
ax_inp[1].set_facecolor("#EEEDFE")
for s in ax_inp[1].spines.values():
    s.set_visible(True); s.set_color("#AFA9EC"); s.set_linewidth(1.2)
readout_text = ax_inp[1].text(0.5, 0.5, "", ha="center", va="center",
                               fontsize=11, fontweight="bold", color="#3C3089",
                               transform=ax_inp[1].transAxes)

# Col 2 — dF/dm box (teal panel)
ax_hdr[2].text(0.5, 0.5, "dF/dm  (force per kg added)", ha="center", va="center",
               fontsize=10, fontweight="bold", color="#085041",
               transform=ax_hdr[2].transAxes)
ax_inp[2].set_facecolor("#E1F5EE")
for s in ax_inp[2].spines.values():
    s.set_visible(True); s.set_color("#5DCAA5"); s.set_linewidth(1.2)
dfdm_line1 = ax_inp[2].text(0.5, 0.65, "", ha="center", va="center",
                              fontsize=13, fontweight="bold", color="#085041",
                              transform=ax_inp[2].transAxes)
dfdm_line2 = ax_inp[2].text(0.5, 0.22, "", ha="center", va="center",
                              fontsize=8.5, color="#0F6E56", style="italic",
                              transform=ax_inp[2].transAxes)

# ── Plot objects ──────────────────────────────────────────────────────────────
fill_safe   = None
fill_unsafe = None
curve_line, = ax_main.plot([], [], color="#1D9E75", linewidth=2.5, zorder=2)
dot_scatter = ax_main.scatter([], [], s=130, color="#534AB7", zorder=6, picker=8)
dot_vline   = ax_main.axvline(x=0, color="#534AB7", linewidth=0.8,
                               linestyle=":", alpha=0.5, zorder=3)
dot_hline   = ax_main.axhline(y=0, color="#534AB7", linewidth=0.8,
                               linestyle=":", alpha=0.5, zorder=3)
safe_label   = ax_main.text(0, 0, "", fontsize=8.5, style="italic", color="#0F6E56",
                             alpha=0.8, bbox=dict(boxstyle="round,pad=0.3",
                                                   fc="white", ec="none", alpha=0.7))
unsafe_label = ax_main.text(0, 0, "", fontsize=8.5, style="italic", color="#A32D2D",
                             alpha=0.8, bbox=dict(boxstyle="round,pad=0.3",
                                                   fc="white", ec="none", alpha=0.7))
robot_plots  = {}
robot_annots = {}
for name, r in ROBOTS.items():
    sc, = ax_main.plot([], [], "o", color=r["color"], markersize=8, zorder=5)
    an  = ax_main.annotate("", (0, 0), fontsize=8, color=r["color"],
                            xytext=(7, 0), textcoords="offset points", va="center")
    robot_plots[name]  = sc
    robot_annots[name] = an

# ── Draw ──────────────────────────────────────────────────────────────────────
def draw():
    global fill_safe, fill_unsafe
    slope = state["slope_deg"]
    dm    = state["dot_mass"]

    masses = np.linspace(WEIGHT_MIN, WEIGHT_MAX, 500)
    forces = calc_force(masses, slope)

    curve_line.set_data(masses, forces)

    # Safe/unsafe fill
    if fill_safe:   fill_safe.remove()
    if fill_unsafe: fill_unsafe.remove()
    y_top = forces.max() * 1.4
    fill_safe   = ax_main.fill_between(masses, 0,     forces, alpha=0.08,
                                        color="#1D9E75", zorder=1)
    fill_unsafe = ax_main.fill_between(masses, forces, y_top,  alpha=0.05,
                                        color="#E24B4A", zorder=1)

    # Safe/unsafe labels at ~25% of x range
    xi = masses[int(len(masses) * 0.25)]
    yi = calc_force(xi, slope)
    safe_label.set_position((xi, yi * 0.38))
    safe_label.set_text("▲ brake exceeds requirement")
    unsafe_label.set_position((xi, yi * 1.65))
    unsafe_label.set_text("▼ brake too weak")

    # Dot
    df = calc_force(dm, slope)
    dot_scatter.set_offsets([[dm, df]])
    dot_vline.set_xdata([dm])
    dot_hline.set_ydata([df])
    readout_text.set_text(f"Weight: {dm:.0f} kg\nForce:  {df:.1f} N")

    # dF/dm panel
    k = calc_dfdm(slope)
    dfdm_line1.set_text(f"{k:.4f} N/kg")
    dfdm_line2.set_text(f"+1 kg  →  +{k:.3f} N     |     +10 kg  →  +{k*10:.2f} N")

    # Axes
    ax_main.set_xlim(WEIGHT_MIN, WEIGHT_MAX)
    ax_main.set_ylim(0, y_top)
    ax_main.set_xlabel("Robot weight (kg)", color="#555555")
    ax_main.set_ylabel("Required brake force (N)", color="#555555")
    ax_main.set_title(
        f"Brake force vs weight  |  Slope = {slope:.2f}°   "
        f"(dF/dm = {calc_dfdm(slope):.4f} N/kg)",
        fontsize=11)

    # Reference robots — plot at their actual slope's force on this weight axis
    for name, r in ROBOTS.items():
        ry = calc_force(r["mass"], slope)   # force at that mass on current slope
        robot_plots[name].set_data([r["mass"]], [ry])
        robot_annots[name].set_position((r["mass"], ry))
        robot_annots[name].set_text(f"  {name.split('(')[0].strip()}")

    fig.canvas.draw_idle()

# ── Callbacks ─────────────────────────────────────────────────────────────────
def on_slope_box(text):
    if state["updating"]:
        return
    try:
        val = float(text)
        if val <= 0 or val >= 90:
            return
    except ValueError:
        return
    state["slope_deg"] = val
    draw()

slope_box.on_submit(on_slope_box)
slope_box.on_text_change(on_slope_box)

# ── Drag ──────────────────────────────────────────────────────────────────────
def on_press(event):
    if event.inaxes != ax_main or event.button != 1:
        return
    offsets = dot_scatter.get_offsets()
    if len(offsets) == 0:
        return
    dx, dy = offsets[0]
    disp_dot   = ax_main.transData.transform([dx, dy])
    disp_click = np.array([event.x, event.y])
    if np.linalg.norm(disp_dot - disp_click) < 18:
        state["dragging"] = True

def on_motion(event):
    if not state["dragging"] or event.inaxes != ax_main:
        return
    new_mass = float(np.clip(event.xdata, WEIGHT_MIN, WEIGHT_MAX))
    state["dot_mass"] = new_mass
    slope = state["slope_deg"]
    df    = calc_force(new_mass, slope)
    dot_scatter.set_offsets([[new_mass, df]])
    dot_vline.set_xdata([new_mass])
    dot_hline.set_ydata([df])
    readout_text.set_text(f"Weight: {new_mass:.0f} kg\nForce:  {df:.1f} N")
    fig.canvas.draw_idle()

def on_release(event):
    state["dragging"] = False

fig.canvas.mpl_connect("button_press_event",   on_press)
fig.canvas.mpl_connect("motion_notify_event",  on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

# ── Hint ──────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.005,
         "Type a slope in the box to update the curve.  "
         "Click and drag the purple dot to read off weight/force pairs.",
         ha="center", fontsize=8, color="#888888", style="italic")

# ── Init ──────────────────────────────────────────────────────────────────────
draw()
plt.show()