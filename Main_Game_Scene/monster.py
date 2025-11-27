import math
import random

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
        self.patrol_speed = 1.5
        self.chase_speed = 2.8
        self.attack_speed = 7.0
        
        # 巡逻相关
        self.patrol_target = None
        
        # 恐怖画面触发标记
        self.trigger_scare = False
        self.distance_to_player = 0.0

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
                # 闭眼时扩大检测范围 (每秒扩大 1.5 单位)
                self.current_detection_range += 1.5 * dt
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
            # 简单的随机巡逻逻辑
            if self.patrol_target is None or math.hypot(self.x - self.patrol_target[0], self.y - self.patrol_target[1]) < 0.5:
                # 随机找一个空地作为新目标
                for _ in range(10): # 尝试10次
                    ty = random.randint(0, len(self.maze) - 1)
                    tx = random.randint(0, len(self.maze[0]) - 1)
                    if self.maze[ty][tx] == 0:
                        self.patrol_target = (tx + 0.5, ty + 0.5)
                        break
            
            if self.patrol_target:
                target_x, target_y = self.patrol_target
            
        elif self.state == 'chase':
            speed = self.chase_speed
            target_x, target_y = player_pos
            
        elif self.state == 'attack':
            speed = self.attack_speed
            target_x, target_y = player_pos
            # 如果非常接近，触发恐怖画面
            if self.distance_to_player < 0.8:
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
            if 0 <= int(ny) < len(self.maze) and 0 <= int(nx) < len(self.maze[0]):
                if self.maze[int(ny)][int(nx)] == 0:
                    self.x = nx
                    self.y = ny
                else:
                    # 简单的滑动处理 (分别尝试 X 和 Y 轴移动)
                    if self.maze[int(self.y)][int(nx)] == 0:
                        self.x = nx
                    elif self.maze[int(ny)][int(self.x)] == 0:
                        self.y = ny
