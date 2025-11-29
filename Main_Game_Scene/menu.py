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


class EyeMenu:
    """眼睛主题的暂停菜单 - 眨眼展开 + 多眼监视"""
    
    def __init__(self, screen_width=800, screen_height=600):
        """初始化眼睛菜单"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 菜单状态
        self.is_open = False
        self.is_animating = False
        self.open_progress = 0.0  # 0.0 = 完全闭眼, 1.0 = 完全睁眼（菜单展开）
        self.animation_speed = 4.0
        
        # 红色方块标签位置和尺寸
        self.tab_width = 120
        self.tab_height = 50
        self.tab_x_hidden = -90  # 隐藏时的X位置（在左侧，只露出一点）
        self.tab_x_hover = 0  # 悬停时的X位置（完全伸出）
        self.tab_x = self.tab_x_hidden  # 当前X位置
        self.tab_y = screen_height // 2 - self.tab_height // 2  # 垂直居中
        self.tab_rect = pygame.Rect(self.tab_x, self.tab_y, self.tab_width, self.tab_height)
        
        # 悬停动画
        self.hover_progress = 0.0  # 0 = 隐藏, 1 = 完全伸出
        self.hover_speed = 8.0
        self.is_hovering = False
        
        # 展开后的菜单尺寸（调整为适合屏幕的大小）
        self.menu_width = 400
        self.menu_height = min(500, screen_height - 80)  # 确保不超出屏幕
        
        # 音量滑块
        self.volume = 0.5
        self.dragging_volume = False
        
        # 按钮悬停状态
        self.hovered_button = None  # 'resume', 'restart', 'quit' 或 None
        
        # 加载MENU图片素材
        self.menu_image = None
        try:
            menu_img_path = os.path.join(os.path.dirname(__file__), 'menu_art', 'menu1.png')
            if not os.path.exists(menu_img_path):
                menu_img_path = os.path.join('menu_art', 'menu1.png')
            if os.path.exists(menu_img_path):
                self.menu_image = pygame.image.load(menu_img_path).convert_alpha()
                # 缩放图片以适应标签大小
                img_height = int(self.tab_height * 0.6)  # 图片高度为标签的60%
                img_width = int(self.menu_image.get_width() * (img_height / self.menu_image.get_height()))
                self.menu_image = pygame.transform.scale(self.menu_image, (img_width, img_height))
        except Exception as e:
            print(f"加载MENU图片失败: {e}")
        
        # 加载PAUSED图片素材
        self.paused_image = None
        try:
            paused_img_path = os.path.join(os.path.dirname(__file__), 'menu_art', 'paused.png')
            if not os.path.exists(paused_img_path):
                paused_img_path = os.path.join('menu_art', 'paused.png')
            if os.path.exists(paused_img_path):
                self.paused_image = pygame.image.load(paused_img_path).convert_alpha()
                # 缩放图片以适应菜单宽度
                img_width = int(self.menu_width * 0.45)  # 图片宽度为菜单的45%（从60%调小）
                img_height = int(self.paused_image.get_height() * (img_width / self.paused_image.get_width()))
                self.paused_image = pygame.transform.scale(self.paused_image, (img_width, img_height))
        except Exception as e:
            print(f"加载PAUSED图片失败: {e}")
        
        # 加载VOLUME图片素材
        self.volume_image = None
        try:
            volume_img_path = os.path.join(os.path.dirname(__file__), 'menu_art', 'volume.png')
            if not os.path.exists(volume_img_path):
                volume_img_path = os.path.join('menu_art', 'volume.png')
            if os.path.exists(volume_img_path):
                self.volume_image = pygame.image.load(volume_img_path).convert_alpha()
                # 缩放图片
                img_height = 20  # 固定高度
                img_width = int(self.volume_image.get_width() * (img_height / self.volume_image.get_height()))
                self.volume_image = pygame.transform.scale(self.volume_image, (img_width, img_height))
        except Exception as e:
            print(f"加载VOLUME图片失败: {e}")
        
        # 加载RESUME图片素材
        self.resume_image = None
        try:
            resume_img_path = os.path.join(os.path.dirname(__file__), 'menu_art', 'resume.png')
            if not os.path.exists(resume_img_path):
                resume_img_path = os.path.join('menu_art', 'resume.png')
            if os.path.exists(resume_img_path):
                self.resume_image = pygame.image.load(resume_img_path).convert_alpha()
                # 缩放图片以适应按钮宽度
                img_width = int(250 * 0.35)  # 按钮宽度的35%（从50%调小）
                img_height = int(self.resume_image.get_height() * (img_width / self.resume_image.get_width()))
                self.resume_image = pygame.transform.scale(self.resume_image, (img_width, img_height))
        except Exception as e:
            print(f"加载RESUME图片失败: {e}")
        
        # 加载RESTART图片素材
        self.restart_image = None
        try:
            restart_img_path = os.path.join(os.path.dirname(__file__), 'menu_art', 'restart.png')
            if not os.path.exists(restart_img_path):
                restart_img_path = os.path.join('menu_art', 'restart.png')
            if os.path.exists(restart_img_path):
                self.restart_image = pygame.image.load(restart_img_path).convert_alpha()
                # 缩放图片以适应按钮宽度
                img_width = int(250 * 0.35)  # 与RESUME保持一致
                img_height = int(self.restart_image.get_height() * (img_width / self.restart_image.get_width()))
                self.restart_image = pygame.transform.scale(self.restart_image, (img_width, img_height))
        except Exception as e:
            print(f"加载RESTART图片失败: {e}")
        
        # 加载QUIT图片素材
        self.quit_image = None
        try:
            quit_img_path = os.path.join(os.path.dirname(__file__), 'menu_art', 'quit.png')
            if not os.path.exists(quit_img_path):
                quit_img_path = os.path.join('menu_art', 'quit.png')
            if os.path.exists(quit_img_path):
                self.quit_image = pygame.image.load(quit_img_path).convert_alpha()
                # 缩放图片以适应按钮宽度
                img_width = int(250 * 0.25)  # 按钮宽度的25%（从35%调小）
                img_height = int(self.quit_image.get_height() * (img_width / self.quit_image.get_width()))
                self.quit_image = pygame.transform.scale(self.quit_image, (img_width, img_height))
        except Exception as e:
            print(f"加载QUIT图片失败: {e}")
        
        # 字体
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 36)
            self.label_font = pygame.font.Font(None, 24)
        except:
            self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
            self.button_font = pygame.font.SysFont('Arial', 36)
            self.label_font = pygame.font.SysFont('Arial', 24)
    
    def update(self, dt):
        """更新动画"""
        # 主菜单展开/折叠动画
        if self.is_animating:
            if self.is_open:
                self.open_progress += self.animation_speed * dt
                if self.open_progress >= 1.0:
                    self.open_progress = 1.0
                    self.is_animating = False
            else:
                self.open_progress -= self.animation_speed * dt
                if self.open_progress <= 0.0:
                    self.open_progress = 0.0
                    self.is_animating = False
        
        # 悬停动画（仅在菜单未打开时）
        if self.open_progress <= 0.1:
            # 检测鼠标是否在标签区域
            mouse_pos = pygame.mouse.get_pos()
            # 扩大检测区域，包括隐藏的部分（在左侧）
            hover_rect = pygame.Rect(0, self.tab_y, 150, self.tab_height)
            self.is_hovering = hover_rect.collidepoint(mouse_pos)
            
            # 更新悬停进度
            if self.is_hovering:
                self.hover_progress += self.hover_speed * dt
                if self.hover_progress > 1.0:
                    self.hover_progress = 1.0
            else:
                self.hover_progress -= self.hover_speed * dt
                if self.hover_progress < 0.0:
                    self.hover_progress = 0.0
            
            # 计算当前X位置
            self.tab_x = self.tab_x_hidden + (self.tab_x_hover - self.tab_x_hidden) * self._ease_out_cubic(self.hover_progress)
            self.tab_rect.x = self.tab_x
        
        # 检测按钮悬停（仅在菜单展开时）
        if self.open_progress > 0.9:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_button = None
            
            # 计算菜单位置
            progress = self.open_progress
            current_width = int(100 + (self.menu_width - 100) * progress)
            current_height = int(50 + (self.menu_height - 50) * progress)
            
            if progress > 0.5:
                target_x = (self.screen_width - self.menu_width) // 2
                target_y = (self.screen_height - self.menu_height) // 2
                transition = (progress - 0.5) / 0.5
                start_x = 0
                start_y = self.tab_y + (self.tab_height - current_height) // 2
                menu_x = int(start_x + (target_x - start_x) * transition)
                menu_y = int(start_y + (target_y - start_y) * transition)
            else:
                menu_x = 0
                menu_y = self.tab_y + (self.tab_height - current_height) // 2
            
            # 检测按钮悬停
            button_actions = ["resume", "restart", "quit"]
            button_y_start = menu_y + 240
            button_spacing = 80
            button_w = 220
            button_h = 60
            
            for i, action in enumerate(button_actions):
                btn_y = button_y_start + i * button_spacing
                btn_x = menu_x + (current_width - button_w) // 2
                btn_rect = pygame.Rect(btn_x, btn_y, button_w, button_h)
                
                if btn_rect.collidepoint(mouse_pos):
                    self.hovered_button = action
                    break
    
    def toggle(self):
        """切换菜单开关状态"""
        self.is_open = not self.is_open
        self.is_animating = True
    
    def close(self):
        """关闭菜单（收起）"""
        if self.is_open:
            self.is_open = False
            self.is_animating = True
    
    def draw(self, screen):
        """绘制菜单"""
        if self.open_progress <= 0.1:
            # 只显示红色方块标签
            self._draw_tab(screen)
        else:
            # 显示展开的菜单
            self._draw_expanded_menu(screen)
    
    def _draw_tab(self, screen):
        """绘制折叠时的白色方块标签"""
        # 白色方块背景
        tab_surface = pygame.Surface((self.tab_width, self.tab_height))
        tab_surface.fill((255, 255, 255))  # 白色
        
        # 绘制边框
        pygame.draw.rect(tab_surface, (200, 200, 200), tab_surface.get_rect(), 3)
        
        # 绘制MENU图片或文字
        if self.menu_image:
            # 使用图片
            img_rect = self.menu_image.get_rect(center=(self.tab_width // 2, self.tab_height // 2))
            tab_surface.blit(self.menu_image, img_rect)
        else:
            # 如果图片加载失败，使用文字
            menu_text = self.button_font.render("MENU", True, (255, 220, 220))
            text_rect = menu_text.get_rect(center=(self.tab_width // 2, self.tab_height // 2))
            tab_surface.blit(menu_text, text_rect)
        
        # 添加阴影效果
        shadow_surface = pygame.Surface((self.tab_width + 6, self.tab_height + 6), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 80))
        screen.blit(shadow_surface, (self.tab_x + 3, self.tab_y + 3))
        
        # 绘制标签
        screen.blit(tab_surface, (self.tab_x, self.tab_y))
    
    def _draw_expanded_menu(self, screen):
        """绘制展开的菜单"""
        progress = self._ease_out_cubic(self.open_progress)
        
        # 绘制背景遮罩层（让游戏画面变暗）
        if progress > 0.1:
            overlay_alpha = int(180 * progress)  # 最大透明度180，随展开进度增加
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            screen.blit(overlay, (0, 0))
        
        # 计算菜单尺寸
        current_width = int(100 + (self.menu_width - 100) * progress)
        current_height = int(50 + (self.menu_height - 50) * progress)
        
        # 菜单居中显示（完全展开后）
        if progress > 0.5:
            # 展开时逐渐移向屏幕中心
            target_x = (self.screen_width - self.menu_width) // 2
            target_y = (self.screen_height - self.menu_height) // 2
            transition = (progress - 0.5) / 0.5  # 0.5-1.0 映射到 0-1
            start_x = 0  # 从左侧开始
            start_y = self.tab_y + (self.tab_height - current_height) // 2
            menu_x = int(start_x + (target_x - start_x) * transition)
            menu_y = int(start_y + (target_y - start_y) * transition)
        else:
            # 前半段从标签位置开始（左侧）
            menu_x = 0
            menu_y = self.tab_y + (self.tab_height - current_height) // 2
        
        # 创建菜单表面
        menu_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        
        # 绘制灰色半透明背景
        bg_color = (128, 128, 128, 150)  # 灰色，透明度150（从200提高透明度）
        menu_surface.fill(bg_color)
        
        # 绘制白色边框
        border_color = (255, 255, 255)
        pygame.draw.rect(menu_surface, border_color, menu_surface.get_rect(), 2)  # 移除圆角
        
        # 菜单内容（展开超过60%时显示）
        if progress > 0.6:
            content_alpha = int(255 * min(1.0, (progress - 0.6) / 0.4))
            
            # 标题 "PAUSED" - 使用图片或文字
            if self.paused_image:
                # 使用图片
                paused_surface = self.paused_image.copy()
                paused_surface.set_alpha(content_alpha)
                title_x = (current_width - self.paused_image.get_width()) // 2
                menu_surface.blit(paused_surface, (title_x, 40))
            else:
                # 如果图片加载失败，使用文字
                title = self.title_font.render("PAUSED", True, (80, 40, 40))
                title.set_alpha(content_alpha)
                title_x = (current_width - title.get_width()) // 2
                menu_surface.blit(title, (title_x, 40))
            
            # 音量控制
            if progress > 0.75:
                self._draw_volume_slider(menu_surface, current_width, content_alpha)
            
            # 按钮
            if progress > 0.9:
                self._draw_buttons(menu_surface, current_width, content_alpha)
        
        # 绘制阴影
        shadow = pygame.Surface((current_width + 15, current_height + 15), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, int(60 * progress)))
        screen.blit(shadow, (menu_x + 8, menu_y + 8))
        
        # 绘制菜单
        screen.blit(menu_surface, (menu_x, menu_y))
    
    def _draw_volume_slider(self, surface, width, alpha):
        """绘制音量滑块"""
        slider_y = 120
        
        # "VOLUME"标签 - 使用图片或文字
        if self.volume_image:
            # 使用图片
            vol_surface = self.volume_image.copy()
            vol_surface.set_alpha(alpha)
            vol_label_x = (width - self.volume_image.get_width()) // 2
            surface.blit(vol_surface, (vol_label_x, slider_y))
        else:
            # 如果图片加载失败，使用文字
            vol_label = self.label_font.render("VOLUME", True, (80, 40, 40))
            vol_label.set_alpha(alpha)
            vol_label_x = (width - vol_label.get_width()) // 2
            surface.blit(vol_label, (vol_label_x, slider_y))
        
        # 滑块轨道
        track_x = 50
        track_y = slider_y + 35
        track_w = width - 100
        track_h = 8
        
        track_surf = pygame.Surface((track_w, track_h), pygame.SRCALPHA)
        track_surf.fill((50, 50, 50, alpha))  # 更深的灰色（从80改为50）
        surface.blit(track_surf, (track_x, track_y))
        
        # 已填充部分（血红色）
        filled_w = int(track_w * self.volume)
        filled_surf = pygame.Surface((filled_w, track_h), pygame.SRCALPHA)
        filled_surf.fill((160, 60, 60, alpha))
        surface.blit(filled_surf, (track_x, track_y))
        
        # 滑块把手（白色圆角小方块）
        handle_x = track_x + filled_w
        handle_y = track_y + track_h // 2
        
        handle_w = 20
        handle_h = 14  # 高度从20缩小到14，让上下变窄
        handle_surf = pygame.Surface((handle_w, handle_h), pygame.SRCALPHA)
        handle_rect = handle_surf.get_rect()
        # 绘制白色圆角矩形
        pygame.draw.rect(handle_surf, (255, 255, 255, alpha), handle_rect, border_radius=3)
        # 添加浅灰色边框（圆角）
        pygame.draw.rect(handle_surf, (200, 200, 200, alpha), handle_rect, 1, border_radius=3)
        
        surface.blit(handle_surf, (handle_x - handle_w // 2, handle_y - handle_h // 2))
        
        # 音量百分比
        vol_pct = self.label_font.render(f"{int(self.volume * 100)}%", True, (80, 40, 40))
        vol_pct.set_alpha(alpha)
        vol_pct_x = (width - vol_pct.get_width()) // 2
        surface.blit(vol_pct, (vol_pct_x, track_y + 25))
    
    def _draw_buttons(self, surface, width, alpha):
        """绘制按钮"""
        button_texts = ["RESUME", "RESTART", "QUIT"]
        button_actions = ["resume", "restart", "quit"]
        button_y_start = 240
        button_spacing = 80
        button_w = 220  # 从280缩小到220
        button_h = 60
        
        for i, btn_text in enumerate(button_texts):
            action = button_actions[i]
            
            # 根据悬停状态计算缩放比例
            scale = 1.1 if self.hovered_button == action else 1.0
            scaled_w = int(button_w * scale)
            scaled_h = int(button_h * scale)
            
            btn_y = button_y_start + i * button_spacing
            btn_x = (width - button_w) // 2
            
            # 调整位置使缩放居中
            scaled_x = btn_x - (scaled_w - button_w) // 2
            scaled_y = btn_y - (scaled_h - button_h) // 2
            
            # 按钮背景（灰色透明底，白色边框）
            btn_surf = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
            btn_rect = btn_surf.get_rect()
            # 灰色半透明背景
            pygame.draw.rect(btn_surf, (128, 128, 128, alpha), btn_rect)
            # 白色边框（移除圆角）
            pygame.draw.rect(btn_surf, (255, 255, 255, alpha), btn_rect, 1)
            
            # 按钮文字或图片
            image_to_use = None
            if btn_text == "RESUME" and self.resume_image:
                image_to_use = self.resume_image
            elif btn_text == "RESTART" and self.restart_image:
                image_to_use = self.restart_image
            elif btn_text == "QUIT" and self.quit_image:
                image_to_use = self.quit_image
            
            if image_to_use:
                # 使用图片并缩放
                original_w, original_h = image_to_use.get_size()
                scaled_img_w = int(original_w * scale)
                scaled_img_h = int(original_h * scale)
                img_surface = pygame.transform.scale(image_to_use, (scaled_img_w, scaled_img_h))
                img_surface.set_alpha(alpha)
                img_rect = img_surface.get_rect(center=btn_rect.center)
                btn_surf.blit(img_surface, img_rect)
            else:
                # 使用文字
                btn_text_surf = self.button_font.render(btn_text, True, (80, 40, 40))
                btn_text_surf.set_alpha(alpha)
                text_rect = btn_text_surf.get_rect(center=btn_rect.center)
                btn_surf.blit(btn_text_surf, text_rect)
            
            surface.blit(btn_surf, (scaled_x, scaled_y))
    
    def _ease_out_cubic(self, t):
        """三次缓动函数"""
        return 1 - pow(1 - t, 3)
    
    def handle_event(self, event):
        """处理事件"""
        if self.open_progress <= 0.1:
            # 折叠状态：检测点击标签
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 扩大点击区域，包括隐藏的部分（在左侧）
                click_rect = pygame.Rect(0, self.tab_y, 150, self.tab_height)
                if click_rect.collidepoint(event.pos):
                    self.toggle()
                    return 'open_menu'  # 返回特殊动作表示打开菜单
        else:
            # 展开状态 - 计算菜单位置（与绘制逻辑一致）
            progress = self.open_progress
            current_width = int(100 + (self.menu_width - 100) * progress)
            current_height = int(50 + (self.menu_height - 50) * progress)
            
            # 使用与绘制相同的位置计算
            if progress > 0.5:
                target_x = (self.screen_width - self.menu_width) // 2
                target_y = (self.screen_height - self.menu_height) // 2
                transition = (progress - 0.5) / 0.5
                start_x = 0  # 从左侧开始
                start_y = self.tab_y + (self.tab_height - current_height) // 2
                menu_x = int(start_x + (target_x - start_x) * transition)
                menu_y = int(start_y + (target_y - start_y) * transition)
            else:
                menu_x = 0  # 左侧
                menu_y = self.tab_y + (self.tab_height - current_height) // 2
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                menu_rect = pygame.Rect(menu_x, menu_y, current_width, current_height)
                
                # 点击菜单外部折叠并恢复游戏
                if not menu_rect.collidepoint(mx, my):
                    self.toggle()
                    return 'resume'  # 返回resume以恢复游戏状态
                
                # 完全展开时处理交互
                if progress >= 0.95:
                    # 检查按钮点击
                    button_actions = ["resume", "restart", "quit"]
                    button_y_start = menu_y + 240
                    button_spacing = 80
                    button_w = 280
                    button_h = 60
                    
                    for i, action in enumerate(button_actions):
                        btn_y = button_y_start + i * button_spacing
                        btn_x = menu_x + (current_width - button_w) // 2
                        btn_rect = pygame.Rect(btn_x, btn_y, button_w, button_h)
                        
                        if btn_rect.collidepoint(mx, my):
                            return action
                    
                    # 检查音量滑块
                    if progress > 0.75:
                        # 使用当前计算的menu_x（已考虑居中）
                        track_x = menu_x + 50
                        track_y = menu_y + 155
                        track_w = current_width - 100
                        
                        if track_y - 15 <= my <= track_y + 20:
                            if track_x <= mx <= track_x + track_w:
                                new_vol = (mx - track_x) / track_w
                                self.volume = max(0.0, min(1.0, new_vol))
                                self.dragging_volume = True
                                return 'volume_change'
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_volume = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_volume and progress > 0.75:
                    mx = event.pos[0]
                    
                    # 重新计算menu_x（与绘制逻辑一致）
                    current_width = int(100 + (self.menu_width - 100) * progress)
                    current_height = int(50 + (self.menu_height - 50) * progress)
                    
                    if progress > 0.5:
                        target_x = (self.screen_width - self.menu_width) // 2
                        target_y = (self.screen_height - self.menu_height) // 2
                        transition = (progress - 0.5) / 0.5
                        start_x = 0  # 从左侧开始
                        start_y = self.tab_y + (self.tab_height - current_height) // 2
                        menu_x = int(start_x + (target_x - start_x) * transition)
                    else:
                        menu_x = 0  # 左侧
                    
                    track_x = menu_x + 50
                    track_w = current_width - 100
                    
                    new_vol = (mx - track_x) / track_w
                    self.volume = max(0.0, min(1.0, new_vol))
                    return 'volume_change'
        
        return None
    
    def get_volume(self):
        """获取当前音量"""
        return self.volume
    
    def set_volume(self, volume):
        """设置音量"""
        self.volume = max(0.0, min(1.0, volume))


class PaperMenu:
    """纸张展开式暂停菜单"""
    
    def __init__(self, screen_width=800, screen_height=600):
        """初始化纸张菜单"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 菜单状态
        self.is_open = False
        self.is_animating = False
        self.open_progress = 0.0  # 0.0 = 完全折叠, 1.0 = 完全展开
        self.animation_speed = 3.0  # 展开速度
        
        # 书页角落位置（折叠时显示的小标签）
        self.tab_width = 80
        self.tab_height = 40
        self.tab_x = screen_width - self.tab_width - 20
        self.tab_y = 20
        self.tab_rect = pygame.Rect(self.tab_x, self.tab_y, self.tab_width, self.tab_height)
        
        # 展开后的菜单尺寸
        self.menu_width = 400
        self.menu_height = 500
        
        # 音量滑块
        self.volume = 0.5
        self.dragging_volume = False
        
        # 字体
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 36)
            self.label_font = pygame.font.Font(None, 24)
        except:
            self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
            self.button_font = pygame.font.SysFont('Arial', 36)
            self.label_font = pygame.font.SysFont('Arial', 24)
    
    def update(self, dt):
        """更新动画"""
        if self.is_animating:
            if self.is_open:
                # 展开动画
                self.open_progress += self.animation_speed * dt
                if self.open_progress >= 1.0:
                    self.open_progress = 1.0
                    self.is_animating = False
            else:
                # 折叠动画
                self.open_progress -= self.animation_speed * dt
                if self.open_progress <= 0.0:
                    self.open_progress = 0.0
                    self.is_animating = False
    
    def toggle(self):
        """切换菜单开关状态"""
        self.is_open = not self.is_open
        self.is_animating = True
    
    def draw(self, screen):
        """绘制菜单"""
        if self.open_progress <= 0.0:
            # 只显示书页角落标签
            self._draw_tab(screen)
        else:
            # 显示展开的菜单
            self._draw_expanded_menu(screen)
    
    def _draw_tab(self, screen):
        """绘制折叠时的书页角落标签"""
        # 背景（旧纸张颜色）
        pygame.draw.rect(screen, (240, 235, 220), self.tab_rect, border_radius=3)
        
        # 边框
        pygame.draw.rect(screen, (180, 170, 150), self.tab_rect, 2, border_radius=3)
        
        # 文字 "MENU"
        text = self.label_font.render("MENU", True, (80, 70, 60))
        text_rect = text.get_rect(center=self.tab_rect.center)
        screen.blit(text, text_rect)
        
        # 小折痕效果（右上角）
        pygame.draw.line(screen, (200, 190, 170), 
                        (self.tab_rect.right - 2, self.tab_rect.top + 2),
                        (self.tab_rect.right - 15, self.tab_rect.top + 15), 2)
    
    def _draw_expanded_menu(self, screen):
        """绘制展开的菜单"""
        # 使用缓动函数让动画更自然
        progress = self._ease_out_cubic(self.open_progress)
        
        # 计算当前尺寸
        current_width = int(self.tab_width + (self.menu_width - self.tab_width) * progress)
        current_height = int(self.tab_height + (self.menu_height - self.tab_height) * progress)
        
        # 创建菜单表面
        menu_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        
        # 绘制纸张背景
        menu_surface.fill((240, 235, 220))
        
        # 添加纸张噪点纹理
        if progress > 0.3:
            import random
            random.seed(42)  # 固定种子，保持纹理一致
            num_dots = int(200 * progress)
            for _ in range(num_dots):
                x = random.randint(0, current_width - 1)
                y = random.randint(0, current_height - 1)
                color = random.randint(220, 245)
                if 0 <= x < current_width and 0 <= y < current_height:
                    menu_surface.set_at((x, y), (color, color, color - 10))
        
        # 绘制边框
        pygame.draw.rect(menu_surface, (180, 170, 150), menu_surface.get_rect(), 3, border_radius=5)
        
        # 只在展开超过60%时显示内容
        if progress > 0.6:
            content_alpha = int(255 * min(1.0, (progress - 0.6) / 0.4))
            
            # 标题 "PAUSED"
            title = self.title_font.render("PAUSED", True, (80, 70, 60))
            title.set_alpha(content_alpha)
            title_x = (current_width - title.get_width()) // 2
            menu_surface.blit(title, (title_x, 30))
            
            # 音量控制（展开超过75%时显示）
            if progress > 0.75:
                slider_y = 100
                
                # "VOLUME"标签
                vol_label = self.label_font.render("VOLUME", True, (80, 70, 60))
                vol_label.set_alpha(content_alpha)
                vol_label_x = (current_width - vol_label.get_width()) // 2
                menu_surface.blit(vol_label, (vol_label_x, slider_y))
                
                # 滑块轨道
                track_x = 50
                track_y = slider_y + 35
                track_w = current_width - 100
                track_h = 6
                
                # 轨道背景
                track_surf = pygame.Surface((track_w, track_h), pygame.SRCALPHA)
                track_surf.fill((180, 170, 150))
                track_surf.set_alpha(content_alpha)
                menu_surface.blit(track_surf, (track_x, track_y))
                
                # 已填充部分
                filled_w = int(track_w * self.volume)
                filled_surf = pygame.Surface((filled_w, track_h), pygame.SRCALPHA)
                filled_surf.fill((150, 120, 90))
                filled_surf.set_alpha(content_alpha)
                menu_surface.blit(filled_surf, (track_x, track_y))
                
                # 滑块按钮
                handle_x = track_x + filled_w
                handle_y = track_y + track_h // 2
                handle_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(handle_surf, (120, 110, 90), (15, 15), 12)
                pygame.draw.circle(handle_surf, (80, 70, 60), (15, 15), 12, 2)
                handle_surf.set_alpha(content_alpha)
                menu_surface.blit(handle_surf, (handle_x - 15, handle_y - 15))
                
                # 音量百分比
                vol_pct = self.label_font.render(f"{int(self.volume * 100)}%", True, (80, 70, 60))
                vol_pct.set_alpha(content_alpha)
                vol_pct_x = (current_width - vol_pct.get_width()) // 2
                menu_surface.blit(vol_pct, (vol_pct_x, track_y + 20))
            
            # 按钮（完全展开时才显示）
            if progress > 0.9:
                button_texts = ["RESUME", "RESTART", "QUIT"]
                button_y_start = 220
                button_spacing = 80
                button_w = 280
                button_h = 60
                
                for i, btn_text in enumerate(button_texts):
                    btn_y = button_y_start + i * button_spacing
                    btn_x = (current_width - button_w) // 2
                    
                    # 按钮背景
                    btn_surf = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
                    btn_rect = btn_surf.get_rect()
                    pygame.draw.rect(btn_surf, (200, 190, 170), btn_rect, border_radius=5)
                    pygame.draw.rect(btn_surf, (120, 110, 90), btn_rect, 2, border_radius=5)
                    btn_surf.set_alpha(content_alpha)
                    
                    # 按钮文字
                    btn_text_surf = self.button_font.render(btn_text, True, (80, 70, 60))
                    text_rect = btn_text_surf.get_rect(center=btn_rect.center)
                    btn_surf.blit(btn_text_surf, text_rect)
                    
                    menu_surface.blit(btn_surf, (btn_x, btn_y))
        
        # 添加阴影
        shadow = pygame.Surface((current_width + 10, current_height + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, int(50 * progress)))
        screen.blit(shadow, (self.tab_x + 5, self.tab_y + 5))
        
        # 绘制菜单
        screen.blit(menu_surface, (self.tab_x, self.tab_y))
    
    def _ease_out_cubic(self, t):
        """三次缓动函数"""
        return 1 - pow(1 - t, 3)
    
    def handle_event(self, event):
        """处理事件"""
        if self.open_progress <= 0.1:
            # 折叠状态：检测点击标签
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.tab_rect.collidepoint(event.pos):
                    self.toggle()
                    return None
        else:
            # 展开状态
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                current_width = int(self.tab_width + (self.menu_width - self.tab_width) * self.open_progress)
                current_height = int(self.tab_height + (self.menu_height - self.tab_height) * self.open_progress)
                menu_rect = pygame.Rect(self.tab_x, self.tab_y, current_width, current_height)
                
                # 点击菜单外部折叠
                if not menu_rect.collidepoint(mx, my):
                    self.toggle()
                    return None
                
                # 完全展开时处理交互
                if self.open_progress >= 0.95:
                    # 检查按钮点击
                    button_texts = ["resume", "restart", "quit"]
                    button_y_start = self.tab_y + 220
                    button_spacing = 80
                    button_w = 280
                    button_h = 60
                    
                    for i, action in enumerate(button_texts):
                        btn_y = button_y_start + i * button_spacing
                        btn_x = self.tab_x + (current_width - button_w) // 2
                        btn_rect = pygame.Rect(btn_x, btn_y, button_w, button_h)
                        
                        if btn_rect.collidepoint(mx, my):
                            return action
                    
                    # 检查音量滑块点击
                    if self.open_progress > 0.75:
                        track_x = self.tab_x + 50
                        track_y = self.tab_y + 135
                        track_w = current_width - 100
                        track_h = 6
                        
                        if track_y - 15 <= my <= track_y + track_h + 15:
                            if track_x <= mx <= track_x + track_w:
                                new_vol = (mx - track_x) / track_w
                                self.volume = max(0.0, min(1.0, new_vol))
                                self.dragging_volume = True
                                return 'volume_change'
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_volume = False
            
            # 音量滑块拖动
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_volume and self.open_progress > 0.75:
                    mx = event.pos[0]
                    current_width = int(self.tab_width + (self.menu_width - self.tab_width) * self.open_progress)
                    track_x = self.tab_x + 50
                    track_w = current_width - 100
                    
                    new_vol = (mx - track_x) / track_w
                    self.volume = max(0.0, min(1.0, new_vol))
                    return 'volume_change'
        
        return None
    
    def get_volume(self):
        """获取当前音量"""
        return self.volume
    
    def set_volume(self, volume):
        """设置音量"""
        self.volume = max(0.0, min(1.0, volume))


class PauseMenu:
    """游戏暂停菜单"""
    
    def __init__(self, screen_width=800, screen_height=600):
        """初始化暂停菜单"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 字体
        try:
            self.title_font = pygame.font.Font(None, 72)
            self.button_font = pygame.font.Font(None, 36)
            self.label_font = pygame.font.Font(None, 28)
        except:
            self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
            self.button_font = pygame.font.SysFont('Arial', 36)
            self.label_font = pygame.font.SysFont('Arial', 28)
        
        # 菜单按钮
        button_width = 250
        button_height = 60
        center_x = screen_width // 2 - button_width // 2
        start_y = screen_height // 2 - 50
        spacing = 80
        
        self.resume_button = HorrorButton(
            center_x, start_y, button_width, button_height,
            "RESUME", self.button_font
        )
        
        self.restart_button = HorrorButton(
            center_x, start_y + spacing, button_width, button_height,
            "RESTART", self.button_font
        )
        
        self.quit_button = HorrorButton(
            center_x, start_y + spacing * 2, button_width, button_height,
            "QUIT", self.button_font
        )
        
        # 音量控制
        self.volume_slider_rect = pygame.Rect(
            center_x, start_y - 100,
            button_width, 20
        )
        self.volume_handle_radius = 12
        self.volume = 0.5  # 默认音量50%
        self.dragging_volume = False
    
    def update(self, dt):
        """更新菜单"""
        self.resume_button.update(dt)
        self.restart_button.update(dt)
        self.quit_button.update(dt)
    
    def draw(self, screen):
        """绘制暂停菜单"""
        # 半透明黑色背景
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 标题
        title_text = self.title_font.render("PAUSED", True, (200, 200, 200))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_text, title_rect)
        
        # 音量控制
        volume_label = self.label_font.render("Volume", True, (200, 200, 200))
        label_rect = volume_label.get_rect(center=(self.screen_width // 2, self.volume_slider_rect.y - 30))
        screen.blit(volume_label, label_rect)
        
        # 音量滑块背景
        pygame.draw.rect(screen, (80, 80, 80), self.volume_slider_rect)
        # 音量滑块填充
        filled_width = int(self.volume_slider_rect.width * self.volume)
        filled_rect = pygame.Rect(
            self.volume_slider_rect.x,
            self.volume_slider_rect.y,
            filled_width,
            self.volume_slider_rect.height
        )
        pygame.draw.rect(screen, (150, 50, 50), filled_rect)
        
        # 音量滑块手柄
        handle_x = self.volume_slider_rect.x + filled_width
        handle_y = self.volume_slider_rect.centery
        pygame.draw.circle(screen, (200, 200, 200), (handle_x, handle_y), self.volume_handle_radius)
        pygame.draw.circle(screen, (100, 100, 100), (handle_x, handle_y), self.volume_handle_radius, 2)
        
        # 音量百分比
        volume_text = self.label_font.render(f"{int(self.volume * 100)}%", True, (200, 200, 200))
        volume_text_rect = volume_text.get_rect(center=(self.screen_width // 2, self.volume_slider_rect.y + 45))
        screen.blit(volume_text, volume_text_rect)
        
        # 按钮
        self.resume_button.draw(screen)
        self.restart_button.draw(screen)
        self.quit_button.draw(screen)
    
    def handle_event(self, event):
        """
        处理事件
        
        Returns:
            str: 'resume', 'restart', 'quit' 或 None
        """
        # 音量滑块拖动
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                handle_x = self.volume_slider_rect.x + int(self.volume_slider_rect.width * self.volume)
                handle_y = self.volume_slider_rect.centery
                distance = math.sqrt((mouse_pos[0] - handle_x)**2 + (mouse_pos[1] - handle_y)**2)
                
                if distance <= self.volume_handle_radius:
                    self.dragging_volume = True
                elif self.volume_slider_rect.collidepoint(mouse_pos):
                    # 点击滑块直接跳转
                    relative_x = mouse_pos[0] - self.volume_slider_rect.x
                    self.volume = max(0.0, min(1.0, relative_x / self.volume_slider_rect.width))
                    self.dragging_volume = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_volume = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_volume:
                mouse_x = event.pos[0]
                relative_x = mouse_x - self.volume_slider_rect.x
                self.volume = max(0.0, min(1.0, relative_x / self.volume_slider_rect.width))
        
        # 按钮事件
        if self.resume_button.handle_event(event):
            return 'resume'
        if self.restart_button.handle_event(event):
            return 'restart'
        if self.quit_button.handle_event(event):
            return 'quit'
        
        return None
    
    def get_volume(self):
        """获取当前音量"""
        return self.volume
    
    def set_volume(self, volume):
        """设置音量"""
        self.volume = max(0.0, min(1.0, volume))


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
        
        # 创建眼睛主题暂停菜单
        self.eye_menu = EyeMenu(screen_width, screen_height)
        
        # 当前状态
        self.current_state = 'start'  # 'start', 'pause', None(游戏中)
    
    def update(self, dt):
        """更新菜单动画"""
        if self.current_state == 'start':
            self.start_screen.update(dt)
        elif self.current_state == 'pause':
            self.eye_menu.update(dt)
    
    def draw(self, screen):
        """绘制当前界面"""
        if self.current_state == 'start':
            self.start_screen.draw(screen)
        elif self.current_state == 'pause':
            self.eye_menu.draw(screen)
    
    def handle_event(self, event):
        """
        处理事件
        
        Returns:
            str: 'start_game', 'resume', 'restart', 'quit' 或 None
        """
        if self.current_state == 'start':
            if self.start_screen.start_button.handle_event(event):
                return 'start_game'
        elif self.current_state == 'pause':
            result = self.eye_menu.handle_event(event)
            if result:
                return result
        return None
    
    def show_start_screen(self):
        """显示开始界面"""
        self.current_state = 'start'
    
    def show_pause_menu(self):
        """显示暂停菜单"""
        self.current_state = 'pause'
    
    def hide(self):
        """隐藏菜单（进入游戏）"""
        self.current_state = None
    
    def is_active(self):
        """检查菜单是否激活"""
        return self.current_state is not None
    
    def get_volume(self):
        """获取暂停菜单的音量设置"""
        return self.eye_menu.get_volume()
    
    def set_volume(self, volume):
        """设置暂停菜单的音量"""
        self.eye_menu.set_volume(volume)
