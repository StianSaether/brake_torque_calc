"""
AMR Brake Force Calculator
---------------------------
Three plot modes, each fixing one variable and plotting the relationship
between the other two. A draggable dot on the curve lets you read off
exact values interactively.

Modes:
  Fix Weight  → plot: Force vs Slope      (drag dot along curve)
  Fix Slope   → plot: Force vs Weight     (drag dot along curve)
  Fix Force   → plot: Weight vs Slope     (drag dot along curve)

Usage:
    pip install matplotlib numpy
    python brake_force_calculator.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import TextBox, RadioButtons

G = 9.81

# ── Reference robots ──────────────────────────────────────────────────────────
ROBOTS = {
    "Arnold (600 kg, 5°)":      {"mass": 600, "slope_deg": 5.0,                        "color": "#E24B4A"},
    "Mecanum AMR (400 kg, 3%)": {"mass": 400, "slope_deg": np.degrees(np.arctan(0.03)), "color": "#BA7517"},
}

# ── Physics ───────────────────────────────────────────────────────────────────
def calc_force(mass, slope_deg):
    return mass * G * np.sin(np.radians(slope_deg))

def calc_mass(force, slope_deg):
    s = np.sin(np.radians(slope_deg))
    return (force / (G * s)) if s > 0 else None

def calc_slope(force, mass):
    if not mass or mass <= 0:
        return None
    ratio = force / (mass * G)
    return np.degrees(np.arcsin(np.clip(ratio, 0, 1))) if ratio <= 1 else None

# ── State ─────────────────────────────────────────────────────────────────────
MODE_WEIGHT = "weight"   # fix weight  → force vs slope
MODE_SLOPE  = "slope"    # fix slope   → force vs weight
MODE_FORCE  = "force"    # fix force   → weight vs slope

MODE_CONFIG = {
    MODE_WEIGHT: dict(
        fixed_label="Weight (kg)", fixed_init=600.0, fixed_min=10,   fixed_max=2000,
        x_label="Slope (°)",       x_min=0.5,        x_max=20.0,
        y_label="Required brake force (N)",
        title=lambda v: f"Brake force vs slope  |  Weight = {v:.0f} kg",
        curve=lambda x, fv: calc_force(fv, x),
        dot_init_x=5.0,
        dot_readout=lambda x, y: f"Slope: {x:.2f}°   →   Force needed: {y:.1f} N",
        safe_side="below",
        safe_text="brake exceeds requirement",
        unsafe_text="brake too weak",
    ),
    MODE_SLOPE: dict(
        fixed_label="Slope (°)", fixed_init=5.0, fixed_min=0.1, fixed_max=20.0,
        x_label="Robot weight (kg)", x_min=10, x_max=2000,
        y_label="Required brake force (N)",
        title=lambda v: f"Brake force vs weight  |  Slope = {v:.2f}°",
        curve=lambda x, fv: calc_force(x, fv),
        dot_init_x=400.0,
        dot_readout=lambda x, y: f"Weight: {x:.0f} kg   →   Force needed: {y:.1f} N",
        safe_side="below",
        safe_text="brake exceeds requirement",
        unsafe_text="brake too weak",
    ),
    MODE_FORCE: dict(
        fixed_label="Brake force (N)", fixed_init=calc_force(600, 5), fixed_min=10, fixed_max=5000,
        x_label="Slope (°)", x_min=0.5, x_max=20.0,
        y_label="Max robot weight (kg)",
        title=lambda v: f"Max weight vs slope  |  Brake force = {v:.0f} N",
        curve=lambda x, fv: calc_mass(fv, x),
        dot_init_x=5.0,
        dot_readout=lambda x, y: f"Slope: {x:.2f}°   →   Max weight: {y:.1f} kg",
        safe_side="below",
        safe_text="safe  (robot within limit)",
        unsafe_text="unsafe  (robot too heavy)",
    ),
}

state = {
    "mode":       MODE_WEIGHT,
    "fixed_val":  600.0,
    "dot_x":      5.0,
    "dragging":   False,
    "updating":   False,
}

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(13, 8.5))
fig.patch.set_facecolor("#F4F4F2")
fig.suptitle("AMR Brake Force Calculator", fontsize=14, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 1, left=0.08, right=0.97, top=0.94, bottom=0.04,
                       hspace=0.50, height_ratios=[3.4, 1.0])

ax_main = fig.add_subplot(gs[0])
ax_main.set_facecolor("#FFFFFF")
for sp in ["top", "right"]:
    ax_main.spines[sp].set_visible(False)
ax_main.spines["left"].set_color("#CCCCCC")
ax_main.spines["bottom"].set_color("#CCCCCC")
ax_main.tick_params(colors="#555555")
ax_main.grid(True, color="#EEEEEE", linewidth=0.8)

# Controls row
gs_ctrl = gridspec.GridSpecFromSubplotSpec(
    2, 3, subplot_spec=gs[1],
    hspace=0.15, wspace=0.35,
    height_ratios=[0.38, 0.62],
)

ax_hdr_fixed = fig.add_subplot(gs_ctrl[0, 0])
ax_inp_fixed = fig.add_subplot(gs_ctrl[1, 0])
ax_hdr_radio = fig.add_subplot(gs_ctrl[0, 1])
ax_inp_radio = fig.add_subplot(gs_ctrl[1, 1])
ax_readout   = fig.add_subplot(gs_ctrl[:, 2])

for ax in [ax_hdr_fixed, ax_inp_fixed, ax_hdr_radio, ax_inp_radio, ax_readout]:
    ax.set_facecolor("#F4F4F2")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

# Fixed variable header + textbox
fixed_hdr = ax_hdr_fixed.text(0.5, 0.5, "Weight (kg)", ha="center", va="center",
                               fontsize=10, fontweight="bold", color="#185FA5",
                               transform=ax_hdr_fixed.transAxes)
fixed_box = TextBox(ax_inp_fixed, "", initial="600.0")
fixed_box.text_disp.set_fontsize(13)

# Mode selector
ax_hdr_radio.text(0.5, 0.5, "Fix variable", ha="center", va="center",
                  fontsize=10, fontweight="bold", color="#444441",
                  transform=ax_hdr_radio.transAxes)
radio = RadioButtons(ax_inp_radio,
                     ("Fix weight", "Fix slope", "Fix force"),
                     activecolor="#534AB7")
for lbl in radio.labels:
    lbl.set_fontsize(9)

# Readout panel
ax_readout.set_facecolor("#EEEDFE")
for s in ax_readout.spines.values():
    s.set_visible(True)
    s.set_color("#AFA9EC")
    s.set_linewidth(1.2)
readout_text = ax_readout.text(0.5, 0.5, "", ha="center", va="center",
                                fontsize=11, fontweight="bold", color="#3C3489",
                                transform=ax_readout.transAxes, wrap=True)
ax_readout.text(0.5, 0.92, "drag the dot ●", ha="center", va="top",
                fontsize=8, color="#8880C0", style="italic",
                transform=ax_readout.transAxes)

# ── Plot objects (persistent, updated in place) ───────────────────────────────
curve_line,    = ax_main.plot([], [], color="#378ADD", linewidth=2, zorder=2)
fill_safe      = None
fill_unsafe    = None
dot_scatter    = ax_main.scatter([], [], s=120, color="#534AB7", zorder=6,
                                  picker=8, label="drag me")
dot_vline      = ax_main.axvline(x=0, color="#534AB7", linewidth=0.8,
                                  linestyle=":", alpha=0.5, zorder=3)
dot_hline      = ax_main.axhline(y=0, color="#534AB7", linewidth=0.8,
                                  linestyle=":", alpha=0.5, zorder=3)
safe_label     = ax_main.text(0, 0, "", fontsize=8.5, style="italic",
                               color="#0F6E56", alpha=0.75,
                               bbox=dict(boxstyle="round,pad=0.3",
                                         fc="white", ec="none", alpha=0.7))
unsafe_label   = ax_main.text(0, 0, "", fontsize=8.5, style="italic",
                               color="#A32D2D", alpha=0.75,
                               bbox=dict(boxstyle="round,pad=0.3",
                                         fc="white", ec="none", alpha=0.7))
robot_scatter  = {}
robot_annots   = {}
for name, r in ROBOTS.items():
    sc, = ax_main.plot([], [], "o", color=r["color"], markersize=7, zorder=5)
    an  = ax_main.annotate("", (0, 0), fontsize=7.5, color=r["color"],
                            xytext=(6, 0), textcoords="offset points",
                            va="center")
    robot_scatter[name] = sc
    robot_annots[name]  = an

# ── Draw ──────────────────────────────────────────────────────────────────────
def draw():
    global fill_safe, fill_unsafe
    cfg = MODE_CONFIG[state["mode"]]
    fv  = state["fixed_val"]
    dx  = state["dot_x"]

    x_arr = np.linspace(cfg["x_min"], cfg["x_max"], 500)
    y_arr = np.array([cfg["curve"](xi, fv) for xi in x_arr], dtype=float)
    valid = np.isfinite(y_arr) & (y_arr > 0)
    x_arr, y_arr = x_arr[valid], y_arr[valid]

    # Curve
    curve_line.set_data(x_arr, y_arr)

    # Fill safe/unsafe
    if fill_safe:
        fill_safe.remove()
    if fill_unsafe:
        fill_unsafe.remove()
    y_max_plot = y_arr.max() * 2.2 if len(y_arr) else 100
    if cfg["safe_side"] == "below":
        fill_safe   = ax_main.fill_between(x_arr, 0,     y_arr, alpha=0.07,
                                            color="#1D9E75", zorder=1)
        fill_unsafe = ax_main.fill_between(x_arr, y_arr, y_max_plot, alpha=0.05,
                                            color="#E24B4A", zorder=1)

    # Dot
    dy = cfg["curve"](dx, fv)
    if dy and dy > 0:
        dot_scatter.set_offsets([[dx, dy]])
        dot_vline.set_xdata([dx])
        dot_hline.set_ydata([dy])
        readout_text.set_text(cfg["dot_readout"](dx, dy))
    else:
        dot_scatter.set_offsets(np.empty((0, 2)))
        readout_text.set_text("out of range")

    # Safe/unsafe labels — positioned at 30% and 70% of x range
    if len(x_arr) > 10:
        xi_lo = x_arr[int(len(x_arr) * 0.28)]
        xi_hi = x_arr[int(len(x_arr) * 0.28)]
        yi_at = cfg["curve"](xi_lo, fv) or 1
        safe_label.set_position((xi_lo, yi_at * 0.38))
        safe_label.set_text("▲ " + cfg["safe_text"])
        unsafe_label.set_position((xi_hi, yi_at * 1.62))
        unsafe_label.set_text("▼ " + cfg["unsafe_text"])

    # Axis limits
    ax_main.set_xlim(cfg["x_min"], cfg["x_max"])
    y_lo = 0
    y_hi = y_arr.max() * 1.35 if len(y_arr) else 100
    # For weight mode extend to show unsafe zone
    ax_main.set_ylim(y_lo, y_hi)

    ax_main.set_xlabel(cfg["x_label"], color="#555555")
    ax_main.set_ylabel(cfg["y_label"], color="#555555")
    ax_main.set_title(cfg["title"](fv), fontsize=11)

    # Reference robots
    for name, r in ROBOTS.items():
        rx = r["slope_deg"] if state["mode"] != MODE_SLOPE else r["mass"]
        ry = cfg["curve"](rx, fv)
        if ry and ry > 0:
            robot_scatter[name].set_data([rx], [ry])
            robot_annots[name].set_position((rx, ry))
            robot_annots[name].set_text(f"  {name.split('(')[0].strip()}")
        else:
            robot_scatter[name].set_data([], [])
            robot_annots[name].set_text("")

    fig.canvas.draw_idle()

# ── Callbacks ─────────────────────────────────────────────────────────────────
MODE_MAP = {
    "Fix weight": MODE_WEIGHT,
    "Fix slope":  MODE_SLOPE,
    "Fix force":  MODE_FORCE,
}
HDR_PROPS = {
    MODE_WEIGHT: ("Weight (kg)",     "#185FA5"),
    MODE_SLOPE:  ("Slope (°)",       "#0F6E56"),
    MODE_FORCE:  ("Brake force (N)", "#3C3489"),
}

def on_radio(label):
    mode = MODE_MAP[label]
    state["mode"] = mode
    cfg = MODE_CONFIG[mode]
    state["fixed_val"] = cfg["fixed_init"]
    state["dot_x"]     = cfg["dot_init_x"]
    # Update fixed box
    state["updating"] = True
    dec = 2 if mode == MODE_SLOPE else 1
    fixed_box.set_val(f"{cfg['fixed_init']:.{dec}f}")
    state["updating"] = False
    # Update header
    title, color = HDR_PROPS[mode]
    fixed_hdr.set_text(title)
    fixed_hdr.set_color(color)
    # Update curve colour
    CURVE_COLORS = {MODE_WEIGHT: "#378ADD", MODE_SLOPE: "#1D9E75", MODE_FORCE: "#534AB7"}
    curve_line.set_color(CURVE_COLORS[mode])
    draw()

def on_fixed_box(text):
    if state["updating"]:
        return
    try:
        val = float(text)
        if val <= 0:
            return
    except ValueError:
        return
    state["fixed_val"] = val
    draw()

radio.on_clicked(on_radio)
fixed_box.on_submit(on_fixed_box)
fixed_box.on_text_change(on_fixed_box)

# ── Drag logic ────────────────────────────────────────────────────────────────
def on_press(event):
    if event.inaxes != ax_main:
        return
    if event.button != 1:
        return
    # Check if click is near the dot
    offsets = dot_scatter.get_offsets()
    if len(offsets) == 0:
        return
    dx, dy = offsets[0]
    # Convert data coords to display coords for hit test
    disp_dot  = ax_main.transData.transform([dx, dy])
    disp_click = np.array([event.x, event.y])
    if np.linalg.norm(disp_dot - disp_click) < 15:
        state["dragging"] = True

def on_motion(event):
    if not state["dragging"]:
        return
    if event.inaxes != ax_main:
        return
    cfg   = MODE_CONFIG[state["mode"]]
    new_x = np.clip(event.xdata, cfg["x_min"], cfg["x_max"])
    state["dot_x"] = new_x
    # Only redraw dot + crosshairs + readout for performance
    fv = state["fixed_val"]
    dy = cfg["curve"](new_x, fv)
    if dy and dy > 0:
        dot_scatter.set_offsets([[new_x, dy]])
        dot_vline.set_xdata([new_x])
        dot_hline.set_ydata([dy])
        readout_text.set_text(cfg["dot_readout"](new_x, dy))
        fig.canvas.draw_idle()

def on_release(event):
    state["dragging"] = False

fig.canvas.mpl_connect("button_press_event",   on_press)
fig.canvas.mpl_connect("motion_notify_event",  on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

# ── Bottom hint ───────────────────────────────────────────────────────────────
fig.text(0.5, 0.005,
         "Click and drag the purple dot along the curve to explore values.  "
         "Type a new fixed value in the box to update the curve.",
         ha="center", fontsize=8, color="#888888", style="italic")

# ── Init ──────────────────────────────────────────────────────────────────────
draw()
plt.show()