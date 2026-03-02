import csv
import math
import numpy as np

topology = "mesh"              
mesh_shape = (2, 2, 4)       
X, Y, Z = mesh_shape
num_ranks = X * Y * Z

#Neighbor offsets: full 26 neighbors (faces + edges + corners)
neighbor_offsets = [
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if not (dx == 0 and dy == 0 and dz == 0)
]

#Rank <-> Coordinate mapping 
def rank_to_coords(rank):
    """x changes fastest, then y, then z"""
    x = rank % X
    y = (rank // X) % Y
    z = rank // (X * Y)
    return (x, y, z)

def coords_to_rank(x, y, z):
    return x + y * X + z * (X * Y)

# hop calculation (Manhattan, +2 for inj/eject)
def mesh_distance_coords(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

def hop_count(rank_a, rank_b):
    a = rank_to_coords(rank_a)
    b = rank_to_coords(rank_b)
    d = mesh_distance_coords(a, b)   # no wraparound for mesh
    return d + 2                     # +2 for injection + ejection latency

# Neighbor generation for mesh (inside-bounds only) with unique unordered pairs 
def get_neighbors_mesh_unique(offset):
    dx, dy, dz = offset
    pairs = []
    seen = set()  # store (min_rank, max_rank) to avoid reverse duplicates
    for r in range(num_ranks):
        x, y, z = rank_to_coords(r)
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < X and 0 <= ny < Y and 0 <= nz < Z:
            nr = coords_to_rank(nx, ny, nz)
            if nr != r:
                key = (min(r, nr), max(r, nr))
                if key not in seen:
                    pairs.append((r, nr))
                    seen.add(key)
    return pairs

# Collectives
def average_pairwise_hops_unique(size):
    """Average hop count across unique unordered pairs (i < j)."""
    total, count = 0, 0
    for i in range(size):
        for j in range(i + 1, size):
            total += hop_count(i, j)
            count += 1
    return total / count if count > 0 else 0.0

def barrier_hops(size):
    """Barrier model: rounds r = 0..ceil(log2(N)-1); partner = (i + 2^r) % N"""
    total = 0.0
    rounds = int(math.ceil(math.log2(size)))
    for r in range(rounds):
        step = 1 << r
        round_sum = 0
        round_count = 0
        for i in range(size):
            partner = (i + step) % size
            if partner != i:
                round_sum += hop_count(i, partner)
                round_count += 1
        if round_count > 0:
            total += (round_sum / round_count)
    return total


def main():
    csv_file = "mesh_2x2x4_hop_counts.csv"
    summary_rows = [["Pattern", "Ranks", "Pairs", "Avg_Hop_Count"]]
    allpingpong_info = []

    with open(csv_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Pattern", "Topology", "Offset", "Rank_A", "Coord_A", "Rank_B", "Coord_B", "Hop_Count"])

        # Per-offset AllPingPong (full 26 offsets)
        for idx, offset in enumerate(neighbor_offsets):
            pairs = get_neighbors_mesh_unique(offset)
            hops_list = []
            for (a, b) in pairs:
                hops = hop_count(a, b)
                ca = rank_to_coords(a)
                cb = rank_to_coords(b)
                writer.writerow([f"AllPingPong Neighbor{idx+1}", topology, offset, a, ca, b, cb, hops])
                hops_list.append(hops)

            avg_hops = float(np.mean(hops_list)) if hops_list else 0.0
            allpingpong_info.append({"pattern": f"AllPingPong Neighbor{idx+1}", "num_pairs": len(pairs), "avg_hops": avg_hops})
            summary_rows.append([f"AllPingPong Neighbor{idx+1} (offset {offset})", num_ranks, len(pairs), round(avg_hops, 3)])

        # Allreduce (unique unordered pairs)
        allreduce_avg = average_pairwise_hops_unique(num_ranks)
        writer.writerow(["Allreduce", topology, "-", "-", "-", "-", "-", round(allreduce_avg, 3)])
        summary_rows.append(["Allreduce", num_ranks, "-", round(allreduce_avg, 3)])

        # Barrier
        barrier_avg = barrier_hops(num_ranks)
        writer.writerow(["Barrier", topology, "-", "-", "-", "-", "-", round(barrier_avg, 3)])
        summary_rows.append(["Barrier", num_ranks, "-", round(barrier_avg, 3)])

        # summary block at end of CSV
        writer.writerow([])
        writer.writerow(["Summary Pattern", "Ranks", "Pairs", "Avg_Hop_Count"])
        for s in summary_rows:
            writer.writerow(s)

    # Overall weighted average (AllPingPong weighted by number of pairs; collectives weighted per-rank)
    total_pair_weight = sum(m["num_pairs"] for m in allpingpong_info)
    weighted_sum = sum(m["avg_hops"] * m["num_pairs"] for m in allpingpong_info)
    weighted_sum += allreduce_avg * num_ranks
    weighted_sum += barrier_avg * num_ranks
    total_pair_weight += 2 * num_ranks  # collectives contribution (Allreduce + Barrier)
    overall_avg = (weighted_sum / total_pair_weight) if total_pair_weight > 0 else 0.0

  
    print("MiniMD Mesh 2x2x4 Hop Count Summary:")
    for row in summary_rows:
        print(f"{row[0]:<50} {row[1]:<5}  {row[2]:<5}  {row[3]}")
    print(f"\nOverall Average (weighted): {round(overall_avg, 3)}")

if __name__ == "__main__":
    main()
