import csv
import numpy as np

def parse_fattree_shape(shape_str):
    """Parse FatTree shape string into pod structure"""
    levels = shape_str.split(':')
    downlinks = []
    for level in levels:
        parts = level.split(',')
        downlinks.append(int(parts[0]))
    
    #for fattree shape "2,2:2,2:4" downlinks = [2, 2,4]
    pods = downlinks[-1]           # 4 pods
    hosts_per_pod = downlinks[0] * downlinks[1]   # 2*2=4 hosts per pod
    return pods, hosts_per_pod, downlinks

def fattree_hops(src, dst, downlinks):
    """Compute hop count in FatTree topology"""
    hosts_per_pod = downlinks[0] * downlinks[1]
    
    pod_src = src // hosts_per_pod
    pod_dst = dst // hosts_per_pod
    
    edge_src = (src % hosts_per_pod) // downlinks[0]
    edge_dst = (dst % hosts_per_pod) // downlinks[0]
    
    if pod_src == pod_dst:
        if edge_src == edge_dst:
            return 3  # Same edge switch
        else:
            return 5  # Same pod, different edge
    else:
        return 7      # Different pods

# Parse FatTree shape
shape_str = "2,2:2,2:4"
pods, hosts_per_pod, downlinks = parse_fattree_shape(shape_str)
total_hosts = pods * hosts_per_pod  # 16 hosts

print(f"FatTree Configuration: {pods} pods, {hosts_per_pod} hosts per pod, {total_hosts} total hosts")

# MPI job motifs
motifs = [
    {"pattern": "Allreduce", "iterations": 92, "size": total_hosts},
    {"pattern": "Bcast", "root": 0, "iterations": 2, "size": total_hosts},
    {"pattern": "Reduce", "root": 0, "iterations": 2, "size": total_hosts},
    {"pattern": "Allgather", "iterations": 3, "size": total_hosts},
    {"pattern": "Barrier", "iterations": 99, "size": total_hosts},
    {"pattern": "PingPong", "pairs": [(0,1), (0,2), (0,4),(0,6),(0,8),(0,12)], "iterations": 105}
]

rows_avg = [["Pattern", "Ranks", "Avg HopCount"]]
hop_values = []

for motif in motifs:
    if motif["pattern"] in ["Allreduce", "Allgather"]:
        size = motif["size"]
        total_hops = 0
        pairs = 0
        
        for i in range(size):
            for j in range(size):
                if i != j:
                    total_hops += fattree_hops(i, j, downlinks)
                    pairs += 1
        
        avg = total_hops / pairs if pairs > 0 else 0
        rows_avg.append([motif["pattern"], size, round(avg, 2)])
        hop_values.extend([fattree_hops(i, j, downlinks) for i in range(size) for j in range(size) if i != j])
    
    elif motif["pattern"] == "Barrier":
        #  dissemination barrier model 
        size = motif["size"]
        total_hops = 0
        num_rounds = int(np.ceil(np.log2(size)))
        
        for r in range(num_rounds):
            round_hops = 0
            round_pairs = 0
            for i in range(size):
                partner = (i + (1 << r)) % size  # i + 2^r mod N
                if i != partner:  # Avoid self-communication
                    round_hops += fattree_hops(i, partner, downlinks)
                    round_pairs += 1
            if round_pairs > 0:
                total_hops += round_hops / round_pairs  # Average for this round
        
        avg = total_hops
        rows_avg.append([motif["pattern"], size, round(avg, 2)])
        hop_values.append(avg)
    
    elif motif["pattern"] in ["Bcast", "Reduce"]:
        root = motif["root"]
        size = motif["size"]
        total_hops = 0
        
        for r in range(size):
            if r != root:
                total_hops += fattree_hops(root, r, downlinks)
        
        avg = total_hops / (size - 1) if size > 1 else 0
        rows_avg.append([f"{motif['pattern']} root={root}", size, round(avg, 2)])
        hop_values.extend([fattree_hops(root, r, downlinks) for r in range(size) if r != root])
    
    elif motif["pattern"] == "PingPong":
        for a, b in motif["pairs"]:
            hops = fattree_hops(a, b, downlinks)
            rows_avg.append([f"PingPong {a}-{b}", 2, hops])
            hop_values.append(hops)

# Overall average
overall = sum(hop_values) / len(hop_values) if hop_values else 0
rows_avg.append(["Overall", "-", round(overall, 2)])

# Print summary
print("\nHop Count per Pattern:")
for row in rows_avg:
    print(f"{row[0]:<20} {str(row[1]):<5} {row[2]}")



# Show barrier details
print(f"\nBarrier implementation: Dissemination barrier with {int(np.ceil(np.log2(total_hosts)))} rounds")
print("Each round represents a communication pattern where ranks exchange with partners at distance 2^r")