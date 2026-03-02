import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Topology:
topo = topoTorus() 
topo.shape = "8x8x2"              
topo.local_ports = 1            
topo.width = "4x4x1"           
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
    "size": 128,
    "start": 0,
    "motifs": [
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=20510"},  # Face neighbor1 (X+/- direction)
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=9500 "},   #Face neighbor2 (Y+/-)
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=20530 "},  # Edge neighbor3 (Z+/-)
        {"pattern": "AllPingPong", "params": "iterations=325 messageSize=8500 "}, # daigonal neighbor4 
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
    "filepath": "torus128.csv",
    "separator": ", "
})

# Enable key statistics
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {
    "MotifLog": "1"
})
sst.enableAllStatisticsForComponentType("ember.nic")

