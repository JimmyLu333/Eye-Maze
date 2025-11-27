import pygame
import os
import math


class StartScreen:
    """恐怖风格游戏开始界面"""
    
    def __init__(self, screen_width=800, screen_height=600):
        """
        初始化开始界面
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 加载背景图片
        self.background = None
        bg_paths = [
            os.path.join('Main_Game_Scene', 'menu_art', '1.jpg'),
            os.path.join('menu_art', '1.jpg'),
            os.path.join(os.path.dirname(__file__), 'menu_art', '1.jpg'),
        ]
        
        for path in bg_paths:
            try:
                self.background = pygame.image.load(path)
                # 保持宽高比缩放并裁剪
                img_w, img_h = self.background.get_size()
                screen_ratio = screen_width / screen_height
                img_ratio = img_w / img_h
                
                if screen_ratio > img_ratio:
                    # 屏幕更宽，以宽度为准
                    new_w = screen_width
                    new_h = int(screen_width / img_ratio)
                else:
                    # 屏幕更高，以高度为准
                    new_h = screen_height
                    new_w = int(screen_height * img_ratio)
                
                # 缩放图片
                scaled = pygame.transform.smoothscale(self.background, (new_w, new_h))
                
                # 裁剪到屏幕大小（居中裁剪）
                crop_x = (new_w - screen_width) // 2
                crop_y = (new_h - screen_height) // 2
                self.background = scaled.subsurface((crop_x, crop_y, screen_width, screen_height)).copy()
                
                print(f"✅ 成功加载开始界面背景: {path}")
                break
            except Exception as e:
                continue
        
        if not self.background:
            print(f"⚠️ 警告：未找到背景图片，使用纯色背景")
            self.background = pygame.Surface((screen_width, screen_height))
            self.background.fill((30, 30, 35))
        
        # 加载标题图片
        self.title_image = None
        title_paths = [
            'title2.png',
            os.path.join('menu_art', 'title2.png'),
            os.path.join(os.path.dirname(__file__), 'menu_art', 'title2.png'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu_art', 'title2.png'),
        ]
        
        for path in title_paths:
            try:
                self.title_image = pygame.image.load(path).convert_alpha()
                # 放大标题图片到原来的1.0倍
                original_w, original_h = self.title_image.get_size()
                new_w = int(original_w * 1.0)
                new_h = int(original_h * 1.0)
                self.title_image = pygame.transform.smoothscale(self.title_image, (new_w, new_h))
                print(f"✅ 成功加载标题图片: {path}")
                break
            except:
                continue
        
        if not self.title_image:
            print("⚠️ 警告：未找到标题图片 'TITLE.png'，使用文字标题")
        
        # 恐怖风格字体（备用）
        try:
            self.title_font = pygame.font.Font(None, 120)
            self.button_font = pygame.font.Font(None, 48)
        except:
            self.title_font = pygame.font.SysFont('Arial', 120, bold=True)
            self.button_font = pygame.font.SysFont('Arial', 48)
        
        # 开始按钮
        button_width = 300
        button_height = 80
        button_x = (screen_width - button_width) // 2
        button_y = screen_height - 200
        self.start_button = HorrorButton(
            button_x, button_y, button_width, button_height,
            "START", self.button_font
        )
        
        # 动画效果
        self.title_pulse = 0.0
        self.blood_drip_offset = 0.0
    
    def update(self, dt):
        """更新动画效果"""
        # 标题脉动效果
        self.title_pulse += dt * 2.0
        
        # 血滴效果
        self.blood_drip_offset += dt * 50
        if self.blood_drip_offset > 20:
            self.blood_drip_offset = 0
        
        # 更新按钮
        self.start_button.update(dt)
    
    def draw(self, screen):
        """绘制开始界面"""
        # 绘制背景
        screen.blit(self.background, (0, 0))
        
        # 绘制"MAZE"标题（恐怖风格）
        self._draw_horror_title(screen)
        
        # 绘制开始按钮
        self.start_button.draw(screen)
        
        # 底部提示文字
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("HOLD YOUR BREATH, THEY MIGHT HEAR YOU...", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        screen.blit(hint_text, hint_rect)
    
    def _draw_horror_title(self, screen):
        """绘制恐怖风格的标题"""
        # 如果有标题图片，直接使用图片
        if self.title_image:
            # 获取图片尺寸并缩放到合适大小
            img_width = self.title_image.get_width()
            img_height = self.title_image.get_height()
            
            # 设置最大宽度（屏幕宽度的70%）
            max_width = int(self.screen_width * 0.7)
            if img_width > max_width:
                scale = max_width / img_width
                new_width = max_width
                new_height = int(img_height * scale)
                scaled_image = pygame.transform.smoothscale(self.title_image, (new_width, new_height))
            else:
                scaled_image = self.title_image
            
            # 居中绘制
            img_rect = scaled_image.get_rect(center=(self.screen_width // 2, 140))
            screen.blit(scaled_image, img_rect)
        else:
            # 备用：使用文字标题
            title_text = "MAZE"
            
            # 计算脉动效果
            pulse = abs(math.sin(self.title_pulse)) * 5
            
            # 绘制多层阴影效果（模拟恐怖感）
            for i in range(5, 0, -1):
                shadow_color = (20 + i * 10, 20 + i * 10, 25 + i * 10)
                shadow_surf = self.title_font.render(title_text, True, shadow_color)
                shadow_rect = shadow_surf.get_rect(center=(self.screen_width // 2 + i * 2, 150 + i * 2))
                screen.blit(shadow_surf, shadow_rect)
            
            # 主标题（带血迹效果的黑色）
            title_surf = self.title_font.render(title_text, True, (30, 30, 35))
            title_rect = title_surf.get_rect(center=(self.screen_width // 2, 150))
            screen.blit(title_surf, title_rect)
    
    def _draw_blood_drips(self, screen, title_rect):
        """在标题周围绘制血滴效果"""
        blood_color = (80, 20, 20, 150)
        
        # 几个固定位置的血滴
        drip_positions = [
            (title_rect.left + 20, title_rect.bottom + int(self.blood_drip_offset)),
            (title_rect.right - 30, title_rect.bottom + int(self.blood_drip_offset * 0.7)),
            (title_rect.centerx - 50, title_rect.bottom + int(self.blood_drip_offset * 1.2)),
        ]
        
        for x, y in drip_positions:
            # 绘制小圆点模拟血滴
            for i in range(3):
                pygame.draw.circle(screen, (max(0, 80 - i * 20), 10, 10), 
                                 (x + i * 2, y + i * 5), max(1, 4 - i))


class HorrorButton:
    """恐怖风格按钮"""
    
    def __init__(self, x, y, width, height, text, font):
        """
        初始化按钮
        
        Args:
            x, y: 按钮位置
            width, height: 按钮尺寸
            text: 按钮文字
            font: 字体对象
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        self.hover_intensity = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
    
    def update(self, dt):
        """更新按钮动画"""
        # 悬停时的抖动效果
        if self.is_hovered:
            self.hover_intensity = min(1.0, self.hover_intensity + dt * 3)
            import random
            self.shake_offset_x = random.randint(-2, 2) if random.random() > 0.7 else 0
            self.shake_offset_y = random.randint(-2, 2) if random.random() > 0.7 else 0
        else:
            self.hover_intensity = max(0.0, self.hover_intensity - dt * 3)
            self.shake_offset_x = 0
            self.shake_offset_y = 0
    
    def draw(self, screen):
        """绘制按钮"""
        # 计算实际位置（带抖动）
        draw_rect = self.rect.copy()
        draw_rect.x += self.shake_offset_x
        draw_rect.y += self.shake_offset_y
        
        # 背景（半透明黑色，悬停时更亮）
        bg_alpha = int(150 + self.hover_intensity * 80)
        bg_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        bg_color = (40, 40, 45, bg_alpha)
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect())
        screen.blit(bg_surface, draw_rect.topleft)
        
        # 边框（带血迹效果）
        border_color = (100 + int(self.hover_intensity * 100), 50, 50)
        pygame.draw.rect(screen, border_color, draw_rect, 3)
        
        # 文字（悬停时颜色变化）
        text_color = (200, 200, 200) if not self.is_hovered else (255, 100, 100)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_surf, text_rect)
        
        # 悬停时的血迹效果
        if self.is_hovered and self.hover_intensity > 0.5:
            self._draw_blood_splatter(screen, draw_rect)
    
    def _draw_blood_splatter(self, screen, rect):
        """在按钮边缘绘制血迹效果"""
        import random
        for i in range(5):
            x = random.randint(rect.left, rect.right)
            y = random.choice([rect.top, rect.bottom])
            radius = random.randint(2, 4)
            color = (80 + random.randint(0, 30), 10, 10)
            pygame.draw.circle(screen, color, (x, y), radius)
    
    def handle_event(self, event):
        """
        处理事件
        
        Returns:
            bool: True 表示按钮被点击
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False


class MenuManager:
    """菜单管理器"""
    
    def __init__(self, screen_width=800, screen_height=600):
        """
        初始化菜单管理器
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 创建开始界面
        self.start_screen = StartScreen(screen_width, screen_height)
        
        # 当前状态
        self.current_state = 'start'  # 'start', None(游戏中)
    
    def update(self, dt):
        """更新菜单动画"""
        if self.current_state == 'start':
            self.start_screen.update(dt)
    
    def draw(self, screen):
        """绘制当前界面"""
        if self.current_state == 'start':
            self.start_screen.draw(screen)
    
    def handle_event(self, event):
        """
        处理事件
        
        Returns:
            str: 'start_game' 或 None
        """
        if self.current_state == 'start':
            if self.start_screen.start_button.handle_event(event):
                return 'start_game'
        return None
    
    def show_start_screen(self):
        """显示开始界面"""
        self.current_state = 'start'
    
    def hide(self):
        """隐藏菜单（进入游戏）"""
        self.current_state = None
    
    def is_active(self):
        """检查菜单是否激活"""
        return self.current_state is not None
