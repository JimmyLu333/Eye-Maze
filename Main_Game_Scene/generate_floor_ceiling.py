import os
import pygame
import random

# Generate two eerie textures: ceiling_pattern.png and floor_pattern.png
# Ceiling: cobweb / dripping paint / hanging shapes (no eyes)
# Floor: cracked tiles / blood spatters / puddles

def make_ceiling(size=(512, 256)):
    w, h = size
    surf = pygame.Surface((w, h))
    surf.fill((30, 30, 40))

    # draw dripping stains and streaks
    for i in range(6):
        x = random.randint(0, w)
        width = random.randint(8, 40)
        pygame.draw.ellipse(surf, (50 + random.randint(-10,10), 10, 10), (x - width//2, random.randint(-20, h//4), width, random.randint(20, h//2)))
        # drips
        for d in range(random.randint(3,7)):
            dx = x + random.randint(-width//2, width//2)
            dy = random.randint(h//8, h)
            pygame.draw.line(surf, (40, 10, 10), (dx, dy - random.randint(10,40)), (dx, dy), 2)

    # cobwebs (thin lines)
    for c in range(12):
        cx = random.randint(0, w)
        cy = random.randint(0, h//2)
        for r in range(6):
            angle = r * (2 * 3.14159 / 6)
            ex = int(cx + (random.randint(40, 150) * pygame.math.Vector2(1,0).rotate_rad(angle).x))
            ey = int(cy + (random.randint(40, 150) * pygame.math.Vector2(0,1).rotate_rad(angle).y))
            pygame.draw.aaline(surf, (120,120,120), (cx, cy), (ex, ey))
        # arcs
        for arc in range(3):
            rect = pygame.Rect(cx - 10 - arc*12, cy - 10 - arc*12, 20 + arc*24, 20 + arc*24)
            pygame.draw.arc(surf, (100,100,110), rect, 0, 3.14159, 1)

    # subtle noise
    for _ in range(2000):
        x = random.randrange(w)
        y = random.randrange(h)
        surf.set_at((x,y), (20 + random.randint(-5,5), 20 + random.randint(-5,5), 30 + random.randint(-5,5)))

    return surf


def make_floor(size=(512, 256)):
    w, h = size
    surf = pygame.Surface((w, h))
    surf.fill((10, 10, 12))

    # cracked tile pattern
    tile_w = 64
    for tx in range(0, w, tile_w):
        for ty in range(0, h, tile_w):
            shade = 20 + random.randint(-6,6)
            pygame.draw.rect(surf, (shade, shade, shade), (tx, ty, tile_w - 2, tile_w - 2))
            # crack
            if random.random() < 0.6:
                start = (tx + random.randint(0, tile_w), ty + random.randint(0, tile_w))
                points = [start]
                for p in range(random.randint(2,5)):
                    points.append((points[-1][0] + random.randint(-20,20), points[-1][1] + random.randint(-20,20)))
                pygame.draw.lines(surf, (10, 10, 10), False, points, 2)

    # blood spatters
    for s in range(12):
        cx = random.randint(0, w)
        cy = random.randint(h//4, h)
        r = random.randint(8, 40)
        for i in range(20):
            angle = random.random() * 2 * 3.14159
            rr = r * random.random()
            x = int(cx + rr * pygame.math.Vector2(1,0).rotate_rad(angle).x)
            y = int(cy + rr * pygame.math.Vector2(0,1).rotate_rad(angle).y)
            if 0 <= x < w and 0 <= y < h:
                surf.set_at((x,y), (120 + random.randint(0,80), 0, 0))

    # subtle gloss/puddle
    for p in range(6):
        rx = random.randint(0, w - 80)
        ry = random.randint(h//2, h - 40)
        pygame.draw.ellipse(surf, (20,20,30), (rx, ry, random.randint(40,120), random.randint(10,40)))

    return surf

if __name__ == '__main__':
    pygame.init()
    base = os.path.dirname(__file__)
    out = os.path.join(base, 'textures')
    os.makedirs(out, exist_ok=True)
    ceil = make_ceiling((1024, 512))
    floor = make_floor((1024, 512))
    pygame.image.save(ceil, os.path.join(out, 'ceiling_pattern.png'))
    pygame.image.save(floor, os.path.join(out, 'floor_pattern.png'))
    print('Wrote ceiling_pattern.png and floor_pattern.png to', out)
    pygame.quit()
