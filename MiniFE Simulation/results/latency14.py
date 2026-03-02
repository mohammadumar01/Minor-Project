import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# =====================
# Data
# =====================
nodes = np.array([4,16,64,256,1024])
node_labels = [str(n) for n in nodes]

# allgather
allgather_mesh = np.array([3.817, 5.411, 8.036, 11.495, 18.572])
allgather_torus = np.array([3.817, 6.236, 9.137, 12.016, 17.705])
allgather_dfly = np.array([3.817, 5.211, 7.813, 10.857, 18.819])
allgather_fat= np.array( [3.768, 6.789, 9.746, 10.818, 14.694])

# =====================
# Plot styling (IEEE-like)
# =====================
plt.rcParams.update({
    'font.family': 'serif',
  'font.sans-serif': ['Arial'],
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'font.size': 10,
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300
})

fig, ax = plt.subplots(figsize=(3.5, 3.5))

# Plot lines with markers for barrier latency
ax.plot(nodes,allgather_mesh, 'o-', color="#68C0EC",linewidth=1.5, 
        markersize=5, label='Mesh',  markeredgewidth=0.5)
ax.plot(nodes, allgather_torus, 's-', color="#ff7f0e", linestyle='dashdot', linewidth=1.5, 
        markersize=5, label='Torus', markeredgewidth=0.5)
ax.plot(nodes, allgather_dfly, '^-', color="#2b8c52", linewidth=1.5, 
        markersize=5, label='Dragonfly',  markeredgewidth=0.5)
ax.plot(nodes,allgather_fat, 'D-', color="#F6BE00",linestyle='dashdot' ,linewidth=1.5, 
        markersize=5, label='Fattree',  markeredgewidth=0.5)

# Set x-axis to log scale for better visualization
ax.set_xscale('log')
ax.set_xlabel("Number of Nodes", fontsize=12)
ax.set_ylabel("Latency (µs)", fontsize=12)
ax.set_title("Allgather Latency", fontsize=12)

ax.set_xticks(nodes)
ax.set_xticklabels(node_labels)
ax.set_ylim(0, 20)
ax.set_yticks(np.arange(0, 21, 5))

# Add grid
ax.grid(True, alpha=0.99, linestyle='dotted')
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout(pad=0.3)
plt.savefig("allgather_latency_grouped.pdf", bbox_inches="tight", dpi=600)
plt.show()





