import pygame
import os


class FootstepManager:
    """管理游戏中的脚步声音效"""
    
    def __init__(self, sound_file='footsteps.wav', volume=0.5, interval=0.6):
        """
        初始化脚步声管理器
        
        Args:
            sound_file: 脚步声音频文件名
            volume: 音量 (0.0 到 1.0)
            interval: 脚步声播放间隔（秒）
        """
        pygame.mixer.init()
        
        self.footstep_sound = None
        self.footstep_timer = 0.0
        self.footstep_interval = interval
        self.was_moving = False
        
        # 尝试从多个路径加载音频文件
        possible_paths = [
            sound_file,  # 当前目录
            os.path.join('..', sound_file),  # 上级目录
            os.path.join(os.path.dirname(__file__), '..', sound_file),  # 相对于Music.py的上级目录
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', sound_file),  # 绝对路径
        ]
        
        for path in possible_paths:
            try:
                self.footstep_sound = pygame.mixer.Sound(path)
                self.footstep_sound.set_volume(volume)
                print(f"✅ 成功加载脚步声: {path}")
                break
            except:
                continue
        if not self.footstep_sound:
            print(f"⚠️ 警告：未找到脚步声音频文件 '{sound_file}'")
    
    def update(self, is_moving, dt):
        """
        更新脚步声状态
        
        Args:
            is_moving: 玩家是否正在移动
            dt: 距离上一帧的时间增量（秒）
        """
        if not self.footstep_sound:
            return
        
        if is_moving:
            # 刚开始移动时，立即播放第一步
            if not self.was_moving:
                # 停止之前可能还在播放的声音，避免重叠
                self.footstep_sound.stop()
                self.footstep_sound.play()
                self.footstep_timer = 0.0
            else:
                # 持续移动时，按节奏播放
                self.footstep_timer += dt
                if self.footstep_timer >= self.footstep_interval:
                    # 停止之前的声音，播放新的，避免重叠
                    self.footstep_sound.stop()
                    self.footstep_sound.play()
                    self.footstep_timer = 0.0
        else:
            # 停止移动时，立即停止声音并重置计时器
            if self.was_moving:
                self.footstep_sound.stop()
                self.footstep_timer = 0.0
        
        self.was_moving = is_moving
    
    def set_volume(self, volume):
        """设置音量 (0.0 到 1.0)"""
        if self.footstep_sound:
            self.footstep_sound.set_volume(volume)
    
    def set_interval(self, interval):
        """设置脚步声播放间隔（秒）"""
        self.footstep_interval = interval


class SoundManager:
    """游戏音效总管理器 - 统一管理所有音效"""
    
    def __init__(self):
        """初始化声音管理器"""
        pygame.mixer.init()
        
        # 脚步声管理器
        self.footstep_manager = FootstepManager(
            sound_file='footsteps.wav',
            volume=0.5,
            interval=0.6
        )
        
        # 未来可以在这里添加更多音效，例如：
        # self.ambient_sound = None  # 环境音
        # self.enemy_sound = None    # 敌人音效
        # self.win_sound = None      # 胜利音效
    
    def update_footsteps(self, is_moving, dt):
        """更新脚步声（对外接口）"""
        self.footstep_manager.update(is_moving, dt)
    
    def set_footstep_volume(self, volume):
        """设置脚步声音量"""
        self.footstep_manager.set_volume(volume)
    
    def set_footstep_interval(self, interval):
        """设置脚步声间隔"""
        self.footstep_manager.set_interval(interval)
    
    # 未来可以添加更多音效控制方法：
    # def play_ambient(self):
    #     """播放环境音"""
    #     pass
    # 
    # def play_enemy_sound(self):
    #     """播放敌人音效"""
    #     pass
    # 
    # def play_win_sound(self):
    #     """播放胜利音效"""
    #     pass
