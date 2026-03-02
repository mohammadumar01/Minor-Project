import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# Select default Firefly platform (NIC/OS parameters)
PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Job configuration
job = {
    "size": 1024,
    "start": 0,
    "motifs": [
        {"pattern": "Allreduce", "params": "iterations=92 count=1 "}, #compute=69ns
        {"pattern": "Bcast", "params": "root=0 iterations=2 count=7 "},#compute=1323ns
        {"pattern": "Reduce", "params": "root=0 iterations=2 count=2 "},#compute=450ns
        {"pattern": "Allgather", "params": "iterations=3 count=3  verify=0"},#compute=243ns
        {"pattern": "Barrier", "params": "iterations=99 "}#compute=75ns
        # {"pattern": "PingPong", "params": "rank2=1 iterations=105 messageSize=409 "},#compute=3ns
        # {"pattern": "PingPong", "params": "rank2=8 iterations=105 messageSize=409 compute=3ns"},
        # {"pattern": "PingPong", "params": "rank2=16 iterations=105 messageSize=82 compute=3ns"},
        # {"pattern": "PingPong", "params": "rank2=32 iterations=105 messageSize=82 compute=3ns"},

        # {"pattern": "PingPong", "params": "rank2=48 iterations=105 messageSize=490 compute=3ns"}

    ]
}


# Fat-tree topology configuration 
topo = topoFatTree()
topo.shape = "4,4:4,4:64"
topo.routing_alg="deterministic"
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
    "filepath": "fat1024.csv",
    "separator": ", "
})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")
