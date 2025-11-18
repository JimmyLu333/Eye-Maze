"""
main_with_blink.py

新的入口文件：在游戏循环中集成眨眼检测（EAR-based），不修改原有 `main.py`。

功能：
- 使用 `Main_Game_Scene.main` 中的 `generate_maze` 与 `cast_ray`（DDA）函数。
- 使用 `Main_Game_Scene.eye_capture.EyeCapture` 来检测眨眼；支持通过命令行调整阈值。
- 支持 `--no-camera`（在无摄像头时合成空帧）和 `--show-ear`（在屏幕上显示当前 EAR）。
"""

import os
import sys
import argparse
import time

# ensure package imports work
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from Main_Game_Scene.main import generate_maze, cast_ray
except Exception:
    # fallback: if direct import fails, try relative import
    try:
        from main import generate_maze, cast_ray
    except Exception:
        raise

try:
    from Main_Game_Scene import eye_capture
    EyeCapture = eye_capture.EyeCapture
except Exception:
    EyeCapture = None

import math
import random
import pygame

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-camera', action='store_true', help='Run without a physical camera')
    parser.add_argument('--show-ear', action='store_true', help='Display EAR (eye aspect ratio) overlay')
    parser.add_argument('--ear-threshold', type=float, default=0.20, help='EAR threshold for closed eye')
    parser.add_argument('--closed-frames', type=int, default=6, help='Number of consecutive closed frames to trigger')
    parser.add_argument('--cooldown', type=float, default=10.0, help='Cooldown (s) between enemy triggers')
    parser.add_argument('--blackout-time', type=float, default=2.0, help='Seconds of blackout after trigger')
    args = parser.parse_args()

    pygame.init()
    screen_w, screen_h = 800, 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    # camera setup (optional)
    try:
        import cv2
    except Exception:
        cv2 = None

    cap = None
    if not args.no_camera and cv2 is not None:
        try:
            cap = cv2.VideoCapture(0)
        except Exception:
            cap = None

    # Eye capture setup
    if EyeCapture is not None and not args.no_camera:
        eye = EyeCapture(ear_threshold=args.ear_threshold, closed_frames=args.closed_frames, cooldown=args.cooldown, blackout_time=args.blackout_time)
        print('Using mediapipe EyeCapture for blink detection')
    else:
        # minimal dummy capture with same interface
        class Dummy:
            def __init__(self):
                self.blackout = False
                self.enemy = False
                self.ear = None
            def update(self, frame):
                return {"blackout": self.blackout, "enemy": self.enemy, "ear": self.ear}
        eye = Dummy()
        if args.no_camera or EyeCapture is None:
            print('EyeCapture not available or --no-camera set; using DummyEyeCapture')

    # Maze and player
    map_w, map_h = 21, 15
    maze = generate_maze(map_w, map_h)
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
    frame_count = 0
    while running:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
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

        # read camera frame or synthesize
        if cap is not None:
            ret, frame = cap.read()
            if not ret:
                frame = None
        else:
            # synthesize small frame if mediapipe expects something
            try:
                import numpy as np
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
            except Exception:
                frame = None

        state = eye.update(frame)

        # render
        if state.get('blackout'):
            screen.fill((0,0,0))
        else:
            screen.fill((100,150,200))
            pygame.draw.rect(screen, (50,50,50), (0, screen_h//2, screen_w, screen_h//2))

            ray_angle = pa - half_fov
            for r in range(num_rays):
                angle = ray_angle + (r / num_rays) * fov
                depth, hit, hx, hy, mpx, mpy, side = cast_ray(px, py, angle, maze, max_depth=max_depth)
                depth *= math.cos(angle - pa)
                if depth <= 0:
                    depth = 0.0001
                proj_height = min(int(wall_height / (depth + 0.0001) * 2), screen_h)
                color_val = max(0, 255 - int(depth * 12))
                col = (color_val, color_val, color_val)
                x = int(r * (screen_w / num_rays))
                pygame.draw.rect(screen, col, (x, screen_h//2 - proj_height//2, int(screen_w/num_rays)+1, proj_height))

        # HUD: enemy warning
        if state.get('enemy'):
            txt = font.render('The monster is approaching!', True, (255,0,0))
            screen.blit(txt, (20,20))

        # optional EAR display
        if args.show_ear:
            ear_val = state.get('ear')
            s = f'EAR: {ear_val:.3f}' if ear_val is not None else 'EAR: --'
            txt = font.render(s, True, (255,255,255))
            screen.blit(txt, (20, 60))

        pygame.display.flip()
        frame_count += 1

    if cap is not None:
        cap.release()
    pygame.quit()


if __name__ == '__main__':
    main()
