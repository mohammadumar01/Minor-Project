import csv
import numpy as np
from collections import Counter

def dragonfly_hops(src, dst, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    """Compute hop count in Dragonfly topology with injection/ejection"""
    nodes_per_group = routers_per_group * hosts_per_router

    g1 = src // nodes_per_group
    g2 = dst // nodes_per_group
    r1 = (src % nodes_per_group) // hosts_per_router
    r2 = (dst % nodes_per_group) // hosts_per_router

    # Same router (add +2 for injection/ejection)
    if g1 == g2 and r1 == r2:
        return 2  # host → router (injection) → router → host (ejection)
    
    # Same group, different router (add +2 for injection/ejection)
    elif g1 == g2:
        return 3 # host → router (injection) → router → router → host (ejection)
    
    # Different groups (add +2 for injection/ejection)
    else:
        # Check if routers are directly connected
        groups_per_router = max(1, num_groups // intergroup_links)
        connected_groups = set()
        for link in range(intergroup_links): 
            target_group = (g1 + link * groups_per_router + 1) % num_groups
            connected_groups.add(target_group)
        
        if g2 in connected_groups:
            return 4  # host → router (injection) → router → router → router → host (ejection)
        else:
            return 5  # host → router (injection) → router → router → router → router → host (ejection)

def calculate_allpairs(size, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    """Calculate average hop count for all pairs with injection/ejection"""
    hops, count = 0, 0
    for i in range(size):
        for j in range(size):
            if i != j:
                h = dragonfly_hops(i, j, num_groups, routers_per_group, hosts_per_router, intergroup_links)
                hops += h
                count += 1
    return hops / count if count > 0 else 0

def calculate_rooted(size, root, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    """Calculate average hop count from root to all other nodes with injection/ejection"""
    hops, count = 0, 0
    for r in range(size):
        if r != root:
            h = dragonfly_hops(root, r, num_groups, routers_per_group, hosts_per_router, intergroup_links)
            hops += h
            count += 1
    return hops / count if count > 0 else 0

def calculate_barrier(size, num_groups, routers_per_group, hosts_per_router, intergroup_links):
    """Calculate barrier hop count using dissemination algorithm"""
    total_hops = 0
    num_rounds = int(np.ceil(np.log2(size)))
    
    for r in range(num_rounds):
        round_hops = 0
        round_pairs = 0
        for i in range(size):
            partner = (i + (1 << r)) % size  # i + 2^r mod N
            if i != partner:  # Avoid self-communication
                h = dragonfly_hops(i, partner, num_groups, routers_per_group, hosts_per_router, intergroup_links)
                round_hops += h
                round_pairs += 1
        if round_pairs > 0:
            total_hops += round_hops / round_pairs  # Average for this round
    
    return total_hops

# Dragonfly configuration
num_groups = 4              
routers_per_group = 4       
hosts_per_router = 1        
intergroup_links = 2        
total_nodes = num_groups * routers_per_group * hosts_per_router

jobs = [
    {"pattern": "Allreduce", "size": total_nodes},
    {"pattern": "Bcast", "size": total_nodes, "root": 0},
    {"pattern": "Reduce", "size": total_nodes, "root": 0},
    {"pattern": "Allgather", "size": total_nodes},
    {"pattern": "Barrier", "size": total_nodes},
    {"pattern": "PingPong", "pairs": [(0,1), (0,2), (0,3), (0,5), (0,8), (0,15)]}
]

rows_avg = [["Pattern", "Ranks", "Avg HopCount"]]
hop_values = []
all_hops = []  # Store all individual hop counts for detailed analysis

for job in jobs:
    if job["pattern"] in ["Allreduce", "Allgather"]:
        avg = calculate_allpairs(job["size"], num_groups, routers_per_group, hosts_per_router, intergroup_links)
        rows_avg.append([job["pattern"], job["size"], round(avg, 2)])
        hop_values.append(avg)
    
    elif job["pattern"] == "Barrier":
        avg = calculate_barrier(job["size"], num_groups, routers_per_group, hosts_per_router, intergroup_links)
        rows_avg.append([job["pattern"], job["size"], round(avg, 2)])
        hop_values.append(avg)
    
    elif job["pattern"] in ["Bcast", "Reduce"]:
        avg = calculate_rooted(job["size"], job["root"], num_groups, routers_per_group, hosts_per_router, intergroup_links)
        rows_avg.append([f"{job['pattern']} root={job['root']}", job["size"], round(avg, 2)])
        hop_values.append(avg)
    
    elif job["pattern"] == "PingPong":
        for a, b in job["pairs"]:
            hops = dragonfly_hops(a, b, num_groups, routers_per_group, hosts_per_router, intergroup_links)
            rows_avg.append([f"PingPong {a}-{b}", 2, hops])
            hop_values.append(hops)

# Overall average
overall = sum(hop_values) / len(hop_values) if hop_values else 0
rows_avg.append(["Overall", "-", round(overall, 2)])

# Print summary
print(f"Dragonfly Hop Count Summary (Groups={num_groups}, Routers/Group={routers_per_group}, Hosts/Router={hosts_per_router}, InterLinks={intergroup_links})")
print("Note: +2 hops included for injection/ejection latency\n")
print("-" * 45)
for row in rows_avg:
    print(f"{row[0]:<20} {str(row[1]):<5} {row[2]}")



# Show specific examples
print(f"\nSpecific examples:")
for a, b in [(0, 1), (0, 4), (0, 8), (0, 15)]:
    hops = dragonfly_hops(a, b, num_groups, routers_per_group, hosts_per_router, intergroup_links)
    g1 = a // (routers_per_group * hosts_per_router)
    g2 = b // (routers_per_group * hosts_per_router)
    print(f"Rank {a} (Group {g1}) → Rank {b} (Group {g2}): {hops} hops")