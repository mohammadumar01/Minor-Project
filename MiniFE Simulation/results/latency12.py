import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# =====================
# Data
# =====================
nodes = np.array([4,16,64,256,1024])
node_labels = [str(n) for n in nodes]

# Allreduce
allreduce_mesh = np.array([3.761, 7.806, 13.109, 21.817, 36.855])
allreduce_torus = np.array([3.761, 7.806, 12.946, 20.931, 34.265])
allreduce_dfly = np.array([3.761, 7.975, 12.025, 16.437, 20.975])
allreduce_fat= np.array([3.761, 8.491, 13.224, 17.270, 22.154])

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
ax.plot(nodes, allreduce_mesh, 'o-', color="#68C0EC",linewidth=1.5, 
        markersize=5, label='Mesh',markeredgewidth=0.5)
ax.plot(nodes, allreduce_torus, 's-', color="#ff7f0e", linestyle='dashdot', linewidth=1.5, 
        markersize=5, label='Torus',markeredgewidth=0.5)
ax.plot(nodes, allreduce_dfly, '^-', color="#2b8c52", linewidth=1.5, 
        markersize=5, label='Dragonfly',  markeredgewidth=0.5)
ax.plot(nodes,allreduce_fat, 'D-', color="#F6BE00",linestyle='dashdot' ,linewidth=1.5, 
        markersize=5, label='Fattree', markeredgewidth=0.5)

# Set x-axis to log scale for better visualization
ax.set_xscale('log')
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Latency (µs)", fontsize=12)
ax.set_title("Allreduce Latency", fontsize=12)

ax.set_xticks(nodes)
ax.set_xticklabels(node_labels)
ax.set_ylim(0, 40)
ax.set_yticks(np.arange(0, 41, 10))

# Add grid
ax.grid(True, alpha=0.999, linestyle='dotted')
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout(pad=0.5)
plt.savefig("allreduce_latency_grouped2.pdf", bbox_inches="tight", dpi=600)
plt.show()





