import csv
import numpy as np
import math

#Mesh configuration
topology = "mesh"
mesh_shape = (8,8,4)  
X, Y, Z = mesh_shape
num_ranks = X * Y * Z


# Rank <-> Coordinate mapping 
def rank_to_coords(rank):
    x = rank % X
    y = (rank // X) % Y
    z = rank // (X * Y)
    return (x, y, z)

def coords_to_rank(x, y, z):
    return x + y * X + z * (X * Y)

# Manhattan hops + injection/ejection
def manhattan_with_latency(rank_a, rank_b):
    a = rank_to_coords(rank_a)
    b = rank_to_coords(rank_b)
    dist = abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])
    return dist + 2  # +2 for injection/ejection

# 26-neighbor offsets (faces + edges + corners)
neighbor_offsets = [
    (dx, dy, dz)
    for dx in (-1,0,1)
    for dy in (-1,0,1)
    for dz in (-1,0,1)
    if not (dx==0 and dy==0 and dz==0)
]

#  Neighbor generation (unique unordered pairs) 
def get_neighbors_mesh_unique(offset):
    dx, dy, dz = offset
    pairs = []
    seen = set()
    for rank in range(num_ranks):
        x, y, z = rank_to_coords(rank)
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < X and 0 <= ny < Y and 0 <= nz < Z:
            neighbor_rank = coords_to_rank(nx, ny, nz)
            key = (min(rank, neighbor_rank), max(rank, neighbor_rank))
            if key not in seen:
                pairs.append((key[0], key[1]))
                seen.add(key)
    return pairs

#  Collectives (average hops)
def average_pairwise_hops(size):
    total, count = 0, 0
    for i in range(size):
        for j in range(i+1, size):
            total += manhattan_with_latency(i,j)
            count += 1
    return total / count if count>0 else 0

def barrier_hops(size):
    total = 0.0
    rounds = int(math.ceil(math.log2(size)))
    for r in range(rounds):
        step = 1<<r
        round_sum = 0
        round_count = 0
        for i in range(size):
            partner = (i+step)%size
            if partner!=i:
                round_sum += manhattan_with_latency(i, partner)
                round_count += 1
        if round_count>0:
            total += (round_sum/round_count)
    return total


def main():
    csv_file = "mesh256_hop_counts.csv"
    summary_rows = [["Pattern","Ranks","Pairs","Avg_Hop_Count"]]

    allpingpong_averages = []

    with open(csv_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Pattern","Topology","Offset","Rank_A","Coord_A","Rank_B","Coord_B","Hop_Count"])

        for idx, offset in enumerate(neighbor_offsets, start=1):
            pairs = get_neighbors_mesh_unique(offset)
            hops_list = []
            for a,b in pairs:
                hops = manhattan_with_latency(a,b)
                ca, cb = rank_to_coords(a), rank_to_coords(b)
                writer.writerow([f"AllPingPong Neighbor{idx}",topology,offset,a,ca,b,cb,hops])
                hops_list.append(hops)
            avg_hops = float(np.mean(hops_list)) if hops_list else 0.0
            allpingpong_averages.append({"pattern":f"AllPingPong Neighbor{idx}","num_pairs":len(pairs),"avg_hops":avg_hops})
            summary_rows.append([f"AllPingPong Neighbor{idx} (offset {offset})", num_ranks, len(pairs), round(avg_hops,3)])

        # Allreduce
        allreduce_avg = average_pairwise_hops(num_ranks)
        writer.writerow(["Allreduce",topology,"-","-","-","-","-",round(allreduce_avg,3)])
        summary_rows.append(["Allreduce",num_ranks,"-",round(allreduce_avg,3)])

        # Barrier
        barrier_avg = barrier_hops(num_ranks)
        writer.writerow(["Barrier",topology,"-","-","-","-","-",round(barrier_avg,3)])
        summary_rows.append(["Barrier",num_ranks,"-",round(barrier_avg,3)])

    # Overall weighted average
    total_weight = sum(m["num_pairs"] for m in allpingpong_averages) + 2*num_ranks*2
    weighted_sum = sum(m["avg_hops"]*m["num_pairs"] for m in allpingpong_averages) + allreduce_avg*num_ranks + barrier_avg*num_ranks
    overall_avg = weighted_sum/total_weight
    summary_rows.append(["Overall Average","-","-",round(overall_avg,3)])

    # Print summary
    print(f"MiniMD Mesh256 (8x8x4) Hop Count Summary:")
    for row in summary_rows:
        print(f"{row[0]:<50} {row[1]:<5}  {row[2]:<5}  {row[3]}")

if __name__=="__main__":
    main()
