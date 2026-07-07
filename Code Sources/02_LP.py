from ortools.linear_solver import pywraplp
import sys

N, Q = map(int, input().split())
order_tasks = [[0]*(N+1) for _ in range(N+1)] 
for i in range(1, Q+1):
    j, k = map(int, input().split())
    order_tasks[j][k] = -1 

d = [0] + list(map(int, input().split())) 

M = int(input())
s = [0] + list(map(int, input().split())) 

K = int(input())
c = {}  # Lưu chi phí

for k in range(K):
    i, j, l = map(int, input().split())
    c[(i, j)] = l  

# Khởi tạo bộ giải MIP 
solver = pywraplp.Solver.CreateSolver('SCIP')
if not solver:
    sys.exit()

# L: Big-M
L = sum(d) + max(s)

# Khai báo các biến quyết định
y = {}      # y[i] = 1 nếu Task i được chọn, 0 nếu bỏ qua
t = {}  # Thời điểm bắt đầu của Task i
e = {}    # Thời điểm kết thúc của Task i

for i in range(1, N + 1):
    y[i] = solver.IntVar(0, 1, f'y_{i}')
    t[i] = solver.NumVar(0, L, f't_{i}')
    e[i] = solver.NumVar(0, L, f'e_{i}')
    
    solver.Add(e[i] == t[i] + d[i])

x = {} #x[i, j] = 1 nếu task i được giao cho team j, 0 ngược lại
for (i, j), l in c.items():
    x[i, j] = solver.IntVar(0, 1, f'x_{i}_{j}')
            
    solver.Add(t[i] >= s[j] - L * (1 - x[i, j]))

# Biến nhị phân phụ z[i, k] = 1 nếu task i làm trước task k bởi cùng 1 team j
z = {}
for i in range(1, N + 1):
    for k in range(i + 1, N + 1):
        z[i, k] = solver.IntVar(0, 1, f'z_{i}_{k}')

# Ràng buộc 1: Tính nhất quán phân công (Mỗi việc được chọn chỉ do 1 đội làm)
for i in range(1, N + 1):
    valid_teams = [x[i, j] for j in range(1, M + 1) if (i, j) in x]
    solver.Add(sum(valid_teams) == y[i])

# Ràng buộc 3: Ràng buộc tiên quyết
for j in range(1, N + 1):
    for k in range(1, N + 1):
        if order_tasks[j][k] == -1:  # Task j bắt buộc phải xong trước Task k (nếu cả 2 cùng được chọn)
            solver.Add(t[k] >= e[j] - L * (2 - y[j] - y[k]))

# Ràng buộc 4: Nếu task i và task k đều được giao cho team j, thì chung không được làm đồng thời
for j in range(1, M + 1):
    tasks_for_team_j = [i for i in range(1, N + 1) if (i, j) in x] #List tất cả các task được giao cho team j
    for id1 in range(len(tasks_for_team_j)):
        for id2 in range(id1 + 1, len(tasks_for_team_j)):
            i = tasks_for_team_j[id1]
            k = tasks_for_team_j[id2]
            u, v = (i, k) if i < k else (k, i)
            
            # Nếu cả i và k đều giao cho đội j thì i chỉ có thể bắt đầu sau khi k kết thúc/ ngược lại
            solver.Add(t[v] >= e[u] - L * (1 - z[u, v]) - L * (2 - x[i, j] - x[k, j]))
            solver.Add(t[u] >= e[v] - L * z[u, v] - L * (2 - x[i, j] - x[k, j]))

# Biến bổ trợ C_max để tối ưu thời gian kết thúc dự án
C_max = solver.NumVar(0, L, 'C_max')
for i in range(1, N + 1):
    solver.Add(C_max >= e[i] - L * (1 - y[i]))

# Đặt giới hạn thời gian chạy (30 giây = 30000 mili giây)
solver.set_time_limit(30000)


# Mục tiêu 1: Tối đa hóa số lượng công việc được lên lịch
objective = solver.Objective()
for i in range(1, N + 1):
    objective.SetCoefficient(y[i], 1)
objective.SetMaximization()

status = solver.Solve()
if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
    sys.exit()

best_f1 = int(round(solver.Objective().Value()))
solver.Add(sum(y[i] for i in range(1, N + 1)) == best_f1) # Cố định kết quả F1

# Mục tiêu 2: Tối thiểu hóa thời gian hoàn thành (Makespan)
solver.Objective().Clear() # Xóa hàm mục tiêu cũ
solver.Objective().SetCoefficient(C_max, 1)
solver.Objective().SetMinimization()

status = solver.Solve()
best_f2 = int(round(solver.Objective().Value()))
solver.Add(C_max == best_f2) # Cố định kết quả F2

# Mục tiêu 3: Tối thiểu hóa tổng chi phí thực hiện dự án
solver.Objective().Clear()
for (i, j), cost_val in c.items():
    solver.Objective().SetCoefficient(x[i, j], cost_val)
solver.Objective().SetMinimization()

status = solver.Solve()
best_f3 = int(round(solver.Objective().Value()))


if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
    print(best_f1)
    # Lên lịch
    sche = []
    for i in range(1, N + 1):
        if y[i].solution_value() > 0.5:
            for j in range(1, M + 1):
                if (i, j) in x and x[i, j].solution_value() > 0.5:
                    sche.append((i, j, int(round(t[i].solution_value()))))
    for i in sche:
        print(*i)
