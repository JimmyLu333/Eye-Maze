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


class BackgroundMusicManager:
    """管理游戏背景音乐"""
    
    def __init__(self, music_file='background_music.mp3', volume=0.3):
        """
        初始化背景音乐管理器
        
        Args:
            music_file: 背景音乐文件名 (支持 MP3, OGG, WAV)
            volume: 音量 (0.0 到 1.0)
        """
        pygame.mixer.init()
        
        self.is_loaded = False
        self.is_playing = False
        
        # 尝试从多个路径加载音乐文件
        possible_paths = [
            music_file,  # 当前目录
            os.path.join('..', music_file),  # 上级目录
            os.path.join(os.path.dirname(__file__), '..', music_file),  # 相对于Music.py的上级目录
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', music_file),  # 绝对路径
        ]
        
        for path in possible_paths:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                self.is_loaded = True
                print(f"✅ 成功加载背景音乐: {path}")
                break
            except Exception as e:
                continue
        
        if not self.is_loaded:
            print(f"⚠️ 警告：未找到背景音乐文件 '{music_file}'")
    
    def play(self, loops=-1, fade_ms=0):
        """
        播放背景音乐
        
        Args:
            loops: 循环次数 (-1 = 无限循环, 0 = 播放一次, 1 = 播放两次, ...)
            fade_ms: 淡入时间（毫秒）
        """
        if not self.is_loaded:
            return
        
        try:
            if fade_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops)
            self.is_playing = True
            print("🎵 背景音乐开始播放")
        except Exception as e:
            print(f"⚠️ 播放背景音乐失败: {e}")
    
    def stop(self, fade_ms=0):
        """
        停止背景音乐
        
        Args:
            fade_ms: 淡出时间（毫秒）
        """
        if not self.is_loaded:
            return
        
        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            self.is_playing = False
            print("🔇 背景音乐已停止")
        except Exception as e:
            print(f"⚠️ 停止背景音乐失败: {e}")
    
    def pause(self):
        """暂停背景音乐"""
        if self.is_loaded and self.is_playing:
            pygame.mixer.music.pause()
            print("⏸️ 背景音乐已暂停")
    
    def resume(self):
        """恢复播放背景音乐"""
        if self.is_loaded:
            pygame.mixer.music.unpause()
            print("▶️ 背景音乐已恢复")
    
    def set_volume(self, volume):
        """
        设置音量
        
        Args:
            volume: 音量 (0.0 到 1.0)
        """
        if self.is_loaded:
            pygame.mixer.music.set_volume(volume)
    
    def get_volume(self):
        """获取当前音量"""
        if self.is_loaded:
            return pygame.mixer.music.get_volume()
        return 0.0
    
    def is_music_playing(self):
        """检查音乐是否正在播放"""
        if self.is_loaded:
            return pygame.mixer.music.get_busy()
        return False


class HeartbeatManager:
    """管理心跳音效"""
    
    def __init__(self, sound_file='heart_beat.mp3', volume=1.0):
        """
        初始化心跳声管理器
        
        Args:
            sound_file: 心跳声音频文件名
            volume: 音量 (0.0 到 1.0)
        """
        pygame.mixer.init()
        
        self.heartbeat_sound = None
        self.is_playing = False
        
        # 尝试从多个路径加载音频文件
        possible_paths = [
            sound_file,  # 当前目录
            os.path.join('..', sound_file),  # 上级目录
            os.path.join(os.path.dirname(__file__), '..', sound_file),  # 相对于Music.py的上级目录
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', sound_file),  # 绝对路径
        ]
        
        for path in possible_paths:
            try:
                self.heartbeat_sound = pygame.mixer.Sound(path)
                self.heartbeat_sound.set_volume(volume)
                print(f"✅ 成功加载心跳声: {path}")
                break
            except:
                continue
        if not self.heartbeat_sound:
            print(f"⚠️ 警告：未找到心跳声音频文件 '{sound_file}'")
    
    def update(self, is_chasing):
        """
        更新心跳声状态
        
        Args:
            is_chasing: 怪物是否正在追逐玩家
        """
        if not self.heartbeat_sound:
            return
        
        if is_chasing:
            if not self.is_playing:
                self.heartbeat_sound.play(loops=-1)
                self.is_playing = True
        else:
            if self.is_playing:
                self.heartbeat_sound.stop()
                self.is_playing = False


class SoundManager:
    """游戏音效总管理器 - 统一管理所有音效"""
    
    def __init__(self, music_file='background_music.mp3', music_volume=0.3):
        """
        初始化声音管理器
        
        Args:
            music_file: 背景音乐文件名
            music_volume: 背景音乐音量 (0.0 到 1.0)
        """
        pygame.mixer.init()
        
        # 保存当前音量
        self.music_volume = music_volume
        
        # 脚步声管理器
        self.footstep_manager = FootstepManager(
            sound_file='footsteps.wav',
            volume=0.5,
            interval=0.6
        )
        
        # 背景音乐管理器
        self.music_manager = BackgroundMusicManager(
            music_file=music_file,
            volume=music_volume
        )
        
        # 心跳声管理器
        self.heartbeat_manager = HeartbeatManager(
            sound_file='heart_beat.mp3',
            volume=1.0
        )
        
        # 未来可以在这里添加更多音效，例如：
        # self.ambient_sound = None  # 环境音效
        # self.enemy_sound = None    # 敌人音效
        # self.win_sound = None      # 胜利音效
    
    def update_footsteps(self, is_moving, dt):
        """更新脚步声（对外接口）"""
        self.footstep_manager.update(is_moving, dt)

    def update_heartbeat(self, is_chasing):
        """更新心跳声（对外接口）"""
        self.heartbeat_manager.update(is_chasing)
    
    def set_footstep_volume(self, volume):
        """设置脚步声音量"""
        self.footstep_manager.set_volume(volume)
    
    def set_footstep_interval(self, interval):
        """设置脚步声间隔"""
        self.footstep_manager.set_interval(interval)
    
    # ===== 背景音乐控制方法 =====
    
    def play_music(self, loops=-1, fade_ms=1000):
        """
        播放背景音乐
        
        Args:
            loops: 循环次数 (-1 = 无限循环)
            fade_ms: 淡入时间（毫秒）
        """
        self.music_manager.play(loops, fade_ms)
    
    def stop_music(self, fade_ms=1000):
        """
        停止背景音乐
        
        Args:
            fade_ms: 淡出时间（毫秒）
        """
        self.music_manager.stop(fade_ms)
    
    def pause_music(self):
        """暂停背景音乐"""
        self.music_manager.pause()
    
    def resume_music(self):
        """恢复背景音乐"""
        self.music_manager.resume()
    
    def set_music_volume(self, volume):
        """设置背景音乐音量 (0.0 到 1.0)"""
        self.music_volume = volume
        self.music_manager.set_volume(volume)
    
    def get_music_volume(self):
        """获取背景音乐音量"""
        return self.music_volume
    
    def is_music_playing(self):
        """检查背景音乐是否正在播放"""
        return self.music_manager.is_music_playing()
    
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
