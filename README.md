# Mini-project-Fundamental-of-Optimization-IT3052E-2025.2---Group-9

This repository contains a comprehensive collection of algorithmic approaches—ranging from exact mathematical models to advanced meta-heuristics—implemented in Python to solve the **Task Assignment & Scheduling Problem**. 

The core objective is to optimally allocate a set of dependent tasks to multiple available teams while satisfying strict precedence constraints and team availability schedules. The algorithms are designed to handle multi-objective optimization:
1. **Maximize** the total number of scheduled tasks.
2. **Minimize** the overall project completion time (Makespan).
3. **Minimize** the total operational/execution cost.

The framework utilizes optimized graph representations, dynamic data structures, and state-of-the-art constraint solvers via Google OR-Tools.

---

## ⚙️ General Requirements & Environment Setup

The repository is built natively using **Python 3**, but it is better to use **Python 3.12** or later to ensure the stability. While the **Heuristic**, **Meta-heuristics**, and **Additional methods** run entirely on standard libraries, the **Exact methods** require external solvers.

```bash
# Required to execute Exact Methods (LP, CP models)
pip install ortools
```

### General Usage
All implementations are engineered to receive problem instances via the standard input stream (`stdin`). You can benchmark any solver by piping an input text file directly through the command line:

```bash
python 03_CP.py < instances/input_data.txt
```

---

## 📂 Algorithmic Breakdown & Tuning Frameworks

The source codes are structurally isolated into four fundamental paradigms, allowing systematic performance tradeoffs between execution speed and global solution quality.

### 1. Exact Methods
These approaches guarantee a mathematically proven global optimal solution by exhaustively mapping the discrete search space or using advanced mathematical branch-and-cut/SAT algorithms.

* **`01_Backtracking.py`**: Combines depth-first Backtracking with dynamic Topological Sorting. It checks every valid permutation of task-team schedules.
* **`02_LP.py`**: Formulates the problem as a Mixed-Integer Programming (MIP) model. It handles overlapping schedules via big-M continuous relaxations and solves them via the SCIP backend.
* **`03_CP.py`**: Formulates the challenge via Constraint Programming. By mapping operations to discrete `Interval Variables`, the underlying CP-SAT solver utilizes powerful propagation engines to outperform traditional MIP on dense scheduling horizons.

> **🔧 Configuration & Tuning Notes:**
> * **Library Dependencies:** Ensure `ortools` is installed correctly via pip.
> * **Enforcing Timeouts:** For larger problem sizes, exact solvers might run indefinitely. You can customize the processing budget by modifying the hard timeout parameters inside the files:
>   * In `02_LP.py`: Locate `solver.set_time_limit(30000)` (parameterized in milliseconds, i.e., 30 seconds).
>   * In `03_CP.py`: Locate `solver.parameters.max_time_in_seconds = 30.0`.
> * **Scalability Threshold:** `01_Backtracking.py` scales exponentially ($O(M^N)$). It should strictly be reserved for small verification instances ($N \le 20$).

### 2. Heuristic
When immediate execution is vital, constructive heuristics generate high-quality feasible schedules within milliseconds.

* **`04_Heuristic.py`**: An advanced Greedy algorithm driven by an structural graph analysis. It pre-calculates structural task weights by tracking the total down-stream successor tree through a bitwise Dynamic Programming (DP) closure over the directed acyclic graph (DAG). Tasks are ordered dynamically based on execution critical paths and assigned to minimizing teams.

> **🔧 Configuration & Tuning Notes:**
> * **Zero External Dependencies:** Runs natively on standard Python libraries (`heapq`, `sys`).
> * **Weight Hyperparameters:** You can steer the greedy behavior by tweaking the balanced scoring functions in the source code:
>   * **Task Priority Equation:** Modify `w1` and `w2` (currently `0.3` and `0.7`). Increasing `w1` forces the solver to prioritize critical bottleneck tasks with massive downward dependency chains, while a higher `w2` favors shorter tasks.
>   * **Team Allocation Tradeoff:** Modify `w3` and `w4` (defaulting to `0.8` and `0.2` within `assign_team_heu2`). Alter these to prioritize early schedule start times (`w3`) versus low financial operational cost (`w4`).

### 3. Meta-heuristics
Designed for massive combinatorial spaces, these algorithms escape local optima by modeling physical or biological processes, delivering near-optimal boundary solutions for dense industrial instances.

* **`06_GeneticAlgorithm.py`**: Genetic Algorithm (GA). Encodes schedules into distinct chromosomes. It preserves DAG sequence constraints across generations using specialized order-preserving crossovers (e.g., POX/TAX mechanics) and targeted team mutations.
* **`07_SimulatedAnnealing.py`**: Simulated Annealing (SA). Employs a stochastic thermodynamic cooling curve. It accepts degrading temporary schedule movements early on based on a Boltzmann probability distribution ($\exp(-\Delta/T)$) to map alternative basins of attraction.
* **`08_TabuSearch.py`**: Tabu Search. Drives deterministic local optimization via responsive short-term memory structures (`Tabu list`). Forbidding recently modified task-team swaps prevents looping and forces the exploration of unmapped neighborhoods.
* **`09_AntColonyOptimization.py`**: Ant Colony Optimization (ACO). Multi-agent system modeling foraging ants. Paths through the scheduling space are built iteratively via a joint probability matrix composed of static greedy heuristics and dynamic pheromone matrices ($\tau_{i,j}$).

> **🔧 Configuration & Tuning Notes:**
> * **Global Processing Bounds:** All meta-heuristics utilize a standard temporal limit check. Modify `max_time = 295.0` (in seconds) to compress or extend the optimization window.
> * **Hyperparameter Optimization Mapping:**
>   * **GA:** Tune `population_size = 10` and `mutation_rate = 0.05` to balance exploration and exploitation.
>   * **SA:** Control the search convergence by altering the initial thermodynamic boundary `T0 = 50.0` and the floor termination condition `t_min = 1e-3`.
>   * **Tabu:** Tweak memory limits via `tabu_tenure = 10` alongside the candidate generation scale `num_neighbors = 10`.
>   * **ACO:** Calibrate the exploration metrics by altering `num_ants = 10`, evaporation rate `rho = 0.1`, pheromone weight `alpha = 1.0`, and visibility heuristic scale `beta = 2.0`.

### 4. Local Search Methods
These implementations optimize solution quality by intensely searching the local neighborhood of an initial candidate solution.

* **`10_IteratedLocalSearch.py`**: Iterated Local Search (ILS). Implements a deep Variable Neighborhood Descent (VND) algorithm to drain a specific local space, combined with structured non-destructive random perturbations to bounce the state into clean operational regions.
* **`11_VariableNeighborhoodSearch.py`**: Variable Neighborhood Search (VNS). Systematically jumps across distinct structural neighborhoods (e.g., swapping disjoint task sets vs. altering isolated team profiles) during its shaking phase to guarantee thorough optimization.

> **🔧 Configuration & Tuning Notes:**
> * **High-Speed Execution:** Engineered for fast iterations. The internal temporal boundaries are calibrated closely via `MAX_TIME = 1.8` seconds (or `TIME_LIMIT = 1.8` depending on the file). Scale this variable up to allow deep, extensive neighborhood crawls.
> * **Neighborhood Structures:** Inside `11_VariableNeighborhoodSearch.py`, you can modify `k_max = 3` to scale up the strength and diversity of the shaking phase, allowing the algorithm to execute larger structural leaps when current search spaces become stagnant.
