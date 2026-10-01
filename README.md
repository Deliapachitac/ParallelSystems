# Parallel systems Assignments

This repository contains the coursework completed for the **Parallel Systems** course, offered by the Department of Informatics and Telecommunications at the National and Kapodistrian University of Athens (NKUA). The project is structured into four main directories (`assignment 1`, `assignment 2`, `assignment 3`, and `assignment 4`), each corresponding to an individual coursework assignment. Every folder includes the complete source code, implementation files, and a comprehensive written technical report in PDF format detailing the architecture, benchmarks, and findings.

## ⚡ Core Concepts & Parallelization Techniques

This repository explores fundamental concepts in high-performance computing (HPC) and parallel algorithm design, focusing on speedup, scalability, and resource utilization across multi-core and distributed architectures:

* **Shared-Memory Parallelism (OpenMP / POSIX Threads)**
  * Loop parallelization and work-sharing constructs with dynamic and static scheduling.
  * Thread synchronization, mutexes, condition variables, and critical sections to eliminate data races.
  * Memory overhead reduction through thread-private variables and reduction clauses.

* **Distributed-Memory Systems (MPI)**
  * Point-to-point communication (`MPI_Send`, `MPI_Recv`) and non-blocking asynchronous transfers (`MPI_Isend`, `MPI_Irecv`).
  * Collective communication routines (`MPI_Bcast`, `MPI_Scatter`, `MPI_Gather`, `MPI_Reduce`) for data distribution.
  * Process topology decomposition and domain partitioning for scalable cluster execution.

* **GPU Acceleration & Massively Parallel Compute (CUDA)**
  * Kernel design, grid/block execution configurations, and thread indexing models.
  * Memory hierarchy optimizations utilizing Shared Memory, Register allocation, and Coalesced Global Memory accesses.
  * Asynchronous host-device data transfers and execution stream overlap.

* **Performance Analysis & Benchmarking**
  * Strong and weak scaling evaluations using Amdahl's Law and Gustafson's Law.
  * Metrics tracking speedup ratios, parallel efficiency, throughput, and communication-to-computation ratios.