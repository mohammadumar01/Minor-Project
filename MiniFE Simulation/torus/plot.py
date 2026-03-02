import matplotlib.pyplot as plt
import numpy as np

# X-axis labels
communication_patterns = ["Allreduce", "Bcast", "Reduce", "Allgather", "Barrier", "Pingpong\nOf 4 pairs"]

# Torus sizes
torus_sizes = ["Torus2x2", "Torus4x4", "Torus8x8", "Torus16x16", "Torus32x32"]

# Correct average hop counts (rows=comm patterns, cols=torus sizes)
average_hop_counts = [
    [3, 4, 6, 10, 18],   # Allreduce
    [3, 4, 6, 10, 18],   # Bcast
    [3, 4, 6, 10, 18],   # Reduce
    [3, 4, 6, 10, 18],   # Allgather
    [3, 6, 14, 18, 22],  # Barrier
    [3, 3, 3, 3, 3],     # Pingpong
]

average_hop_counts = np.array(average_hop_counts)

# Bar positions
x = np.arange(len(communication_patterns))
width = 0.15

# Colors chosen similar to your original figure
colors = ['#5DADE2', '#F39C12', '#E67E22', '#95A5A6', '#F4D03F']

fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars
for i, (torus, color) in enumerate(zip(torus_sizes, colors)):
    ax.bar(x + i * width, average_hop_counts[:, i], width, label=torus, color=color, edgecolor='black')

# Labels
ax.set_xlabel("Communication Pattern", fontsize=12)
ax.set_ylabel("Average Hop Count", fontsize=12)
ax.set_title("MiniFE Average Hopcount across Torus Topologies", fontsize=14, fontweight='bold')

# X-axis ticks
ax.set_xticks(x + width * 2)
ax.set_xticklabels(communication_patterns, fontsize=11)

# Y-axis range
ax.set_ylim(0, 25)

# Grid for readability
ax.grid(axis='y', linestyle='--', alpha=0.6)

# Legend
ax.legend(title="Topology", fontsize=10)

plt.tight_layout()

# Save in multiple formats for publication
plt.savefig("MiniFE_Torus_Hopcount.pdf")   # Vector for journals
plt.savefig("MiniFE_Torus_Hopcount.png", dpi=300)  # High-quality PNG

plt.show()
