N, Q = map(int, input().split())
order_tasks = [[0]*(N+1) for _ in range(N+1)] #ma trận 2 chiều lưu điều kiện tiên quyết, sau này lưu thời điểm sớm nhất mà team i có thể nhận việc mới(lưu tại hàng i)

od = [row[:] for row in order_tasks] #Dùng để tạo 1 list các task theo thứ tự tiên quyết

for i in range(1, Q+1):
    j, k = map(int, input().split())
    order_tasks[j][k] = -1 
    od[j][k] = -1

order = [0] #List lưu các task theo thứ tự xếp việc trước đến sau

task_duration_time = [0] + list(map(int, input().split())) #Thời lượng mỗi task

M = int(input())
team_free_time = [0] + list(map(int, input().split())) #Thời gian các team sẵn sàng làm việc
team_busy = [(0, 0)] + [[(0, team_free_time[i])] for i in range(1, M+1)] #List lưu trữ khoảng thời gian bận của các team

K = int(input())
cost_table = [[float('inf')]*(M+1) for _ in range(N+1)] #Bảng giá c của team j với task i
for k in range(K):
    i, j, c = map(int, input().split())
    cost_table[i][j] = c

in_degree = [0] * (N + 1)
for j in range(1, N + 1):
    for k in range(1, N + 1):
        if od[j][k] == -1:
            in_degree[k] += 1

queue = [i for i in range(1, N + 1) if in_degree[i] == 0]
order = [0] #List lưu các task theo thứ tự xếp việc trước đến sau

while queue:
    #Lấy ra 1 task u từ queue và đẩy vào list order
    u = queue.pop(0)
    order.append(u)
    for v in range(1, N + 1):
        if od[u][v] == -1:
            #Số đỉnh vào v giảm đi 1, nếu bằng 0 thì thêm v vào queue để đẩy vào list ở các bước tiếp theo
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

# Khử lỗi nếu đồ thị bị chu trình hoặc thiếu task
if len(order) < N + 1:
    for i in range(1, N + 1):
        if i not in order:
            order.append(i)

sche = [] 
best_sche = []
best_cur = (-1, 0, 0) 


def backtracking(k, cn, finish_time, total_cost):
    global best_sche, best_cur
    if k == N+1: 
        cur = (cn, -finish_time, -total_cost)
        if best_cur < cur:
            best_sche = sche[:]
            best_cur = cur
        return
    
    best_cn, minus_best_makespan, minus_best_cost = best_cur
    best_makespan = -minus_best_makespan
    best_cost = -minus_best_cost
    
    remaining_tasks = N + 1 - k
    max_possible_cn = cn + remaining_tasks
    
    if max_possible_cn < best_cn:
        return
        
    if max_possible_cn == best_cn:
        if finish_time > best_makespan:
            return  
        elif finish_time == best_makespan and total_cost >= best_cost:
            return  
        
    i = order[k]
    
    can_do = True
    latest_end_i = 0 #Thời điểm sớm nhất task i có thể được bắt đầu
    for h in range(1, N+1):
        if order_tasks[h][i] == -1: #Nếu tồn tại 1 task h trước i vẫn chưa được hoàn thành, trả về False và gọi backtracking tiếp
            can_do = False
            break
        elif order_tasks[h][i] > 0: #Nếu không có, gán latest_end_i cho 0 hoặc thời điểm muộn nhất mà các task tiên quyết hoàn thành
            latest_end_i = max(latest_end_i, order_tasks[h][i])
            
    if can_do: #Nếu can_do đúng, thực hiện:
        available_team = sorted([h for h in range(1, M+1) if cost_table[i][h] != float('inf')], key=lambda x: (team_busy[x][-1][1], cost_table[i][x]))
        #available_team là list các team có thể làm được task i và được sắp xếp theo thứ tự thời gian sẵn sàng sớm nhất đến muộn nhất, rồi đến chi phí từ thấp đến cao
        for j in available_team:
            start = max(latest_end_i, team_busy[j][-1][1])
            end = start + task_duration_time[i]
            if all(start >= e or end <= s for s, e in team_busy[j]):
                team_busy[j].append((start, end))
                sche.append((i, j, start))
                
                # Chuyển trạng thái các task phụ thuộc thành end time
                old_deps = []
                for v in range(1, N+1):
                    if order_tasks[i][v] == -1:
                        order_tasks[i][v] = end
                        old_deps.append(v)
                        
                backtracking(k+1, cn + 1, max(finish_time, end), total_cost + cost_table[i][j])
                
                for v in old_deps:
                    order_tasks[i][v] = -1
                sche.pop()
                team_busy[j].pop() # Gỡ lịch của team j
                
    backtracking(k+1, cn, finish_time, total_cost) #Nếu can_do sai, gọi tiếp hàm mà bỏ qua task i

backtracking(1, 0, 0, 0)
print(len(best_sche))
for i in best_sche:
    print(*i)