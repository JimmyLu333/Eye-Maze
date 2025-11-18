import pygame
import sys


def draw_text(surface, text, x, y, font, color=(255, 255, 255)):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def main():
    pygame.init()
    WIDTH, HEIGHT = 880, 540
    RIGHT_PANEL_W = 220
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Debug Blink — 按 E 模拟眨眼黑屏')

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    bigfont = pygame.font.SysFont(None, 36)

    # simulated eye state
    blackout_frames = 0
    BLACKOUT_DURATION = 45  # frames (约 0.75s @60fps)
    ear = 0.32
    enemy = False
    consecutive_closed = 0

    show_instructions = True

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:
                    # 按 E 键模拟一次眨眼 -> 触发黑屏
                    blackout_frames = BLACKOUT_DURATION
                elif event.key == pygame.K_r:
                    enemy = not enemy
                elif event.key == pygame.K_i:
                    show_instructions = not show_instructions

        # update simulated EAR (轻微波动)
        import math
        ear = 0.32 + 0.02 * math.sin(pygame.time.get_ticks() / 300.0)

        if blackout_frames > 0:
            blackout_frames -= 1
            is_blackout = True
        else:
            is_blackout = False

        # 渲染主区域
        if is_blackout:
            screen.fill((0, 0, 0))
        else:
            # 背景格子
            screen.fill((40, 40, 40))
            for x in range(0, WIDTH - RIGHT_PANEL_W, 40):
                for y in range(0, HEIGHT, 40):
                    if (x // 40 + y // 40) % 2 == 0:
                        pygame.draw.rect(screen, (60, 60, 60), (x, y, 40, 40))

        # 右侧数据面板
        panel_x = WIDTH - RIGHT_PANEL_W
        pygame.draw.rect(screen, (20, 20, 20), (panel_x, 0, RIGHT_PANEL_W, HEIGHT))
        pygame.draw.line(screen, (80, 80, 80), (panel_x, 0), (panel_x, HEIGHT))

        # 标题
        draw_text(screen, 'Debug Blink 状态', panel_x + 12, 12, bigfont)

        y = 60
        draw_text(screen, f'BLACKOUT: {is_blackout}', panel_x + 12, y, font)
        y += 28
        draw_text(screen, f'blackout_frames: {blackout_frames}', panel_x + 12, y, font)
        y += 28
        draw_text(screen, f'EAR (sim): {ear:.3f}', panel_x + 12, y, font)
        y += 28
        draw_text(screen, f'Enemy flag: {enemy}', panel_x + 12, y, font)
        y += 28
        draw_text(screen, f'Consec closed: {consecutive_closed}', panel_x + 12, y, font)
        y += 32

        draw_text(screen, '按键说明:', panel_x + 12, y, font)
        y += 24
        draw_text(screen, 'E - 模拟眨眼 (触发黑屏)', panel_x + 12, y, font)
        y += 22
        draw_text(screen, 'R - 切换 enemy 标志', panel_x + 12, y, font)
        y += 22
        draw_text(screen, 'I - 开/关 说明', panel_x + 12, y, font)
        y += 22
        draw_text(screen, 'Esc - 退出', panel_x + 12, y, font)

        if show_instructions:
            draw_text(screen, '说明: 按 E 模拟眨眼并短暂黑屏', 12, HEIGHT - 28, font, (200, 200, 200))

        # FPS
        fps = clock.get_fps()
        draw_text(screen, f'FPS: {fps:.1f}', panel_x + 12, HEIGHT - 40, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
