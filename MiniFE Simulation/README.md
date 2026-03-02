
# MiniFE and MiniMD Communication Profiling and SST Simulation Project

## 📘 Project Overview

This project focuses on profiling the MPI communication patterns of the **MiniFE** and **MiniMD** mini-applications using the **TAU performance profiler** and simulating these patterns using the **Structural Simulation Toolkit (SST)**. The objective is to capture realistic communication behaviors and analyze their performance over scalable interconnection network topologies (eg.2D and 3D meshes).

---

## 🔧 TAU Installation 

### 📥 Download and Install

```bash
# Download from official site
wget https://www.cs.uoregon.edu/research/paracomp/tau/tau.tgz

# Extract and enter directory
tar -xzf tau.tgz
cd tau-*/  # e.g., tau-2.34.1/

# Configure TAU with MPI and PDT support
./configure -mpi -pdt=/path/to/pdtoolkit \
            -prefix=/opt/tau-install \
            -cc=mpicc -c++=mpicxx

# Build and install
make -j$(nproc)
make install
```

### ✅ Load TAU Environment

```bash
source /opt/tau-install/x86_64/bin/tau.sh
```

📌 Reference: [https://tau.uoregon.edu/](https://tau.uoregon.edu/)

---

## 🧱 MiniFE Installation and Profiling

### 📥 Download and Build

```bash
git clone https://github.com/Mantevo/miniFE.git
cd miniFE/ref

# Build with TAU
make clean
make PROFILE=1 TAU_VERBOSE=1
```

### ▶️ Run with TAU Profiling

```bash
mpirun -np 4 --oversubscribe tau_exec -T mpi ./miniFE.x -nx 8 -ny 8 -nz 8
```

---

## 🧱 MiniMD Installation and Profiling

### 📥 Download and Build

```bash
git clone https://github.com/Mantevo/miniMD.git
cd miniMD/ref

make clean
make PROFILE=1 TAU_VERBOSE=1
```

### ▶️ Run with TAU Profiling

```bash
mpirun -np 16 --oversubscribe tau_exec -T mpi ./miniMD -i lj.in
```

---

## 📊 TAU Profiling Commands

```bash
# Generate text summary
pprof -a > summary.txt

# Optionally: generate GUI profiles
paraprof --pack miniapp.ppk
paraprof miniapp.ppk
```

---

## ⚙️ Simulating Communication Patterns in SST

### 🧩 Prerequisites

- SST Simulator: [https://sst-simulator.org/](https://sst-simulator.org/)
  - `sst-core`
  - `sst-elements` (including `ember`, `merlin`)
- Python 3.x

### ▶️ Run SST Simulation

```bash
sst path/to/simulation_config.py
```

---

## 📏 Hop Count Analysis

Run:

```bash
# For MiniFE
python miniFE/mesh_topology/hopcount.py

# For MiniMD
python miniMD/mesh3D/hopcount.py
```

---

## 🧾 Summary of Important Commands

| Task                          | Command Example                                             |
|------------------------------|-------------------------------------------------------------|
| Install TAU (tarball)        | `./configure -mpi ... && make -j && make install`          |
| Load TAU                     | `source /opt/tau-install/x86_64/bin/tau.sh`                |
| Build MiniFE with TAU        | `make clean && make PROFILE=1 TAU_VERBOSE=1`               |
| Build MiniMD with TAU        | `make clean && make PROFILE=1 TAU_VERBOSE=1`               |
| Run MiniFE with TAU          | `mpirun -np 4 tau_exec -T mpi ./miniFE.x -nx 8 -ny 8 -nz 8` |
| Run MiniMD with TAU          | `mpirun -np 16 tau_exec -T mpi ./miniMD -i lj.in`          |
| Extract TAU Summary          | `pprof -a > summary.txt`                                   |
| Run SST Simulation           | `sst simulation_config.py`                                 |
| Run Hop Count Script         | `python hopcount.py`                                       |

---

## 🔗 Useful Links

- [TAU Profiler](https://tau.uoregon.edu/)
- [SST Simulator](https://sst-simulator.org/)
- [MiniFE GitHub](https://github.com/Mantevo/miniFE)
- [MiniMD GitHub](https://github.com/Mantevo/miniMD)
- [Mantevo]( https://mantevo.github.io/applications.html)

---

