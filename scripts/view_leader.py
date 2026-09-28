"""Live 1D readout of each SO101 leader joint position.

Usage: uv run scripts/view_leader.py COM4
Each row is one joint on its own raw-position scale, which grows to fit the min and max
seen since launch. The dot is the current position, the shaded band is the range swept.
Close the window to stop.
"""

import sys

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

SURFACE, INK, INK_2, GRID, BLUE, BLUE_BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#e1e0d9", "#2a78d6", "#cde2f7"
MIN_SPAN = 100  # keep a still joint from zooming in on sensor noise
PAD = 0.05

port = sys.argv[1] if len(sys.argv) > 1 else "COM4"
names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
motors = {name: Motor(i, "sts3215", MotorNormMode.RANGE_M100_100) for i, name in enumerate(names, start=1)}
bus = FeetechMotorsBus(port=port, motors=motors)
bus.connect()  # handshake: fails fast if any motor is missing

first = bus.sync_read("Present_Position", normalize=False)
seen_min = dict(first)
seen_max = dict(first)

fig, axes = plt.subplots(len(names), 1, figsize=(9, 5), facecolor=SURFACE)
fig.canvas.manager.set_window_title(f"SO101 leader - {port}")
fig.subplots_adjust(left=0.2, right=0.88, top=0.95, bottom=0.05, hspace=1.2)

rows = {}
for i, (name, ax) in enumerate(zip(names, axes), start=1):
    ax.set_facecolor(SURFACE)
    ax.set_ylim(-1, 1)
    ax.set_yticks([0], [f"{i}  {name}"])
    ax.tick_params(colors=INK_2, length=0, labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    track = ax.axhline(0, color=GRID, linewidth=2, solid_capstyle="round", zorder=1)
    band = ax.plot([], [], color=BLUE_BAND, linewidth=8, solid_capstyle="round", zorder=2)[0]
    dot = ax.scatter([first[name]], [0], s=110, color=BLUE, edgecolors=SURFACE, linewidths=2, zorder=3, clip_on=False)
    value = ax.text(1.02, 0, "", transform=ax.get_yaxis_transform(), va="center", ha="left",
                    color=INK, fontsize=10, family="monospace")
    rows[name] = (ax, band, dot, value)


def update(_):
    pos = bus.sync_read("Present_Position", normalize=False)
    for name, (ax, band, dot, value) in rows.items():
        p = pos[name]
        lo, hi = seen_min[name], seen_max[name] = min(seen_min[name], p), max(seen_max[name], p)
        span = max(hi - lo, MIN_SPAN)
        mid = (lo + hi) / 2
        ax.set_xlim(mid - span * (0.5 + PAD), mid + span * (0.5 + PAD))
        ax.set_xticks([lo, hi] if hi > lo else [lo])
        band.set_data([lo, hi], [0, 0])
        dot.set_offsets([[p, 0]])
        value.set_text(f"{p:>5}")


anim = FuncAnimation(fig, update, interval=50, cache_frame_data=False)
try:
    plt.show()
finally:
    bus.disconnect(disable_torque=False)
