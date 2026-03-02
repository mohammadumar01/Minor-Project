import numpy as np
import csv

# Torus size
DIM_X, DIM_Y = 16, 16
size = DIM_X * DIM_Y 

# Map ranks to (x,y) coordinates
rank_coords = {r: (r // DIM_Y, r % DIM_Y) for r in range(size)}

def torus_distance(a, b, dims=(DIM_X, DIM_Y)):
    """Hop count in Torus with wrap-around +2 for injection/ejection"""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    # wrap-around distance
    dx = min(dx, dims[0] - dx)
    dy = min(dy, dims[1] - dy)
    return dx + dy + 2

def calculate_allpairs(size, rank_coords):
    """Calculate average hop count for all pairs"""
    hops, count = 0, 0
    for i in range(size):
        for j in range(size):
            if i != j:
                hops += torus_distance(rank_coords[i], rank_coords[j])
                count += 1
    return hops / count if count > 0 else 0

def calculate_rooted(size, root, rank_coords):
    """Calculate average hop count from root to all other nodes"""
    hops, count = 0, 0
    for r in range(size):
        if r != root:
            hops += torus_distance(rank_coords[root], rank_coords[r])
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
                round_hops += torus_distance(rank_coords[i], rank_coords[partner])
                round_pairs += 1
        if round_pairs > 0:
            total_hops += round_hops / round_pairs  # Average for this round
    
    return total_hops

# Representative PingPong pairs 
rep_pairs = [
    (0, 1),  # nearest neighbor
    (0, 15),  # same row, far end
    (0, 240), # same column, far end
    (0, 255)   # farthest diagonal
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
            hops = torus_distance(rank_coords[a], rank_coords[b])
            rows_avg.append([f"PingPong {a}-{b}", 2, hops])
            hop_values.append(hops)

# Overall average
overall = sum(hop_values) / len(hop_values) if hop_values else 0
rows_avg.append(["Overall", "-", round(overall, 2)])

# Write to CSV
with open("torus16x16_hopcount_summary.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows_avg)

# Print summary
print("Torus Topology Hop Count Summary (2×2)")
print("Note: +2 hops included for injection/ejection latency")
print("-" * 45)
for row in rows_avg:
    print(f"{row[0]:<20} {str(row[1]):<5} {row[2]}")

