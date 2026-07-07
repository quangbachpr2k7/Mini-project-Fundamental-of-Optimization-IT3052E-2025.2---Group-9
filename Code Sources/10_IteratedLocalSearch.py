import sys
import time
import random
import math

def solve():
    start_time = time.time()
    TIME_LIMIT = 1.8 
    
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    iterator = iter(input_data)
    
    N = int(next(iterator))
    Q = int(next(iterator))
    
    adj = [[] for _ in range(N + 1)]
    rev_adj = [[] for _ in range(N + 1)]
    adj_set = [set() for _ in range(N + 1)]
    in_deg = [0] * (N + 1)
    
    for _ in range(Q):
        u = int(next(iterator))
        v = int(next(iterator))
        adj[u].append(v)
        rev_adj[v].append(u)
        adj_set[u].add(v)
        in_deg[v] += 1
        
    duration = [0] * (N + 1)
    for i in range(1, N + 1):
        duration[i] = int(next(iterator))
        
    M = int(next(iterator))
    team_avail = [0] * (M + 1)
    for i in range(1, M + 1):
        team_avail[i] = int(next(iterator))
        
    K = int(next(iterator))
    allowed_teams = [[] for _ in range(N + 1)]
    cost_matrix = [{} for _ in range(N + 1)]
    
    for _ in range(K):
        i = int(next(iterator))
        j = int(next(iterator))
        c = int(next(iterator))
        allowed_teams[i].append(j)
        cost_matrix[i][j] = c
        
    q = [i for i in range(1, N + 1) if in_deg[i] == 0]
    base_order = []
    
    while q:
        u = q.pop(0)
        
        if allowed_teams[u]:
            base_order.append(u)
            
        for v in adj[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                q.append(v)
                    
    if not base_order:
        print(0)
        return
        
    def evaluate(order, assignment):
        end_time = [0] * (N + 1)
        team_ready = team_avail[:]
        cost_sum = 0
        
        for i in order:
            est_pred = 0
            for p in rev_adj[i]:
                if end_time[p] > est_pred:
                    est_pred = end_time[p]
            
            t = assignment[i]
            start = max(est_pred, team_ready[t])
            e_i = start + duration[i]
            end_time[i] = e_i
            team_ready[t] = e_i
            cost_sum += cost_matrix[i][t]
            
        makespan = max(end_time)
        return (makespan, cost_sum)

    # Initial greedy construction
    curr_order = base_order[:]
    curr_assignment = [0] * (N + 1)
    end_time = [0] * (N + 1)
    team_ready = team_avail[:]
    
    for i in curr_order:
        est_pred = 0
        for p in rev_adj[i]:
            if end_time[p] > est_pred:
                est_pred = end_time[p]
        
        best_team = -1
        best_e_i = float('inf')
        best_cost = float('inf')
        
        for t in allowed_teams[i]:
            start = max(est_pred, team_ready[t])
            e_i = start + duration[i]
            c = cost_matrix[i][t]
            if e_i < best_e_i or (e_i == best_e_i and c < best_cost):
                best_e_i = e_i
                best_cost = c
                best_team = t
                
        curr_assignment[i] = best_team
        end_time[i] = best_e_i
        team_ready[best_team] = best_e_i
        
    curr_fit = evaluate(curr_order, curr_assignment)
    
    # Variable Neighborhood Descent
    def vnd(order, assignment, fit):
        improved = True
        while improved:
            improved = False
            if time.time() - start_time > TIME_LIMIT:
                break
            
            # Neighborhood 1: Swap adjacent independent tasks
            for k in range(len(order) - 1):
                i, j = order[k], order[k+1]
                if j not in adj_set[i]:
                    order[k], order[k+1] = order[k+1], order[k]
                    new_fit = evaluate(order, assignment)
                    if new_fit < fit:
                        fit = new_fit
                        improved = True
                        break
                    else:
                        order[k], order[k+1] = order[k+1], order[k]
            if improved: 
                continue
            
            # Neighborhood 2: Change task assignment to a different team
            for k in range(len(order)):
                i = order[k]
                old_t = assignment[i]
                for t in allowed_teams[i]:
                    if t == old_t: 
                        continue
                    assignment[i] = t
                    new_fit = evaluate(order, assignment)
                    if new_fit < fit:
                        fit = new_fit
                        improved = True
                        break
                if improved:
                    break
                else:
                    assignment[i] = old_t
                    
        return order, assignment, fit

    curr_order, curr_assignment, curr_fit = vnd(curr_order, curr_assignment, curr_fit)
    best_order, best_assignment, best_fit = curr_order[:], curr_assignment[:], curr_fit
    
    # Simulated Annealing parameters
    Temp = 100.0
    alpha = 0.95
    d = 3
    
    # Iterated Local Search loop
    while time.time() - start_time < TIME_LIMIT:
        new_order = curr_order[:]
        new_assignment = curr_assignment[:]
        
        # Perturbation step
        for _ in range(d):
            if random.random() < 0.5 and len(new_order) >= 2:
                idx1 = random.randint(0, len(new_order) - 1)
                idx2 = random.randint(0, len(new_order) - 1)
                if idx1 != idx2:
                    new_order[idx1], new_order[idx2] = new_order[idx2], new_order[idx1]
                    
                    valid = True
                    pos = {task: idx for idx, task in enumerate(new_order)}
                    for u in new_order:
                        for v in adj[u]:
                            if v in pos and pos[u] > pos[v]:
                                valid = False
                                break
                        if not valid: 
                            break
                            
                    if not valid:
                        new_order[idx1], new_order[idx2] = new_order[idx2], new_order[idx1]
            else:
                idx = random.randint(0, len(new_order) - 1)
                task = new_order[idx]
                if len(allowed_teams[task]) > 1:
                    old_t = new_assignment[task]
                    cand = [t for t in allowed_teams[task] if t != old_t]
                    new_assignment[task] = random.choice(cand)
                    
        # Apply VND on perturbed solution
        new_order, new_assignment, new_fit = vnd(new_order, new_assignment, evaluate(new_order, new_assignment))
        
        # Update best solution
        if new_fit < best_fit:
            best_fit = new_fit
            best_order = new_order[:]
            best_assignment = new_assignment[:]
            
        # Acceptance criteria
        if new_fit < curr_fit:
            curr_order, curr_assignment, curr_fit = new_order, new_assignment, new_fit
        else:
            delta = (new_fit[0] - curr_fit[0]) * 1000 + (new_fit[1] - curr_fit[1])
            if delta > 0 and Temp > 0.0001:
                prob = math.exp(-delta / Temp)
                if random.random() <= prob:
                    curr_order, curr_assignment, curr_fit = new_order, new_assignment, new_fit
                    
        Temp *= alpha
        
    # Re-evaluate best solution to format final output
    end_time = [0] * (N + 1)
    start_time_res = [0] * (N + 1)
    team_ready = team_avail[:]
    
    for i in best_order:
        est_pred = 0
        for p in rev_adj[i]:
            if end_time[p] > est_pred:
                est_pred = end_time[p]
        t = best_assignment[i]
        start = max(est_pred, team_ready[t])
        start_time_res[i] = start
        e_i = start + duration[i]
        end_time[i] = e_i
        team_ready[t] = e_i
        
    print(len(best_order))
    for i in best_order:
        print(f"{i} {best_assignment[i]} {start_time_res[i]}")

if __name__ == '__main__':
    solve()
