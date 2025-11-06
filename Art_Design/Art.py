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


def cast_ray(px, py, angle, maze, max_depth=100):
	"""
	DDA-based raycast. Returns:
	  depth, hit_bool, hit_x, hit_y, map_x, map_y, side
	where side==0 indicates a vertical wall hit (x-side), side==1 horizontal (y-side).
	"""
	rayDirX = math.cos(angle)
	rayDirY = math.sin(angle)

	mapX = int(px)
	mapY = int(py)

	# length of ray from one x or y side to next x or y side
	deltaDistX = abs(1.0 / rayDirX) if rayDirX != 0 else 1e30
	deltaDistY = abs(1.0 / rayDirY) if rayDirY != 0 else 1e30

	# step and initial sideDist
	if rayDirX < 0:
		stepX = -1
		sideDistX = (px - mapX) * deltaDistX
	else:
		stepX = 1
		sideDistX = (mapX + 1.0 - px) * deltaDistX
	if rayDirY < 0:
		stepY = -1
		sideDistY = (py - mapY) * deltaDistY
	else:
		stepY = 1
		sideDistY = (mapY + 1.0 - py) * deltaDistY

	hit = False
	side = 0
	max_iter = int(max_depth * max(deltaDistX, deltaDistY)) + 5
	iter_count = 0
	while not hit and iter_count < max_iter:
		# jump to next map square, OR in x-direction, OR in y-direction
		if sideDistX < sideDistY:
			sideDistX += deltaDistX
			mapX += stepX
			side = 0
		else:
			sideDistY += deltaDistY
			mapY += stepY
			side = 1
		# bounds check
		if mapY < 0 or mapY >= len(maze) or mapX < 0 or mapX >= len(maze[0]):
			# went out of map
			break
		if maze[mapY][mapX] == 1:
			hit = True
			break
		iter_count += 1

	if not hit:
		# no wall hit within range
		# approximate hit at max depth
		hit_x = px + rayDirX * max_depth
		hit_y = py + rayDirY * max_depth
		return max_depth, False, hit_x, hit_y, mapX, mapY, side

	# calculate distance to the point of impact (perpendicular distance to avoid fish-eye)
	if side == 0:
		perpWallDist = (mapX - px + (1 - stepX) / 2) / (rayDirX if rayDirX != 0 else 1e-6)
	else:
		perpWallDist = (mapY - py + (1 - stepY) / 2) / (rayDirY if rayDirY != 0 else 1e-6)

	hit_x = px + rayDirX * perpWallDist
	hit_y = py + rayDirY * perpWallDist

	return perpWallDist, True, hit_x, hit_y, mapX, mapY, side


def main():
	pygame.init()
	# SCALE increases internal pixel density; set to 1 (original), 2 (double), or 3 (triple)
	SCALE = 2
	# FLOOR_STEP controls floor/ceiling sampling horizontal resolution.
	# Increase to 2-6 to reduce cost (bigger means faster but blockier).
	FLOOR_STEP = 4
	# By default use perspective (world-anchored) floor/ceiling rendering but render at reduced
	# vertical resolution and scale up for speed. REDUCE_FACTOR=2 renders at half height.
	USE_PERSPECTIVE_FLOOR = True
	REDUCE_FACTOR = 2
	# Visual tone adjustments to make floor/ceiling darker/more gloomy
	# 0.0..1.0 scale where 1.0 = original brightness
	FLOOR_BRIGHTNESS = 0.45
	CEIL_BRIGHTNESS = 0.15
	# DESATURATE: 0.0 = keep colors, 1.0 = fully grayscale
	DESATURATE = 0.35
	# Ceiling can have its own stronger desaturation factor
	CEIL_DESATURATE = 0.8
	screen_w, screen_h = 800 * SCALE, 480 * SCALE
	screen = pygame.display.set_mode((screen_w, screen_h))
	clock = pygame.time.Clock()

	# load wall textures from Art_Design/textures/ (if any)
	textures = []
	tex_dir = os.path.join(os.path.dirname(__file__), 'textures')
	floor_tex = None
	ceil_tex = None
	if os.path.isdir(tex_dir):
		# prefer files that contain 'eye' in the name so your provided eye image is used first
		files = [fn for fn in os.listdir(tex_dir) if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
		files.sort(key=lambda n: (0 if 'eye' in n.lower() else 1, n.lower()))
		for fn in files:
			try:
				surf = pygame.image.load(os.path.join(tex_dir, fn)).convert()
				# detect floor/ceiling by name
				lname = fn.lower()
				if 'floor' in lname:
					floor_tex = surf
				elif 'ceiling' in lname or 'ceil' in lname:
					ceil_tex = surf
				else:
					textures.append(surf)
			except Exception as e:
				print(f"Warning: failed loading texture {fn}: {e}")
	if textures:
		print(f"Loaded {len(textures)} wall texture(s) from {tex_dir}")
	if floor_tex:
		print('Loaded floor texture')
	if ceil_tex:
		print('Loaded ceiling texture')

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

	move_speed = 3.0 * SCALE
	rot_speed = 2.0

	fov = math.pi / 3
	half_fov = fov / 2
	num_rays = 200 * SCALE
	max_depth = 20
	wall_height = 120 * SCALE

	running = True
	frame_count = 0
	while running:
		dt = clock.tick(60) / 1000.0
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				running = False
			# (removed runtime F toggle; perspective floor is enabled by default)

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

		# render: floor & ceiling selection
		# If perspective floor is disabled (default), use fast tiling which is responsive.
		if USE_PERSPECTIVE_FLOOR and (floor_tex or ceil_tex):
			# Try to use numpy + surfarray for vectorized sampling (much faster than per-pixel Python loops)
			try:
				import numpy as np
			except Exception:
				print('numpy not available; disabling perspective floor')
				USE_PERSPECTIVE_FLOOR = False

		if USE_PERSPECTIVE_FLOOR and (floor_tex or ceil_tex):
			# prepare numpy-backed arrays for textures
			if floor_tex:
				ftw, fth = floor_tex.get_size()
				floor_tex_arr = pygame.surfarray.array3d(floor_tex)  # shape (w,h,3)
			else:
				floor_tex_arr = None
			if ceil_tex:
				ctw, cth = ceil_tex.get_size()
				ceil_tex_arr = pygame.surfarray.array3d(ceil_tex)
			else:
				ceil_tex_arr = None

			# direction vectors for left and right edge of the screen
			rayDirLeftX = math.cos(pa - half_fov)
			rayDirLeftY = math.sin(pa - half_fov)
			rayDirRightX = math.cos(pa + half_fov)
			rayDirRightY = math.sin(pa + half_fov)

			posZ = 0.5 * screen_h  # distance from camera to the projection plane

			# reduced-height rendering: build small buffers and scale up
			half_h = screen_h // 2
			reduced_h = max(1, half_h // REDUCE_FACTOR)
			cols = np.arange(screen_w)
			hor = cols / float(screen_w)
			dirX = rayDirRightX - rayDirLeftX
			dirY = rayDirRightY - rayDirLeftY

			# floor: small buffer (width, reduced_h, 3)
			if floor_tex_arr is not None:
				floor_small = np.zeros((screen_w, reduced_h, 3), dtype=np.uint8)
				for sy in range(reduced_h):
					screen_y = half_h + sy * REDUCE_FACTOR + REDUCE_FACTOR // 2
					p = screen_y - half_h
					if p == 0:
						p = 1e-6
					rowDistance = posZ / p
					leftX = rayDirLeftX + hor * dirX
					leftY = rayDirLeftY + hor * dirY
					floorX = px + rowDistance * leftX
					floorY = py + rowDistance * leftY
					tx = ((floorX - np.floor(floorX)) * ftw).astype(np.int64) % ftw
					ty = ((floorY - np.floor(floorY)) * fth).astype(np.int64) % fth
					colors = floor_tex_arr[tx, ty].astype(np.float32)
					shade = max(30, 255 - int(rowDistance * 8))
					mul = (shade / 255.0) * FLOOR_BRIGHTNESS
					# optional desaturation
					if DESATURATE > 0.0:
						# colors is (screen_w,3) so average over channel axis=1
						gray = colors.mean(axis=1, keepdims=True)
						colors = colors * (1.0 - DESATURATE) + gray * DESATURATE
					colors = (colors * mul).clip(0, 255).astype(np.uint8)
					floor_small[:, sy, :] = colors
				# create surface and scale up
				floor_surf = pygame.surfarray.make_surface(floor_small)
				floor_surf = pygame.transform.scale(floor_surf, (screen_w, half_h))
				# apply brightness tint via BLEND_MULT
				if FLOOR_BRIGHTNESS < 1.0:
					shade = pygame.Surface(floor_surf.get_size()).convert()
					v = int(255 * FLOOR_BRIGHTNESS)
					shade.fill((v, v, v))
					try:
						floor_surf.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)
					except Exception:
						pass
				screen.blit(floor_surf, (0, half_h))
			else:
				# solid color fallback
				pygame.draw.rect(screen, (50, 50, 50), (0, half_h, screen_w, half_h))

			# ceiling
			if ceil_tex_arr is not None:
				ceil_small = np.zeros((screen_w, reduced_h, 3), dtype=np.uint8)
				for sy in range(reduced_h):
					screen_y = sy * REDUCE_FACTOR + REDUCE_FACTOR // 2
					p = half_h - screen_y
					if p == 0:
						p = 1e-6
					rowDistance = posZ / p
					leftX = rayDirLeftX + hor * dirX
					leftY = rayDirLeftY + hor * dirY
					ceilingX = px + rowDistance * leftX
					ceilingY = py + rowDistance * leftY
					tx = ((ceilingX - np.floor(ceilingX)) * ctw).astype(np.int64) % ctw
					ty = ((ceilingY - np.floor(ceilingY)) * cth).astype(np.int64) % cth
					colors = ceil_tex_arr[tx, ty].astype(np.float32)
					shade = max(30, 255 - int(rowDistance * 8))
					mul = (shade / 255.0) * CEIL_BRIGHTNESS
					if CEIL_DESATURATE > 0.0:
						# colors is (screen_w,3) so average over channel axis=1
						gray = colors.mean(axis=1, keepdims=True)
						colors = colors * (1.0 - CEIL_DESATURATE) + gray * CEIL_DESATURATE
					colors = (colors * mul).clip(0, 255).astype(np.uint8)
					ceil_small[:, sy, :] = colors
				ceil_surf = pygame.surfarray.make_surface(ceil_small)
				ceil_surf = pygame.transform.scale(ceil_surf, (screen_w, half_h))
				if CEIL_BRIGHTNESS < 1.0:
					shade = pygame.Surface(ceil_surf.get_size()).convert()
					v = int(255 * CEIL_BRIGHTNESS)
					shade.fill((v, v, v))
					try:
						ceil_surf.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)
					except Exception:
						pass
				screen.blit(ceil_surf, (0, 0))
			else:
				pygame.draw.rect(screen, (100, 150, 200), (0, 0, screen_w, half_h))
		else:
			# fallback: tile existing textures or solid colors as before
			if ceil_tex:
				# tile the ceiling texture across top half
				tw, th = ceil_tex.get_size()
				# choose tile width (smaller tiles for more repetition)
				tile_w = min(256 * SCALE, tw)
				tile_h = max(16, int(tile_w * th / tw))
				scaled = pygame.transform.scale(ceil_tex, (tile_w, tile_h))
				for yy in range(0, screen_h // 2, tile_h):
					for xx in range(0, screen_w, tile_w):
						# apply darkness tint for atmosphere
						if CEIL_BRIGHTNESS < 1.0:
							sh = scaled.copy()
							shade = pygame.Surface(sh.get_size()).convert()
							v = int(255 * CEIL_BRIGHTNESS)
							shade.fill((v, v, v))
							try:
								sh.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)
							except Exception:
								pass
							screen.blit(sh, (xx, yy))
						else:
							screen.blit(scaled, (xx, yy))
			else:
				screen.fill((100, 150, 200))  # sky

			if floor_tex:
				# tile the floor texture across bottom half
				tw, th = floor_tex.get_size()
				# choose tile width
				tile_w = min(256 * SCALE, tw)
				tile_h = max(16, int(tile_w * th / tw))
				scaled = pygame.transform.scale(floor_tex, (tile_w, tile_h))
				for yy in range(screen_h // 2, screen_h, tile_h):
					for xx in range(0, screen_w, tile_w):
						# apply darkness tint for atmosphere
						if FLOOR_BRIGHTNESS < 1.0:
							sh = scaled.copy()
							shade = pygame.Surface(sh.get_size()).convert()
							v = int(255 * FLOOR_BRIGHTNESS)
							shade.fill((v, v, v))
							try:
								sh.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)
							except Exception:
								pass
							screen.blit(sh, (xx, yy))
						else:
							screen.blit(scaled, (xx, yy))
			else:
				pygame.draw.rect(screen, (50, 50, 50), (0, screen_h // 2, screen_w, screen_h // 2))

		ray_angle = pa - half_fov
		slice_w = int(screen_w / num_rays) + 1
		for r in range(num_rays):
			angle = ray_angle + (r / num_rays) * fov
			depth, hit, hx, hy, mpx, mpy, side = cast_ray(px, py, angle, maze, max_depth=max_depth)
			# simple fish-eye correction already handled by perp dist in DDA; still apply cosine to be safe
			depth *= math.cos(angle - pa)
			if depth <= 0: depth = 0.0001
			proj_height = min(int(wall_height / (depth + 0.0001) * 2), screen_h)
			x = int(r * (screen_w / num_rays))

			if hit and textures:
				# choose texture (use first texture so all walls show the eye image)
				tex = textures[0]
				tw, th = tex.get_size()
				# compute wall_x: where exactly wall was hit (fractional part within the tile)
				if side == 0:
					# vertical wall, use y coordinate
					wall_x = hy - math.floor(hy)
				else:
					# horizontal wall, use x coordinate
					wall_x = hx - math.floor(hx)
				# ensure 0..1
				wall_x = wall_x - math.floor(wall_x)
				u = int(wall_x * (tw - 1))
				try:
					col_surf = tex.subsurface((u, 0, 1, th)).copy()
					col_surf = pygame.transform.scale(col_surf, (slice_w, proj_height)).convert()
					# apply distance-based shading: nearer slices are brighter, far ones darker
					color_val = max(30, 255 - int(depth * 12))
					shade = pygame.Surface(col_surf.get_size()).convert()
					shade.fill((color_val, color_val, color_val))
					try:
						col_surf.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)
					except Exception:
						pass
					screen.blit(col_surf, (x, screen_h // 2 - proj_height // 2))
				except Exception:
					color_val = max(30, 255 - int(depth * 12))
					col = (color_val, color_val, color_val)
					pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2, slice_w, proj_height))
			else:
				color_val = max(0, 255 - int(depth * 12))
				col = (color_val, color_val, color_val)
				pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2, slice_w, proj_height))

		# mini-map
		mm_scale = 8 * SCALE
		for y in range(map_h):
			for x in range(map_w):
				rect = pygame.Rect(x * mm_scale, y * mm_scale, mm_scale - 1, mm_scale - 1)
				color = (200, 200, 200) if maze[y][x] == 1 else (30, 30, 30)
				pygame.draw.rect(screen, color, rect)
		# draw exit on mini-map (green)
		ex_rect = pygame.Rect(exit_x * mm_scale, exit_y * mm_scale, mm_scale - 1, mm_scale - 1)
		pygame.draw.rect(screen, (0, 200, 0), ex_rect)
		# player on mini-map
		pygame.draw.circle(screen, (255, 0, 0), (int(px * mm_scale), int(py * mm_scale)), max(2, 3 * SCALE))

		# debug: print integer player cell and exit cell on first frame
		if frame_count == 0:
			print(f"DEBUG: Player int cell: ({int(px)}, {int(py)}), Exit cell: ({exit_x}, {exit_y})")

		# check win condition: player reached exit cell
		if int(px) == exit_x and int(py) == exit_y:
			# draw a simple win overlay and wait for user to press a key or close the window
			font = pygame.font.SysFont(None, 64 * SCALE)
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