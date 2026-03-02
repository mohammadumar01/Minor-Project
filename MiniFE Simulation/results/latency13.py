import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# =====================
# Data
# =====================
nodes = np.array([4,16,64,256,1024])
node_labels = [str(n) for n in nodes]

# Bcast
bcast_mesh = np.array([0.440, 0.570, 0.570, 0.570, 0.570])
bcast_torus = np.array([0.440, 0.570, 0.570, 0.570, 1.893])
bcast_dfly = np.array([0.440, 0.570, 0.570, 0.570, 0.571])
bcast_fat= np.array( [0.440, 0.570, 0.570, 0.570, 0.570])

# =====================
# Plot styling (IEEE-like)
# =====================
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Arial'],
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'legend.fontsize': 9,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300
})

fig, ax = plt.subplots(figsize=(3.5, 3.5))

# Plot lines with markers for barrier latency
ax.plot(nodes, bcast_mesh, 'o-', color="#68C0EC",linewidth=1.5, 
        markersize=5, label='Mesh', markeredgewidth=0.5)
ax.plot(nodes, bcast_torus, 's-', color="#ff7f0e", linestyle='dashed', linewidth=1.5, 
        markersize=5, label='Torus', markeredgewidth=0.5)
ax.plot(nodes, bcast_dfly, '^-', color="#2b8c52", linewidth=1.5, 
        markersize=5, label='Dragonfly', markeredgewidth=0.5)
ax.plot(nodes, bcast_fat, 'D-', color="#F6BE00",linestyle='dashed' ,linewidth=1.5, 
        markersize=5, label='Fattree', markeredgewidth=0.5)

# Set x-axis to log scale for better visualization
ax.set_xscale('log')
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Latency (µs)", fontsize=12)
ax.set_title("Bcast Latency", fontsize=12)

ax.set_xticks(nodes)
ax.set_xticklabels(node_labels,)
ax.set_ylim(0.3, 2.2)
ax.set_yticks(np.arange(0.5, 2.3, 0.5))

# Add grid
ax.grid(True, alpha=0.99, linestyle='dotted')
ax.legend(loc='upper left', fontsize=8)

plt.tight_layout(pad=0.5)
plt.savefig("bcast_latency_lines.pdf", bbox_inches="tight", dpi=600)
plt.show()




