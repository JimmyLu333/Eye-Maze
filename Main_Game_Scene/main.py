import math
import random
import cv2
import pygame
from eye_capture import EyeCapture   # 导入眼睛检测机制


def generate_maze(w, h):
    # simple randomized DFS maze (odd dimensions recommended)
    maze = [[1 for _ in range(w)] for _ in range(h)]

    def carve(x, y):
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < w and 0 < ny < h and maze[ny][nx] == 1:
                maze[ny - dy // 2][nx - dx // 2] = 0
                maze[ny][nx] = 0
                carve(nx, ny)

    # start at random odd cell
    sx = random.randrange(1, w, 2)
    sy = random.randrange(1, h, 2)
    maze[sy][sx] = 0
    carve(sx, sy)
    return maze


def cast_ray(px, py, angle, maze, max_depth=20, step=0.01):
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    depth = 0.0
    while depth < max_depth:
        depth += step
        x = px + cos_a * depth
        y = py + sin_a * depth
        ix, iy = int(x), int(y)
        if iy < 0 or iy >= len(maze) or ix < 0 or ix >= len(maze[0]):
            return depth, True
        if maze[iy][ix] == 1:
            return depth, True
    return max_depth, False


def main():
    pygame.init()
    screen_w, screen_h = 800, 480
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()

    # Initialize eye capture
    cap = cv2.VideoCapture(0)
    eye_mech = EyeCapture()
    font = pygame.font.SysFont(None, 36)   # 用于显示提示文字

    # maze params
    map_w, map_h = 21, 15  # odd sizes
    maze = generate_maze(map_w, map_h)

    # player
    px, py = 1.5, 1.5
    pa = 0.0

    move_speed = 3.0
    rot_speed = 2.0

    fov = math.pi / 3
    half_fov = fov / 2
    num_rays = 200
    max_depth = 20
    wall_height = 120

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            pa -= rot_speed * dt
        if keys[pygame.K_d]:
            pa += rot_speed * dt
        dx = math.cos(pa) * move_speed * dt
        dy = math.sin(pa) * move_speed * dt
        if keys[pygame.K_w]:
            nx, ny = px + dx, py + dy
            if maze[int(ny)][int(nx)] == 0:
                px, py = nx, ny
        if keys[pygame.K_s]:
            nx, ny = px - dx, py - dy
            if maze[int(ny)][int(nx)] == 0:
                px, py = nx, ny

        # 摄像头帧 + 眼睛检测
        ret, frame = cap.read()
        if not ret:
            print("The camera failed to read frame.")
            break
        state = eye_mech.update(frame)

        # render
        if state["blackout"]:
            screen.fill((0,0,0))   # 黑屏覆盖
        else:
            # 正常渲染迷宫
            screen.fill((100, 150, 200))  # sky
            pygame.draw.rect(screen, (50, 50, 50), (0, screen_h // 2, screen_w, screen_h // 2))

            ray_angle = pa - half_fov
            for r in range(num_rays):
                angle = ray_angle + (r / num_rays) * fov
                depth, hit = cast_ray(px, py, angle, maze, max_depth=max_depth)
                depth *= math.cos(angle - pa)
                if depth <= 0: depth = 0.0001
                proj_height = min(int(wall_height / (depth + 0.0001) * 2), screen_h)
                color_val = max(0, 255 - int(depth * 12))
                col = (color_val, color_val, color_val)
                x = int(r * (screen_w / num_rays))
                pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2,
                                               int(screen_w / num_rays) + 1, proj_height))

            # mini-map
            mm_scale = 8
            for y in range(map_h):
                for x in range(map_w):
                    rect = pygame.Rect(x * mm_scale, y * mm_scale, mm_scale - 1, mm_scale - 1)
                    color = (200, 200, 200) if maze[y][x] == 1 else (30, 30, 30)
                    pygame.draw.rect(screen, color, rect)
            pygame.draw.circle(screen, (255, 0, 0), (int(px * mm_scale), int(py * mm_scale)), 3)

        # 敌人提示
        if state["enemy"]:
            text = font.render("The monster is approaching!", True, (255,0,0))
            screen.blit(text, (20,20))

        pygame.display.flip()

    cap.release()
    pygame.quit()


if __name__ == '__main__':
    main()
