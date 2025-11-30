import math
import random
from collections import deque

class Monster:
    def __init__(self, start_pos, maze):
        """
        初始化 Monster 类
        :param start_pos: (x, y) 初始位置
        :param maze: 迷宫地图数据 (2D array)
        """
        self.x, self.y = start_pos
        self.maze = maze
        
        # 状态: 'patrol' (巡逻), 'chase' (跟随), 'frozen' (冻结), 'attack' (逼近)
        self.state = 'patrol'
        
        # 属性
        self.base_detection_range = 4.0
        self.current_detection_range = self.base_detection_range
        self.patrol_speed = 1.0  # 稍微提高巡逻速度
        self.chase_speed = 1.8   # 玩家速度(1.5) * 1.2
        self.attack_speed = 4.0  # 保持突袭速度
        
        # 巡逻相关
        self.patrol_target = None
        self.path = [] # 存储路径点 (x, y)
        
        # 恐怖画面触发标记
        self.trigger_scare = False
        self.distance_to_player = 0.0

    def find_path(self, start, end):
        """
        使用 BFS 寻找从 start 到 end 的路径
        :param start: (x, y) 整数坐标
        :param end: (x, y) 整数坐标
        :return: list of (x, y) 路径点
        """
        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))
        
        if start == end:
            return []
            
        queue = deque([(start, [])])
        visited = set([start])
        
        rows = len(self.maze)
        cols = len(self.maze[0])
        
        while queue:
            (curr_x, curr_y), path = queue.popleft()
            
            if (curr_x, curr_y) == end:
                return path + [(curr_x + 0.5, curr_y + 0.5)] # 返回中心点坐标
            
            # 检查四个方向
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = curr_x + dx, curr_y + dy
                
                # 只要不是墙壁 (1)，就可以通行 (包括门 2)
                if 0 <= ny < rows and 0 <= nx < cols and self.maze[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(curr_x + 0.5, curr_y + 0.5)]))
                    
        return [] # 没找到路径

    def update(self, player_pos, player_angle, eye_open, dt):
        """
        根据玩家位置和眼睛状态更新怪物状态
        :param player_pos: (x, y) 玩家位置
        :param player_angle: 玩家朝向角度 (radians)
        :param eye_open: Boolean, 玩家眼睛是否睁开
        :param dt: delta time, 帧间隔时间
        """
        px, py = player_pos
        self.distance_to_player = math.hypot(self.x - px, self.y - py)
        
        # 计算玩家是否在看怪物
        # 向量: 玩家 -> 怪物
        dx = self.x - px
        dy = self.y - py
        angle_to_monster = math.atan2(dy, dx)
        
        # 计算角度差 (归一化到 -pi 到 pi)
        angle_diff = (angle_to_monster - player_angle + math.pi) % (2 * math.pi) - math.pi
        
        # 假设视野范围 (FOV) 为 90度 (左右各 45度, pi/4)
        is_visible = abs(angle_diff) < (math.pi / 4)
        
        # --- 状态机逻辑 ---
        
        # 1. 玩家不在检测范围内
        if self.distance_to_player > self.current_detection_range:
            self.state = 'patrol'
            if not eye_open:
                # 闭眼时扩大检测范围 (每秒扩大 0.5 单位)
                self.current_detection_range += 0.5 * dt
                # print(f"[Monster] Range expanding: {self.current_detection_range:.2f}")
        
        # 2. 玩家在检测范围内
        else:
            if not eye_open:
                # 闭眼 -> 快速逼近并触发恐怖画面
                self.state = 'attack'
            elif is_visible:
                # 睁眼且看到怪物 -> 冻结
                self.state = 'frozen'
            else:
                # 睁眼但没看到怪物 -> 跟随
                self.state = 'chase'
                
        # 执行当前状态的动作
        self.act(player_pos, dt)

    def act(self, player_pos, dt):
        """
        根据状态执行移动逻辑
        """
        if self.state == 'frozen':
            return

        target_x, target_y = self.x, self.y
        speed = 0

        if self.state == 'patrol':
            speed = self.patrol_speed
            
            # 如果没有目标或已到达目标，寻找新目标
            if self.patrol_target is None or (not self.path and math.hypot(self.x - self.patrol_target[0], self.y - self.patrol_target[1]) < 0.5):
                # 随机找一个空地作为新目标
                found_target = False
                for _ in range(10): # 尝试10次
                    ty = random.randint(0, len(self.maze) - 1)
                    tx = random.randint(0, len(self.maze[0]) - 1)
                    # 目标点只要不是墙壁即可
                    if self.maze[ty][tx] != 1:
                        self.patrol_target = (tx + 0.5, ty + 0.5)
                        # 计算路径
                        self.path = self.find_path((self.x, self.y), self.patrol_target)
                        if self.path:
                            found_target = True
                            break
                if not found_target:
                    self.patrol_target = None # 重试
            
            # 如果有路径，沿着路径移动
            if self.path:
                next_node = self.path[0]
                target_x, target_y = next_node
                
                # 如果到达当前路径点，移除并前往下一个
                if math.hypot(self.x - target_x, self.y - target_y) < 0.1:
                    self.path.pop(0)
                    if self.path:
                        target_x, target_y = self.path[0]
                    else:
                        target_x, target_y = self.patrol_target
            elif self.patrol_target:
                 target_x, target_y = self.patrol_target
            
        elif self.state == 'chase':
            speed = self.chase_speed
            
            # 智能寻路：如果隔着墙，使用 BFS 规划路径
            mx, my = int(self.x), int(self.y)
            px, py = int(player_pos[0]), int(player_pos[1])
            
            if mx == px and my == py:
                # 在同一个格子，直接直线移动
                target_x, target_y = player_pos
            else:
                # 不在同一个格子，寻找路径
                path = self.find_path((self.x, self.y), player_pos)
                if len(path) >= 2:
                    # path[0] 是当前格子中心，path[1] 是下一个格子中心
                    target_x, target_y = path[1]
                else:
                    # 寻路失败（可能不可达），尝试直线移动
                    target_x, target_y = player_pos
            
            # 保持距离逻辑：如果距离玩家太近，就停止移动，让玩家能看到
            keep_distance = 2.5
            if self.distance_to_player < keep_distance:
                speed = 0
            
        elif self.state == 'attack':
            speed = self.attack_speed
            
            # 攻击状态也使用智能寻路，避免卡墙
            mx, my = int(self.x), int(self.y)
            px, py = int(player_pos[0]), int(player_pos[1])
            
            if mx == px and my == py:
                target_x, target_y = player_pos
            else:
                path = self.find_path((self.x, self.y), player_pos)
                if len(path) >= 2:
                    target_x, target_y = path[1]
                else:
                    target_x, target_y = player_pos

            self.path = [] # 攻击时不保留巡逻路径
            # 如果非常接近，触发恐怖画面
            if self.distance_to_player < 0.5:
                self.trigger_scare = True

        # --- 移动逻辑 (简单的碰撞检测) ---
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            move_dist = speed * dt
            # 归一化方向向量
            dir_x = dx / dist
            dir_y = dy / dist
            
            # 尝试移动
            nx = self.x + dir_x * move_dist
            ny = self.y + dir_y * move_dist
            
            # 检查碰撞 (假设墙壁是 1)
            # 简单的圆形/点碰撞检测
            # 注意：maze[y][x] == 2 是门，怪物应该可以穿过门或者至少不被卡住
            # 所以我们只检查是否是墙壁 (1)
            if 0 <= int(ny) < len(self.maze) and 0 <= int(nx) < len(self.maze[0]):
                if self.maze[int(ny)][int(nx)] != 1:
                    self.x = nx
                    self.y = ny
                else:
                    # 简单的滑动处理 (分别尝试 X 和 Y 轴移动)
                    if self.maze[int(self.y)][int(nx)] != 1:
                        self.x = nx
                    elif self.maze[int(ny)][int(self.x)] != 1:
                        self.y = ny
