import matplotlib.pyplot as plt
import numpy as np

# =====================
# Styling (IEEE-like)
# =====================
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'font.size': 10,
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300
})

# =====================
# Data
# =====================
node_sizes = [16, 32, 64, 128, 256, 512, 1024]
node_labels = ['16', '32', '64', '128', '256', '512', '1024']

# Mesh latencies
mesh_data = np.array([
    [11.063, 10.879, 11.063, 10.879, 11.063, 11.431, 11.063], # Allpingpong X
    [2.078, 2.017, 2.078, 2.017, 2.078, 2.201, 2.078],         # Allpingpong Y 
    [11.063, 10.879, 11.063, 10.879, 18.572, 11.431, 11.063],  # Allpingpong Z
    [2.078, 2.017, 2.078, 2.017, 36.960, 2.201, 2.078],        # Allpingpong diagonal
])

# Torus latencies
torus_data = np.array([
    [11.125, 10.879, 11.125, 10.925, 11.125, 11.525, 11.063], # Allpingpong X
    [2.099, 2.017, 2.099, 2.032, 2.099, 2.232, 2.078],        # Allpingpong Y 
    [11.125, 10.879, 11.125, 10.925, 11.125, 11.525, 11.063], # Allpingpong Z
    [2.099, 2.017, 2.099, 2.032, 2.099, 2.232, 2.078],        # Allpingpong diagonal
])

patterns = ["X-dir", "Y-dir", "Z-dir", "Diagonal"]

# =====================
# Plot setup
# =====================
fig, ax = plt.subplots(figsize=(3.5, 2.5))

x = np.arange(len(node_sizes))
bar_width = 0.15
spacing = 0.04

colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"]  # one color per pattern

# Plot grouped bars
for i, pattern in enumerate(patterns):
    offset = (i - 1.5) * (bar_width + spacing)  # center around ticks

    # Mesh
    ax.bar(x + offset, mesh_data[i], width=bar_width, 
           color=colors[i], edgecolor="black", linewidth=0.7,
           label=f"Mesh3D {pattern}" if i == 0 else "")

    # Torus
    ax.bar(x + offset + bar_width/2, torus_data[i], width=bar_width, 
           color="white", edgecolor=colors[i], linewidth=1.2, hatch="///",
           label=f"Torus3D {pattern}" if i == 0 else "")

# =====================
# Labels & Formatting
# =====================
ax.set_xlabel("Number of Nodes", fontsize=10, fontweight="bold")
ax.set_ylabel("Latency (µs)", fontsize=10, fontweight="bold")
ax.set_title("Allpingpong Latency: Mesh3D vs Torus3D", fontsize=10, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(node_labels, fontweight="bold")

ax.set_ylim(0, 40)
ax.grid(axis="y", linestyle="--", alpha=0.5)

# Legend: show Mesh vs Torus styles only once
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#1f77b4", edgecolor="black", label="Mesh3D (X/Y/Z/Diagonal)"),
    Patch(facecolor="white", edgecolor="black", hatch="///", label="Torus3D (X/Y/Z/Diagonal)"),
]
ax.legend(handles=legend_elements, loc="upper left", frameon=False, fontsize=8)

plt.tight_layout()
plt.savefig("Allpingpong_latency_grouped.pdf", bbox_inches="tight", dpi=600)
plt.show()
