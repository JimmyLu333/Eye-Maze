import os
import pygame

# Simple procedural texture generator that draws creepy eyes + drips
# Saves three images into Art_Design/textures/

def make_eye_surface(size=(256, 256), bg=(30, 30, 30), eye_color=(200, 40, 40), accents=(10,10,10)):
    w, h = size
    surf = pygame.Surface((w, h))
    surf.fill(bg)

    cx, cy = w // 2, h // 2
    # sclera
    pygame.draw.ellipse(surf, (230, 230, 230), (cx - 90, cy - 50, 180, 100))
    # iris
    pygame.draw.circle(surf, eye_color, (cx, cy), 35)
    # pupil
    pygame.draw.circle(surf, (0, 0, 0), (cx, cy), 15)
    # highlights
    pygame.draw.circle(surf, (255, 255, 255), (cx - 10, cy - 10), 6)

    # add radial lines for veins / creep
    for i in range(20):
        a = i * (2 * 3.1415 / 20)
        x1 = cx + int(math_cos(a) * 40)
        y1 = cy + int(math_sin(a) * 40)
        x2 = cx + int(math_cos(a) * 80)
        y2 = cy + int(math_sin(a) * 80)
        pygame.draw.aaline(surf, (80, 10, 10), (x1, y1), (x2, y2))

    # dripping paint
    for dx in range(-60, 80, 30):
        rx = cx + dx
        for depth in range(4):
            ry = cy + 50 + depth * 10
            pygame.draw.circle(surf, (eye_color[0]//2, eye_color[1]//2, eye_color[2]//2), (rx, ry), 6 - depth)

    return surf

# small helpers to avoid importing math repeatedly
import math

def math_sin(a):
    return math.sin(a)

def math_cos(a):
    return math.cos(a)


def generate_all(out_dir):
    pygame.init()
    os.makedirs(out_dir, exist_ok=True)
    sizes = [(256, 256), (256, 256), (256, 256)]
    colors = [(200, 30, 30), (30, 180, 80), (30, 150, 140)]
    names = ['eye_red.png', 'eye_green.png', 'eye_teal.png']
    for sz, col, name in zip(sizes, colors, names):
        surf = make_eye_surface(size=sz, bg=(10,10,10), eye_color=col)
        path = os.path.join(out_dir, name)
        try:
            pygame.image.save(surf, path)
            print('Wrote', path)
        except Exception as e:
            print('Failed saving', path, e)
    pygame.quit()

if __name__ == '__main__':
    base = os.path.dirname(__file__)
    out = os.path.join(base, 'textures')
    generate_all(out)
