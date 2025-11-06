import math
import random
import sys
import os

import pygame


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
	"""
	Ray-march until hit. Returns (depth, hit_bool, hit_x, hit_y).
	hit_x/hit_y are the precise world coordinates of the collision.
	"""
	sin_a = math.sin(angle)
	cos_a = math.cos(angle)
	depth = 0.0
	x = px
	y = py
	while depth < max_depth:
		depth += step
		x = px + cos_a * depth
		y = py + sin_a * depth
		ix, iy = int(x), int(y)
		if iy < 0 or iy >= len(maze) or ix < 0 or ix >= len(maze[0]):
			return depth, True, x, y
		if maze[iy][ix] == 1:
			return depth, True, x, y
	return max_depth, False, x, y


def main():
	pygame.init()
	screen_w, screen_h = 800, 480
	screen = pygame.display.set_mode((screen_w, screen_h))
	clock = pygame.time.Clock()

	# load wall textures from Art_Design/textures/ (if any)
	textures = []
	tex_dir = os.path.join(os.path.dirname(__file__), 'textures')
	if os.path.isdir(tex_dir):
		for fn in os.listdir(tex_dir):
			if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
				try:
					surf = pygame.image.load(os.path.join(tex_dir, fn)).convert()
					textures.append(surf)
				except Exception as e:
					print(f"Warning: failed loading texture {fn}: {e}")
	if textures:
		print(f"Loaded {len(textures)} wall texture(s) from {tex_dir}")

	# maze params
	map_w, map_h = 21, 15  # odd sizes
	maze = generate_maze(map_w, map_h)

	# player (initial position)
	px, py = 1.5, 1.5
	pa = 0.0

	# determine an exit cell: pick the empty cell farthest from the player start
	start_ix, start_iy = int(px), int(py)
	exit_x, exit_y = start_ix, start_iy
	max_dist2 = -1
	for y in range(map_h):
		for x in range(map_w):
			# skip walls and the start cell itself
			if maze[y][x] == 0 and not (x == start_ix and y == start_iy):
				d2 = (x - start_ix) ** 2 + (y - start_iy) ** 2
				if d2 > max_dist2:
					max_dist2 = d2
					exit_x, exit_y = x, y
	# if no other empty cell found (extremely unlikely), fall back to a corner
	if max_dist2 == -1:
		fallback = (map_w - 2, map_h - 2)
		if maze[fallback[1]][fallback[0]] == 0:
			exit_x, exit_y = fallback
		else:
			# find any empty cell
			for y in range(map_h):
				for x in range(map_w):
					if maze[y][x] == 0:
						exit_x, exit_y = x, y
						break
				else:
					continue
				break
	print(f"Exit set at: ({exit_x}, {exit_y}), start at: ({start_ix}, {start_iy})")

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

		# render
		screen.fill((100, 150, 200))  # sky
		pygame.draw.rect(screen, (50, 50, 50), (0, screen_h // 2, screen_w, screen_h // 2))

		ray_angle = pa - half_fov
		slice_w = int(screen_w / num_rays) + 1
		for r in range(num_rays):
			angle = ray_angle + (r / num_rays) * fov
			depth, hit, hx, hy = cast_ray(px, py, angle, maze, max_depth=max_depth)
			# simple fish-eye correction
			depth *= math.cos(angle - pa)
			if depth <= 0: depth = 0.0001
			proj_height = min(int(wall_height / (depth + 0.0001) * 2), screen_h)
			x = int(r * (screen_w / num_rays))

			if hit and textures:
				# sample texture column based on fractional hit coordinate
				tex = textures[r % len(textures)]
				tw, th = tex.get_size()
				# use fractional part of hit x coordinate as u; fallback to hit y
				frac = hx - math.floor(hx)
				if frac == 0:
					frac = hy - math.floor(hy)
				u = int(abs(frac) * (tw - 1))
				try:
					col_surf = tex.subsurface((u, 0, 1, th)).copy()
					col_surf = pygame.transform.scale(col_surf, (slice_w, proj_height))
					screen.blit(col_surf, (x, screen_h // 2 - proj_height // 2))
				except Exception:
					# if subsurface failed, fallback to flat shading
					color_val = max(0, 255 - int(depth * 12))
					col = (color_val, color_val, color_val)
					pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2, slice_w, proj_height))
			else:
				color_val = max(0, 255 - int(depth * 12))
				col = (color_val, color_val, color_val)
				pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2, slice_w, proj_height))

		# mini-map
		mm_scale = 8
		for y in range(map_h):
			for x in range(map_w):
				rect = pygame.Rect(x * mm_scale, y * mm_scale, mm_scale - 1, mm_scale - 1)
				color = (200, 200, 200) if maze[y][x] == 1 else (30, 30, 30)
				pygame.draw.rect(screen, color, rect)
		# draw exit on mini-map (green)
		ex_rect = pygame.Rect(exit_x * mm_scale, exit_y * mm_scale, mm_scale - 1, mm_scale - 1)
		pygame.draw.rect(screen, (0, 200, 0), ex_rect)
		# player on mini-map
		pygame.draw.circle(screen, (255, 0, 0), (int(px * mm_scale), int(py * mm_scale)), 3)

		# debug: print integer player cell and exit cell on first frame
		if frame_count == 0:
			print(f"DEBUG: Player int cell: ({int(px)}, {int(py)}), Exit cell: ({exit_x}, {exit_y})")

		# check win condition: player reached exit cell
		if int(px) == exit_x and int(py) == exit_y:
			# draw a simple win overlay and wait for user to press a key or close the window
			font = pygame.font.SysFont(None, 64)
			text = font.render('You escaped!', True, (255, 255, 255))
			tw, th = text.get_size()
			screen.blit(text, (screen_w // 2 - tw // 2, screen_h // 2 - th // 2))
			pygame.display.flip()
			print('Player reached exit — waiting for keypress or window close')
			waiting = True
			while waiting:
				for ev in pygame.event.get():
					if ev.type == pygame.QUIT:
						waiting = False
						running = False
						break
					if ev.type == pygame.KEYDOWN:
						waiting = False
						running = False
						break
				pygame.time.wait(100)

		frame_count += 1
		pygame.display.flip()

	pygame.quit()


if __name__ == '__main__':
	main()