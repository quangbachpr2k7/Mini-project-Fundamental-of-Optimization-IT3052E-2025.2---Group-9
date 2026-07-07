import sys
import heapq

sys.setrecursionlimit(200000)

def get_reachable_set(node, adj, memo, visited):
    if visited[node]:
        return memo[node]
    
    visited[node] = True
    res_set = 0
    for neighbor in adj[node]:
        neighbor_set = get_reachable_set(neighbor, adj, memo, visited)
        res_set |= neighbor_set
        res_set |= (1 << neighbor)
        
    memo[node] = res_set
    return res_set

def compute_successors_dp(N, adj):
    memo = [0] * (N + 1)
    visited = [False] * (N + 1)
    succ_count = [0] * (N + 1)
    
    for i in range(1, N + 1):
        if not visited[i]:
            get_reachable_set(i, adj, memo, visited)
            
    for i in range(1, N + 1):
        succ_count[i] = bin(memo[i]).count('1')
        
    return succ_count

def assign_team_heu2(task, rev_adj, comp_time, task_teams, team_busy, s, w3=0.8, w4=0.2):
    """
    Lựa chọn đội tối ưu cho task dựa trên hàm Heuristic: H_team(i, j) = w3 * actual_start_time + w4 * c(i, j)
    """
    task_ready_time = max((comp_time[p] for p in rev_adj[task]), default=0)
    
    options = []
    for team_id, cost in task_teams[task]:
        team_avail = max(s[team_id], team_busy[team_id])
        actual_start = max(task_ready_time, team_avail)
        score = w3 * actual_start + w4 * cost
        options.append((score, team_id, actual_start))
        
    if not options:
        return None, None
        
    _, best_team, best_start = min(options, key=lambda x: (x[0], x[1]))
    return best_team, best_start

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
        
    iterator = iter(input_data)
    
    N = int(next(iterator))
    Q = int(next(iterator))
    
    adj = [[] for _ in range(N + 1)]
    rev_adj = [[] for _ in range(N + 1)]
    in_degree = [0] * (N + 1)
    
    for _ in range(Q):
        u = int(next(iterator))
        v = int(next(iterator))
        adj[u].append(v)
        rev_adj[v].append(u)
        in_degree[v] += 1
        
    durations = [0] + [int(next(iterator)) for _ in range(N)]
    
    M = int(next(iterator))
    s = [0] + [int(next(iterator)) for _ in range(M)]
    
    K = int(next(iterator))
    task_teams = [[] for _ in range(N + 1)]
    for _ in range(K):
        ti = int(next(iterator))
        tj = int(next(iterator))
        tc = int(next(iterator))
        task_teams[ti].append((tj, tc))
        
    succ_count = compute_successors_dp(N, adj)
    
    w1, w2 = 0.3, 0.7
    task_scores = [0.0] * (N + 1)
    for i in range(1, N + 1):
        if not task_teams[i]:
            continue
        d_i = durations[i] if durations[i] > 0 else 1e-9
        task_scores[i] = w1 * succ_count[i] + w2 * (1.0 / d_i)
        
    ready_heap = []
    for i in range(1, N + 1):
        if in_degree[i] == 0 and task_teams[i]:
            heapq.heappush(ready_heap, (-task_scores[i], i))
            
    team_busy = [0] * (M + 1)
    comp_time = [0] * (N + 1)
    scheduled = []
    
    while ready_heap:
        _, chosen_task = heapq.heappop(ready_heap)
        
        best_team, best_start = assign_team_heu2(chosen_task, rev_adj, comp_time, task_teams, team_busy, s)
        if best_team is None:
            continue
            
        team_busy[best_team] = best_start + durations[chosen_task]
        comp_time[chosen_task] = best_start + durations[chosen_task]
        scheduled.append((chosen_task, best_team, best_start))
        
        for neighbor in adj[chosen_task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0 and task_teams[neighbor]:
                heapq.heappush(ready_heap, (-task_scores[neighbor], neighbor))
                
    print(len(scheduled))
    scheduled.sort(key=lambda x: x[0])
    for t, tm, st in scheduled:
        print(f"{t} {tm} {st}")

if _name_ == '_main_':
    solve()