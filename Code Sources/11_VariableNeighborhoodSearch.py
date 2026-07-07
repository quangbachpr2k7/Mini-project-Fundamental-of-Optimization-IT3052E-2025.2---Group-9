import sys
import time
import random

def solve():
    start_time = time.time()
    MAX_TIME = 1.8

    input_data = sys.stdin.read().split()
    if not input_data:
        return
    iterator = iter(input_data)

    N = int(next(iterator))
    Q = int(next(iterator))

    predecessors = [[] for _ in range(N + 1)]
    successors = [[] for _ in range(N + 1)]
    is_direct_pred = [[False] * (N + 1) for _ in range(N + 1)]

    for _ in range(Q):
        u = int(next(iterator))
        v = int(next(iterator))
        predecessors[v].append(u)
        successors[u].append(v)
        is_direct_pred[u][v] = True

    duration = [0] * (N + 1)
    for i in range(1, N + 1):
        duration[i] = int(next(iterator))

    M = int(next(iterator))
    
    team_ready_list = [0] * (M + 1)
    for i in range(1, M + 1):
        team_ready_list[i] = int(next(iterator))

    K = int(next(iterator))
    
    available_teams = [[] for _ in range(N + 1)]
    costs_mat = [[0] * (M + 1) for _ in range(N + 1)]

    for _ in range(K):
        i = int(next(iterator))
        j = int(next(iterator))
        c = int(next(iterator))
        available_teams[i].append(j)
        costs_mat[i][j] = c

    def calc_fitness(T, A):
        task_end = [-1] * (N + 1)
        team_ready = team_ready_list[:]
        total_cost = 0
        max_end = 0

        for t in T:
            j = A[t]
            pred_end = 0
            for p in predecessors[t]:
                e = task_end[p]
                if e > pred_end:
                    pred_end = e

            start_t = team_ready[j] if team_ready[j] > pred_end else pred_end
            end_t = start_t + duration[t]

            task_end[t] = end_t
            team_ready[j] = end_t
            total_cost += costs_mat[t][j]
            if end_t > max_end:
                max_end = end_t

        return (-len(T), max_end, total_cost)

    def is_precedence_feasible_full(T):
        pos = [-1] * (N + 1)
        for idx, t in enumerate(T):
            pos[t] = idx
            
        for v in T:
            p_v = pos[v]
            for u in predecessors[v]:
                p_u = pos[u]
                if p_u >= p_v:
                    return False
        return True

    # Initialization
    in_degree = [len(predecessors[i]) for i in range(N + 1)]
    queue = [i for i in range(1, N + 1) if in_degree[i] == 0]

    curr_T = []
    curr_A = [0] * (N + 1)
    task_end_greedy = [-1] * (N + 1)
    team_ready_greedy = team_ready_list[:]

    # Greedy Construction
    while queue:
        u = queue.pop(0)

        if not available_teams[u]:
            for v in successors[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
            continue

        pred_end = 0
        for p in predecessors[u]:
            e = task_end_greedy[p]
            if e > pred_end:
                pred_end = e

        best_team = 0
        best_finish = float('inf')

        for tm in available_teams[u]:
            start_t = team_ready_greedy[tm] if team_ready_greedy[tm] > pred_end else pred_end
            finish_t = start_t + duration[u]
            if finish_t < best_finish:
                best_finish = finish_t
                best_team = tm
            elif finish_t == best_finish:
                if costs_mat[u][tm] < costs_mat[u][best_team]:
                    best_team = tm

        curr_T.append(u)
        curr_A[u] = best_team
        task_end_greedy[u] = best_finish
        team_ready_greedy[best_team] = best_finish

        for v in successors[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    best_T = curr_T[:]
    best_A = curr_A[:]
    f_best = calc_fitness(best_T, best_A)

    # Shaking Phase (Perturbation)
    def shake(T, A, k):
        new_T = T[:]
        new_A = A[:]
        n_tasks = len(T)

        if n_tasks < 2:
            return new_T, new_A

        if k == 1:
            # Swap adjacent independent tasks
            for _ in range(10):
                idx = random.randint(0, n_tasks - 2)
                t1, t2 = new_T[idx], new_T[idx + 1]
                if not is_direct_pred[t1][t2]:
                    new_T[idx], new_T[idx + 1] = t2, t1
                    break
                    
        elif k == 2:
            # Reassign a task to a different team
            for _ in range(10):
                idx = random.randint(0, n_tasks - 1)
                task = new_T[idx]
                if len(available_teams[task]) > 1:
                    current_team = new_A[task]
                    candidates = [tm for tm in available_teams[task] if tm != current_team]
                    if candidates:
                        new_A[task] = random.choice(candidates)
                        break
                        
        elif k == 3:
            # Swap any two tasks and randomly reassign one
            for _ in range(10):
                idx1, idx2 = random.sample(range(n_tasks), 2)
                new_T[idx1], new_T[idx2] = new_T[idx2], new_T[idx1]
                
                if is_precedence_feasible_full(new_T):
                    task = new_T[idx1]
                    if len(available_teams[task]) > 1:
                        current_team = new_A[task]
                        candidates = [tm for tm in available_teams[task] if tm != current_team]
                        if candidates:
                            new_A[task] = random.choice(candidates)
                    break
                else:
                    # Revert swap if topological order is violated
                    new_T[idx1], new_T[idx2] = new_T[idx2], new_T[idx1]

        return new_T, new_A

    # Variable Neighborhood Descent (Local Search)
    def vnd_local_search(T, A):
        current_T = T[:]
        current_A = A[:]
        best_fit = calc_fitness(current_T, current_A)

        l = 1
        l_max = 2
        n_tasks = len(current_T)

        while l <= l_max:
            improved = False

            # Neighborhood 1: Swap adjacent tasks
            if l == 1:
                for idx in range(n_tasks - 1):
                    t1 = current_T[idx]
                    t2 = current_T[idx + 1]
                    if not is_direct_pred[t1][t2]:
                        current_T[idx], current_T[idx + 1] = t2, t1
                        fit = calc_fitness(current_T, current_A)
                        if fit < best_fit:
                            best_fit = fit
                            improved = True
                        else:
                            current_T[idx], current_T[idx + 1] = t1, t2

            # Neighborhood 2: Team reassignment
            elif l == 2:
                for idx in range(n_tasks):
                    t = current_T[idx]
                    current_team = current_A[t]
                    best_team_for_t = current_team
                    best_team_fit = best_fit
                    found_better = False

                    for tm in available_teams[t]:
                        if tm != current_team:
                            current_A[t] = tm
                            fit = calc_fitness(current_T, current_A)
                            if fit < best_team_fit:
                                best_team_fit = fit
                                best_team_for_t = tm
                                found_better = True

                    if found_better:
                        current_A[t] = best_team_for_t
                        best_fit = best_team_fit
                        improved = True
                    else:
                        current_A[t] = current_team

            if improved:
                l = 1
            else:
                l += 1

        return current_T, current_A, best_fit

    # VNS Main Loop
    k_max = 3
    while True:
        if time.time() - start_time > MAX_TIME:
            break

        k = 1
        while k <= k_max:
            if time.time() - start_time > MAX_TIME:
                break

            cand_T, cand_A = shake(best_T, best_A, k)
            opt_T, opt_A, f_cand = vnd_local_search(cand_T, cand_A)

            if f_cand < f_best:
                best_T = opt_T[:]
                best_A = opt_A[:]
                f_best = f_cand
                k = 1
            else:
                k += 1

    # Format Output
    task_start = [-1] * (N + 1)
    task_end = [-1] * (N + 1)
    team_ready = team_ready_list[:]

    for t in best_T:
        j = best_A[t]
        pred_end = 0
        for p in predecessors[t]:
            e = task_end[p]
            if e > pred_end:
                pred_end = e

        start_t = team_ready[j] if team_ready[j] > pred_end else pred_end
        task_start[t] = start_t
        end_t = start_t + duration[t]
        task_end[t] = end_t
        team_ready[j] = end_t

    print(len(best_T))
    
    for t in sorted(best_T):
        print(f"{t} {best_A[t]} {task_start[t]}")

if __name__ == '__main__':
    solve()
