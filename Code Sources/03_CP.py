from ortools.sat.python import cp_model
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
c = [[float('inf')]*(M+1) for _ in range(N+1)] 
for k in range(K):
    i, j, l = map(int, input().split())
    c[i][j] = l

model = cp_model.CpModel()

# L: Big_M
L = sum(d) + max(s)

y = {}      # y[i] = 1 nếu Task i được phân công, 0 nếu bị bỏ qua
start = {}  # Thời điểm bắt đầu của Task i
end = {}    # Thời điểm kết thúc của Task i

for i in range(1, N + 1):
    y[i] = model.NewBoolVar(f'y_{i}')
    start[i] = model.NewIntVar(0, L, f'start_{i}')
    end[i] = model.NewIntVar(0, L, f'end_{i}')
    
    # end = start + duration (chỉ kích hoạt khi y[i] == 1)
    model.Add(end[i] == start[i] + d[i]).OnlyEnforceIf(y[i])


x = {} 
team_intervals = {j: [] for j in range(1, M + 1)}

for i in range(1, N + 1):
    for j in range(1, M + 1):
        if c[i][j] != float('inf'):
            x[i, j] = model.NewBoolVar(f'x_{i}_{j}')
            
            # Ràng buộc thời gian rảnh, chỉ có tác dụng nếu task i được giao cho team j
            model.Add(start[i] >= s[j]).OnlyEnforceIf(x[i, j])
            
            interval = model.NewOptionalIntervalVar(
                start[i], 
                d[i], 
                end[i], 
                x[i, j], #(start[i]. end[i]) chỉ được kích hoạt nếu task i được giao cho team j
                f'interval_{i}_{j}'
            )
            team_intervals[j].append(interval) #Thêm khoảng thời gian vào dict thời gian bận của team j


# Ràng buộc 1: Tính nhất quán phân công (Mỗi việc được chọn chỉ do 1 đội làm)
for i in range(1, N + 1):
    valid_teams = [x[i, j] for j in range(1, M + 1) if (i, j) in x]
    model.Add(sum(valid_teams) == y[i])

# Ràng buộc 2: Ràng buộc tiên quyết 
for j in range(1, N + 1):
    for k in range(1, N + 1):
        if order_tasks[j][k] == -1:  # Task j bắt buộc phải xong trước Task k
            model.Add(start[k] >= end[j]).OnlyEnforceIf([y[j], y[k]]) #Chỉ được kích hoạt nếu cả 2 task đều được lên lịch

# Ràng buộc 3: Không chồng chéo lịch trình trên cùng một Team
for j in range(1, M + 1):
    model.AddNoOverlap(team_intervals[j])

# Biến bổ trợ C_max để tối ưu thời gian kết thúc dự án
C_max = model.NewIntVar(0, L, 'C_max')
for i in range(1, N + 1):
    model.Add(C_max >= end[i]).OnlyEnforceIf(y[i])



solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0 # Đặt giới hạn thời gian chạy

#Tối đa hóa số lượng công việc được lên lịch
model.Maximize(sum(y[i] for i in range(1, N + 1)))
status = solver.Solve(model)
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    sys.exit()

best_f1 = int(solver.ObjectiveValue())
model.Add(sum(y[i] for i in range(1, N + 1)) == best_f1) # Cố định kết quả

#Tối thiểu hóa thời gian hoàn thành (Makespan)
model.Minimize(C_max)
status = solver.Solve(model)
best_f2 = int(solver.ObjectiveValue())
model.Add(C_max == best_f2) # Cố định kết quả

#Tối thiểu hóa tổng chi phí thực hiện dự án
total_cost = sum(x[i, j] * c[i][j] for (i, j) in x)
model.Minimize(total_cost)
status = solver.Solve(model)
best_f3 = int(solver.ObjectiveValue())


if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(best_f1)
    #Lên lịch
    sche = []
    for i in range(1, N + 1):
        if solver.Value(y[i]):
            for j in range(1, M + 1):
                if (i, j) in x and solver.Value(x[i, j]):
                    sche.append((i, j, solver.Value(start[i])))
    for l in sche:
        print(*l)

