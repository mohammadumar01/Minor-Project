import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# Set the platform
PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Configure topology
topo = topoTorus() 
topo.shape = "32x32"
topo.local_ports = 1
topo.width = "16x16"
topo.link_latency = "25ns"

# Router configuration 
router = hr_router()
router.link_bw = "12GB/s"
router.flit_size = "16B"
router.xbar_bw = "20GB/s"
router.input_latency = "30ns"
router.output_latency = "30ns"
router.input_buf_size = "32kB"
router.output_buf_size = "32kB"
router.num_vns = 2
router.xbar_arb = "merlin.xbar_arb_lru"
topo.router = router

# Network interface 
nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"

# Create system 
system = System()
system.setTopology(topo)


# Job definition
job = {
    "size": 1024 , 
    "start": 0,
    "motifs": [
        {"pattern": "Allreduce", "params": "iterations=92 count=1"},
        {"pattern": "Bcast", "params": "root=0 iterations=2 count=7 "},
        {"pattern": "Reduce", "params": "root=0 iterations=2 count=2"},
        {"pattern": "Allgather", "params": "iterations=3 count=3  verify=0"},
        {"pattern": "Barrier", "params": "iterations=99 "}

    ] 
}
# Target ranks for PingPong from rank=0
# target_ranks = [
#     1,   # nearest neighbor
#     31,   # same row, far end
#     992,  # same column, far end
#     1023  # farthest diagonal
# ]

# # Append PingPong motifs
# for target in target_ranks:
#     job["motifs"].append(
#         {
#             "pattern": "PingPong",
#             "params": f"rank2={target} iterations=105 messageSize=256 compute=3ns"
#         }
#     )

# Create and assign job 
ep = EmberMPIJob(0, job["size"])
ep.network_interface = nic
ep.addMotif("Init")
for motif in job["motifs"]:
    ep.addMotif(f"{motif['pattern']} {motif['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"
system.allocateNodes(ep, "linear")

# Build the system 
system.build()

# Statistics configuration 
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "torus32x32.csv", 
    "separator": ", "
})

# Enable detailed statistics 
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {
    "MotifLog": "1"
})
sst.enableAllStatisticsForComponentType("ember.nic")