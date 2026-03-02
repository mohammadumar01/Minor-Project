import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Topology: 3D Torus (2x2x4) with 1 host per router (total 16 nodes)
topo = topoTorus() 
topo.shape = "2x2x4"              
topo.local_ports = 1            
topo.width = "1x1x2"           
topo.link_latency = "25ns"

# Router configuration
router = hr_router()
router.link_bw = "12GB/s"
router.flit_size = "16B"
router.xbar_bw = "24GB/s"
router.input_latency = "20ns"
router.output_latency = "20ns"
router.input_buf_size = "16kB"
router.output_buf_size = "16kB"
router.num_vns = 2
router.xbar_arb = "merlin.xbar_arb_lru"
topo.router = router

# Network interface configuration
nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"

# Create the system and assign the topology
system = System()
system.setTopology(topo)

# Job Patterns Based on MiniMD TAU Profiling
job = {
    "size": 16,
    "start": 0,
    "motifs": [
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=20510"},  # Face neighbor1 (X+/- direction)
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=9500 "},   #Face neighbor2 (Y+/-)
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=20530 "},  # Edge neighbor3 (Z+/-)
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=8500 "}, # daigonal/Edge-corner neighbor4 
        {"pattern": "Allreduce", "params": "count=1 iterations=40 "}, 
        {"pattern": "Barrier", "params": "iterations=15 "},     
    ]
}

# Assign jobs to system 
ep = EmberMPIJob(job["start"], job["size"])
ep.network_interface = nic
ep.addMotif("Init")
for motif in job["motifs"]:
    ep.addMotif(f"{motif['pattern']} {motif['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"
system.allocateNodes(ep, "linear")

# Build the system
system.build()

# Configure statistics and debugging
sst.setStatisticLoadLevel(12) 
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "torus16.csv",
    "separator": ", "
})

# Enable key statistics
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {
    "MotifLog": "1"
})
sst.enableAllStatisticsForComponentType("ember.nic")

# Print confirmation
print("MiniMD Pattern Simulation Configured:")
print("- Topology: 3D torus 2x2x4")
print("- Hosts per router: 1")
print(f"- Total compute nodes: {2*2*4*topo.local_ports}")
print(f"- Total ranks: {job['size']}")
print(f"- Jobs configured: 1 job, {job['size']} total ranks")