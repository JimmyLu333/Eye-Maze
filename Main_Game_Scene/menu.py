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
                
                # 裁剪到屏幕大小（居中裁剪，向上偏移50像素）
                crop_x = (new_w - screen_width) // 2
                crop_y = (new_h - screen_height) // 2 + 50  # 向上偏移50像素（增加crop_y）
                # 确保不超出范围
                if crop_y + screen_height > new_h:
                    crop_y = new_h - screen_height
                self.background = scaled.subsurface((crop_x, crop_y, screen_width, screen_height)).copy()
                
                # 添加暗化效果以突出标题
                dark_overlay = pygame.Surface((screen_width, screen_height))
                dark_overlay.fill((0, 0, 0))
                dark_overlay.set_alpha(100)  # 透明度（0-255，越大越暗）
                self.background.blit(dark_overlay, (0, 0))
                
                # 添加上暗下亮的渐变效果
                gradient_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                for y in range(screen_height):
                    # 从上到下，alpha值从较大（暗）到0（不影响）
                    alpha = int(180 * (1 - y / screen_height))  # 上方最暗180，下方0（从120改为180）
                    pygame.draw.line(gradient_overlay, (0, 0, 0, alpha), (0, y), (screen_width, y))
                self.background.blit(gradient_overlay, (0, 0))
                
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
                # 放大标题图片到原来的1.3倍
                original_w, original_h = self.title_image.get_size()
                new_w = int(original_w * 1.3)
                new_h = int(original_h * 1.3)
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
        
        # 加载start按钮图片
        self.start_button_image = None
        start_paths = [
            'start4.png',
            os.path.join('menu_art', 'start4.png'),
            os.path.join(os.path.dirname(__file__), 'menu_art', 'start4.png'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'menu_art', 'start4.png'),
        ]
        
        for path in start_paths:
            try:
                self.start_button_image = pygame.image.load(path).convert_alpha()
                print(f"✅ 成功加载START按钮图片: {path}")
                break
            except:
                continue
        
        self.start_button = HorrorButton(
            button_x, button_y, button_width, button_height,
            "START", self.button_font, self.start_button_image
        )
        
        # 动画效果
        self.title_pulse = 0.0
        self.blood_drip_offset = 0.0
        self.glitch_time = 0.0
        self.glitch_offset_x = 0
        self.glitch_offset_y = 0
        self.glitch_active = False
    
    def update(self, dt):
        """更新动画效果"""
        # 标题脉动效果
        self.title_pulse += dt * 2.0
        
        # 血滴效果
        self.blood_drip_offset += dt * 50
        if self.blood_drip_offset > 20:
            self.blood_drip_offset = 0
        
        # 故障效果 - 随机触发
        import random
        self.glitch_time += dt
        if self.glitch_time > 0.1:  # 每0.1秒检查一次
            self.glitch_time = 0
            if random.random() < 0.15:  # 15%概率触发故障
                self.glitch_active = True
                self.glitch_offset_x = random.randint(-8, 8)
                self.glitch_offset_y = random.randint(-3, 3)
            else:
                self.glitch_active = False
                self.glitch_offset_x = 0
                self.glitch_offset_y = 0
        
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
            
            # 应用故障效果
            center_x = self.screen_width // 2
            center_y = 140
            
            if self.glitch_active:
                # 横向闪回效果 - 分割成水平条纹
                import random
                img_rect = scaled_image.get_rect(center=(center_x, center_y))
                
                # 分条纹绘制，每个条纹随机偏移（更细的条纹）
                strip_height = 2  # 每个条纹的高度（从8改为2，更细）
                img_height = scaled_image.get_height()
                img_width = scaled_image.get_width()
                
                for y in range(0, img_height, strip_height):
                    h = min(strip_height, img_height - y)
                    # 随机水平偏移
                    offset = random.randint(-12, 12)
                    
                    try:
                        strip = scaled_image.subsurface((0, y, img_width, h))
                        strip_rect = strip.get_rect()
                        strip_rect.x = img_rect.x + offset
                        strip_rect.y = img_rect.y + y
                        screen.blit(strip, strip_rect)
                    except:
                        pass
            else:
                # 正常绘制
                img_rect = scaled_image.get_rect(center=(center_x, center_y))
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
    
    def __init__(self, x, y, width, height, text, font, image=None):
        """
        初始化按钮
        
        Args:
            x, y: 按钮位置
            width, height: 按钮尺寸
            text: 按钮文字
            font: 字体对象
            image: 按钮图片（可选）
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.image = image
        self.is_hovered = False
        self.hover_intensity = 0.0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
    
    def update(self, dt):
        """更新按钮动画"""
        # 不再有动画效果
        pass
    
    def draw(self, screen):
        """绘制按钮"""
        # 如果有图片，直接绘制图片（不再有背景、边框、效果）
        if self.image:
            # 缩放图片到更小的尺寸
            img_w, img_h = self.image.get_size()
            # 保持宽高比，缩放到按钮宽度的50%（从80%改为50%）
            base_scale = 0.5
            # 悬停时稍微放大
            if self.is_hovered:
                base_scale = 0.55
            
            target_w = int(self.rect.width * base_scale)
            scale = target_w / img_w
            target_h = int(img_h * scale)
            scaled_img = pygame.transform.smoothscale(self.image, (target_w, target_h))
            
            img_rect = scaled_img.get_rect(center=self.rect.center)
            screen.blit(scaled_img, img_rect)
        else:
            # 备用：文字按钮
            text_surf = self.font.render(self.text, True, (200, 200, 200))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
    
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
