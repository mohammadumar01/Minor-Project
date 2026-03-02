import numpy as np
import csv

# Mesh size
DIM_X, DIM_Y = 16,16
size = DIM_X * DIM_Y

# Map ranks to (x,y) coordinates
rank_coords = {r: (r // DIM_Y, r % DIM_Y) for r in range(size)}

def manhattan(a, b):
    """Hop count in Mesh with +2 for injection/ejection"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + 2

def calculate_allpairs(size, rank_coords):
    """Calculate average hop count for all pairs"""
    hops, count = 0, 0
    for i in range(size):
        for j in range(size):
            if i != j:
                hops += manhattan(rank_coords[i], rank_coords[j])
                count += 1
    return hops / count if count > 0 else 0

def calculate_rooted(size, root, rank_coords):
    """Calculate average hop count from root to all other nodes"""
    hops, count = 0, 0
    for r in range(size):
        if r != root:
            hops += manhattan(rank_coords[root], rank_coords[r])
            count += 1
    return hops / count if count > 0 else 0

def calculate_barrier(size, rank_coords):
    """Calculate barrier hop count using dissemination algorithm"""
    total_hops = 0
    num_rounds = int(np.ceil(np.log2(size)))
    
    for r in range(num_rounds):
        round_hops = 0
        round_pairs = 0
        for i in range(size):
            partner = (i + (1 << r)) % size  # i + 2^r mod N
            if i != partner:  # Avoid self-communication
                round_hops += manhattan(rank_coords[i], rank_coords[partner])
                round_pairs += 1
        if round_pairs > 0:
            total_hops += round_hops / round_pairs  # Average for this round
    
    return total_hops

# Representative PingPong pairs 
rep_pairs = [
    (0, 1),   # nearest neighbor (distance 1 + 2 = 3 hops)
    (0, 15),   # same row, far end (distance 3 + 2 = 5 hops)
    (0, 240),  # same column, far end (distance 3 + 2 = 5 hops)
    (0, 255)   # farthest diagonal (distance 6 + 2 = 8 hops)
]

motifs = [
    {"pattern": "Allreduce", "size": size},
    {"pattern": "Bcast", "root": 0, "size": size},
    {"pattern": "Reduce", "root": 0, "size": size},
    {"pattern": "Allgather", "size": size},
    {"pattern": "Barrier", "size": size},
    {"pattern": "PingPong", "pairs": rep_pairs}
]

rows_avg = [["Pattern", "Ranks", "Avg HopCount"]]
hop_values = []

for motif in motifs:
    if motif["pattern"] in ["Allreduce", "Allgather"]:
        avg = calculate_allpairs(motif["size"], rank_coords)
        rows_avg.append([motif["pattern"], motif["size"], round(avg, 2)])
        hop_values.append(avg)

    elif motif["pattern"] == "Barrier":
        avg = calculate_barrier(motif["size"], rank_coords)
        rows_avg.append([motif["pattern"], motif["size"], round(avg, 2)])
        hop_values.append(avg)

    elif motif["pattern"] in ["Bcast", "Reduce"]:
        avg = calculate_rooted(motif["size"], motif["root"], rank_coords)
        rows_avg.append([f"{motif['pattern']} root={motif['root']}", motif["size"], round(avg, 2)])
        hop_values.append(avg)

    elif motif["pattern"] == "PingPong":
        for a, b in motif["pairs"]:
            hops = manhattan(rank_coords[a], rank_coords[b])
            rows_avg.append([f"PingPong {a}-{b}", 2, hops])
            hop_values.append(hops)

# Overall average
overall = sum(hop_values) / len(hop_values) if hop_values else 0
rows_avg.append(["Overall", "-", round(overall, 2)])

# Print summary
print("Mesh Topology Hop Count Summary ")
print("Note: +2 hops included for injection/ejection latency")
print("-" * 45)
for row in rows_avg:
    print(f"{row[0]:<20} {str(row[1]):<5} {row[2]}")

# Additional analysis
print(f"\nDetailed hop count examples:")
for a, b in rep_pairs:
    x1, y1 = rank_coords[a]
    x2, y2 = rank_coords[b]
    hops = manhattan(rank_coords[a], rank_coords[b])
    network_hops = hops - 2  # Subtract injection/ejection
    print(f"Rank {a} ({x1},{y1}) → Rank {b} ({x2},{y2}): {network_hops} network + 2 injection/ejection = {hops} total")