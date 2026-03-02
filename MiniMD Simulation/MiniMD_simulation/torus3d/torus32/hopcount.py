import numpy as np
import csv

# Topology Configuration
torus_shape = (4, 4, 2)   
X, Y, Z = torus_shape
num_ranks = X * Y * Z  

# Map rank -> (x, y, z)
def rank_to_coords(rank):
    x = rank % X
    y = (rank // X) % Y
    z = rank // (X * Y)
    return (x, y, z)

# Map coordinates -> rank
def coords_to_rank(x, y, z):
   return x + y * X + z * (X * Y)

# 3D Torus shortest path hops with wraparound
def torus_distance(a, b):
    dist_x = min(abs(a[0] - b[0]), X - abs(a[0] - b[0]))
    dist_y = min(abs(a[1] - b[1]), Y - abs(a[1] - b[1]))
    dist_z = min(abs(a[2] - b[2]), Z - abs(a[2] - b[2]))
    return dist_x + dist_y + dist_z

# Total hop count including injection/ejection
def hop_count(rank_a, rank_b):
    return torus_distance(rank_to_coords(rank_a), rank_to_coords(rank_b)) + 2

# Get neighbor pairs for an offset (torus wraparound only)
def get_neighbors_for_offset(offset):
    dx, dy, dz = offset
    pairs = []
    seen = set()
    for rank in range(num_ranks):
        x, y, z = rank_to_coords(rank)
        nx = (x + dx) % X
        ny = (y + dy) % Y
        nz = (z + dz) % Z
        neighbor_rank = coords_to_rank(nx, ny, nz)
        if neighbor_rank != rank:
            if (neighbor_rank, rank) not in seen:  # avoid duplicate reverse pairs
                pairs.append((rank, neighbor_rank))
                seen.add((rank, neighbor_rank))
    return pairs

# Average hop count for all unique pairs (Allreduce model)
def average_pairwise_hops(size):
    total_hops, count = 0, 0
    for i in range(size):
        for j in range(i + 1, size):
            total_hops += hop_count(i, j)
            count += 1
    return total_hops / count if count > 0 else 0

# Barrier hop count model 
def barrier_hops(size):
    total_hops = 0
    num_rounds = int(np.ceil(np.log2(size)))
    for r in range(num_rounds):
        round_hops, round_pairs = 0, 0
        step = 1 << r
        for i in range(size):
            partner = (i + step) % size
            if i != partner:
                round_hops += hop_count(i, partner)
                round_pairs += 1
        if round_pairs > 0:
            total_hops += round_hops / round_pairs
    return total_hops

def main():
    neighbor_offsets = [
        (dx, dy, dz)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        for dz in (-1, 0, 1)
        if not (dx == 0 and dy == 0 and dz == 0)
    ]

    print(f"Calculating hop counts for 3D Torus {torus_shape}...\n")

    summary_rows = [["Pattern", "Ranks", "Pairs", "Avg Hop Count"]]

    # CSV output setup
    csv_file = "torus32_hop_counts.csv"
    with open(csv_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Pattern", "Offset", "Rank_A", "Coord_A", "Rank_B", "Coord_B", "Hop_Count"])

        # AllPingPong patterns for each offset
        for idx, offset in enumerate(neighbor_offsets):
            pairs = get_neighbors_for_offset(offset)
            hops_list = [hop_count(a, b) for (a, b) in pairs]
            avg_hops = round(np.mean(hops_list), 3) if hops_list else 0
            summary_rows.append([f"Allpingpong Neighbor{idx+1} (offset {offset})", 
                                 num_ranks, len(pairs), avg_hops])

            # print(f"\n--- Neighbor{idx+1} (offset {offset}) ---")
            for (a, b) in pairs:
                ca, cb = rank_to_coords(a), rank_to_coords(b)
                hops = hop_count(a, b)
                # print(f"Rank {a} {ca}  <->  Rank {b} {cb}   (hops={hops})")
                writer.writerow([f"Allpingpong Neighbor{idx+1}", offset, a, ca, b, cb, hops])

        # Allreduce 
        allreduce_avg = average_pairwise_hops(num_ranks)
        summary_rows.append(["Allreduce", num_ranks, "-", round(allreduce_avg, 3)])
        writer.writerow(["Allreduce", "-", "-", "-", "-", "-", round(allreduce_avg, 3)])

        # Barrier 
        barrier_avg = barrier_hops(num_ranks)
        summary_rows.append(["Barrier", num_ranks, "-", round(barrier_avg, 3)])
        writer.writerow(["Barrier", "-", "-", "-", "-", "-", round(barrier_avg, 3)])

    # Print summary
    print("\n\nMiniMD 3D Torus Hop Count Summary:")
    for row in summary_rows:
        print(f"{row[0]:<50} {row[1]:<5}  {row[2]:<5}  {row[3]}")


if __name__ == "__main__":
    main()


