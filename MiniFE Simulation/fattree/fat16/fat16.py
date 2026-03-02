import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# Select default Firefly platform (NIC/OS parameters)
PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Define MPI job with 4 ranks and communication motifs
job = {
    "size": 16,
    "start": 0,
    "motifs": [
        {"pattern": "Allreduce", "params": "iterations=92 count=1 "},
        {"pattern": "Bcast", "params": "root=0 iterations=2 count=7 "},
        {"pattern": "Reduce", "params": "root=0 iterations=2 count=2"},
        {"pattern": "Allgather", "params": "iterations=3 count=3  verify=0"},
        {"pattern": "Barrier", "params": "iterations=99 "}
        # {"pattern": "PingPong", "params": "rank2=1 iterations=105 messageSize=409 "},
        # {"pattern": "PingPong", "params": "rank2=2 iterations=105 messageSize=409 "},
        # {"pattern": "PingPong", "params": "rank2=4 iterations=105 messageSize=82"},
        # {"pattern": "PingPong", "params": "rank2=8 iterations=105 messageSize=82"},
        # {"pattern": "PingPong", "params": "rank2=12 iterations=105 messageSize=82"}

    ]
}


# Fat-tree topology configuration (3 levels, 4 end hosts total)
topo = topoFatTree()
topo.shape = "2,2:2,2:4"
topo.routing_alg="deterministic"
topo.link_latency = "25ns"

# Router configuration (input/output latency, buffers, bandwidths)
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

# NIC configuration
nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"

# Build system with topology and endpoints
system = System()
system.setTopology(topo)

ep = EmberMPIJob(0, job["size"])
ep.network_interface = nic
ep.addMotif("Init")
for motif in job["motifs"]:
    ep.addMotif(f"{motif['pattern']} {motif['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"

system.allocateNodes(ep, "linear")
system.build()

# Statistics collection
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "fat16.csv",
    "separator": ", "
})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")
