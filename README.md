# Mini-project-Fundamental-of-Optimization-IT3052E-2025.2---Group-9

This repository contains a comprehensive collection of algorithmic approaches—ranging from simple exact methods to advanced meta-heuristics—implemented in Python to solve the **Task Assignment & Scheduling Problem**. 

The core objective is to optimally allocate a set of dependent tasks to multiple available teams while satisfying strict precedence constraints and team availability schedules. The algorithms are designed to handle multi-objective optimization:
1. **Maximize** the total number of scheduled tasks.
2. **Minimize** the overall project completion time (Makespan).
3. **Minimize** the total operational/execution cost.

These methods utilize optimized graph representations, dynamic data structures, and state-of-the-art constraint solvers via Google OR-Tools.

---

## ⚙️ General Requirements & Environment Setup

The repository is built natively using **Python 3**, but it is better to use **Python 3.12** or later to ensure the stability. While the **Heuristic**, **Meta-heuristics**, and **Additional methods** run entirely on standard libraries, the **Exact methods** require external solvers.

```bash
# Required to execute Exact Methods (LP, CP models)
pip install ortools
```

### General Usage
To run these programs, you can copy the codes and push into a complier, or you can install them and run directly through the command line, for example:

```bash
python 03_CP.py < instances/input_data.txt
```

---

## 📂 Algorithms & Tuning Guide

The source code is divided into four main approaches, balancing execution speed and solution quality depending on the dataset size.

### 1. Exact Methods
These methods guarantee finding the global optimal solution by exploring all possibilities or using mathematical solver tools.

* **`01_Backtracking.py`**: Combines depth-first Backtracking with Topological Sorting to check all valid task-team combinations.
* **`02_LP.py`**: Formulates the problem as a Mixed-Integer Linear Programming (MILP) model and solves it using the SCIP solver backend in OR-Tools.
* **`03_CP.py`**: Formulates the problem using Constraint Programming (CP). By using `Interval Variables`, the CP-SAT solver runs highly efficiently on dense scheduling problems.

> **🔧 Configuration & Tuning Notes:**
> * **Dependencies:** Requires `pip install ortools`.
> * **Setting Time Limits:** Exact methods can take a long time on large inputs. You can limit the running time inside the code:
>   * In `02_LP.py`: Find `solver.set_time_limit(30000)` (measured in milliseconds, which equals 30 seconds).
>   * In `03_CP.py`: Find `solver.parameters.max_time_in_seconds = 30.0`.
> * **Scalability:** As noted in the report, exact methods have poor scalability and are strictly limited to small or moderate problems. Do not use `01_Backtracking.py` for large inputs ($N > 20$) due to exponential time complexity.

### 2. Heuristics
When you need an immediate solution, heuristics can construct a good, feasible schedule within milliseconds.

* **`04_Heuristic.py`**: A Greedy algorithm based on Topological Sorting. It calculates task weights by counting downstream successors using a Dynamic Programming (DP) closure over the directed graph, ensuring critical path tasks are prioritized.

> **🔧 Configuration & Tuning Notes:**
> * **Dependencies:** Pure Python. Uses standard libraries like `heapq` and `sys`.
> * **Weight Hyperparameters:** You can change the algorithm's behavior by adjusting the weights directly in the code:
>   * **Task Priority:** Modify `w1` and `w2` (default: `0.3` and `0.7`). A higher `w1` prioritizes tasks with many dependents, while a higher `w2` prefers shorter tasks.
>   * **Team Allocation:** Modify `w3` and `w4` (default: `0.8` and `0.2` in `assign_team_heu2`) to balance between an early start time (`w3`) and low team cost (`w4`).

### 3. Meta-heuristics
Designed for large-scale problems, these algorithms explore the search space broadly and use mechanisms to escape local optima.

* **`06_GeneticAlgorithm.py`**: Genetic Algorithm (GA). Uses crossover (like POX/TAX) and mutation operators to evolve a population of schedules while respecting task dependencies.
* **`07_SimulatedAnnealing.py`**: Simulated Annealing (SA). Accepts worse solutions with a dynamic probability based on a cooling temperature schedule to explore new areas.
* **`08_TabuSearch.py`**: Tabu Search. Uses a short-term memory list (`Tabu list`) to temporarily forbid recently made task-team changes, preventing the search from looping.
* **`09_AntColonyOptimization.py`**: Ant Colony Optimization (ACO). Simulates foraging ants where decisions are guided by a combination of greedy heuristics and a shared pheromone matrix.

> **🔧 Configuration & Tuning Notes:**
> * **Runtime Limit:** All meta-heuristics use a hard time stop. You can modify `max_time = 295.0` (in seconds) to shorten or extend the search.
> * **Tuning Effort:** As highlighted in the report, meta-heuristics require trial-and-error testing to find the best hyperparameters:
>   * **GA:** Change `population_size = 10` or `mutation_rate = 0.05`.
>   * **SA:** Adjust the initial temperature `T0 = 50.0` or stopping floor `t_min = 1e-3`.
>   * **Tabu:** Change the memory size `tabu_tenure = 10` or neighborhood size `num_neighbors = 10`.
>   * **ACO:** Tune `num_ants = 10`, evaporation rate `rho = 0.1`, pheromone weight `alpha = 1.0`, or heuristic weight `beta = 2.0`.

### 4. Adđitional Methods (Local Search Methods)
These methods focus on intensively improving the neighborhood of an existing solution to find better results quickly.

* **`10_IteratedLocalSearch.py`**: Iterated Local Search (ILS). Uses Variable Neighborhood Descent (VND) for deep local optimization, combined with random perturbation (shaking) steps to kick the solution into new areas.
* **`11_VariableNeighborhoodSearch.py`**: Variable Neighborhood Search (VNS). Jumps between different structural neighborhoods (like swapping tasks vs. changing team assignments) during its shaking phase to ensure thorough optimization.

> **🔧 Configuration & Tuning Notes:**
> * **Fast Iterations:** These scripts are tuned for high-speed execution. The internal time limit is controlled by `MAX_TIME = 1.8` seconds (or `TIME_LIMIT = 1.8`). Increase this value if you want a deeper neighborhood search.
> * **Search Depth:** In `11_VariableNeighborhoodSearch.py`, you can modify `k_max = 3` to increase the size and intensity of the shaking phase when the search becomes stuck.
