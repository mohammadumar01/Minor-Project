import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# =====================
# Data
# =====================
nodes = np.array([4,16,64,256,1024])
node_labels = [str(n) for n in nodes]

# allgather
barrier_mesh = np.array([3.753, 7.815, 13.146, 21.895, 36.960])
barrier_torus = np.array([3.753, 7.797, 12.937, 20.929, 34.266])
barrier_dfly = np.array([3.753, 7.997, 12.033, 16.438, 20.965])
barrier_fat= np.array([3.753, 8.483, 13.212, 17.291, 22.156])

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
ax.plot(nodes,barrier_mesh, 'o-', color="#68C0EC",linewidth=1.5, 
        markersize=5, label='Mesh', markeredgewidth=0.5)
ax.plot(nodes, barrier_torus, 's-', color="#ff7f0e", linestyle='dashdot', linewidth=1.5, 
        markersize=5, label='Torus', markeredgewidth=0.5)
ax.plot(nodes, barrier_dfly, '^-', color="#2b8c52", linewidth=1.5, 
        markersize=5, label='Dragonfly',markeredgewidth=0.5)
ax.plot(nodes,barrier_fat, 'D-', color="#F6BE00",linestyle='dashdot' ,linewidth=1.5, 
        markersize=5, label='Fattree',  markeredgewidth=0.5)

# Set x-axis to log scale for better visualization
ax.set_xscale('log')
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Latency (µs)", fontsize=12)
ax.set_title("Barrier Latency", fontsize=12)

ax.set_xticks(nodes)
ax.set_xticklabels(node_labels)
ax.set_ylim(0, 40)

# Add grid
ax.grid(True, alpha=0.999, linestyle='dotted')
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout(pad=0.5)
plt.savefig("barrier_latency_grouped.pdf", bbox_inches="tight", dpi=600)
plt.show()





