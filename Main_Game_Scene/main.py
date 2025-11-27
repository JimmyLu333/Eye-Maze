import math
import random
import sys
import os
import argparse

import pygame

# 导入声音管理器
try:
	from Music_And_SFX.Music import SoundManager
except ImportError:
	try:
		sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
		from Music_And_SFX.Music import SoundManager
	except:
		print("⚠️ 警告：无法导入SoundManager，音效功能将不可用")
		SoundManager = None

# 导入菜单管理器
try:
	from Main_Game_Scene.menu import MenuManager
except ImportError:
	try:
		from menu import MenuManager
	except:
		print("⚠️ 警告：无法导入MenuManager，菜单功能将不可用")
		MenuManager = None

try:
	from Main_Game_Scene.eye_capture import EyeCapture
except Exception:
	try:
		from eye_capture import EyeCapture
	except Exception:
		EyeCapture = None

# maze generation and minimap helper moved to separate module for clarity
try:
	from Main_Game_Scene.maze import generate_maze, draw_minimap
except Exception:
	# fallback to relative import if package import fails
	from maze import generate_maze, draw_minimap


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


def _apply_blood_overlay(surf, droplets=6, alpha=80, seed=None):
	"""Apply a subtle procedural blood/smudge overlay to the given surface.
	This is a lightweight fallback so code paths that call this helper won't fail
	if a more advanced generator isn't present.
	"""
	try:
		import random as _rnd
		if seed is not None:
			_rnd.seed(seed)
		w, h = surf.get_size()
		overlay = pygame.Surface((w, h), pygame.SRCALPHA)
		for i in range(max(1, droplets)):
			rx = _rnd.randint(0, max(0, w - 1))
			ry = _rnd.randint(0, max(0, h - 1))
			r = _rnd.randint(3, max(4, min(w, h) // 8))
			col = (120, 0, 0, int(alpha))
			pygame.draw.circle(overlay, col, (rx, ry), r)
		# blend the overlay on top using additive alpha so it's subtle
		try:
			surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
		except Exception:
			surf.blit(overlay, (0, 0))
	except Exception:
		# non-fatal: if anything fails, silently continue
		return


def main():
	pygame.init()
	
	# 游戏状态控制
	game_state = 'menu'  # 'menu' 或 'playing'
	
	# CLI: allow optional no-camera and blink detection parameters
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument('--no-camera', action='store_true', help='Run without opening a physical camera')
	parser.add_argument('--ear-threshold', type=float, default=0.20, help='EAR threshold for closed eye')
	parser.add_argument('--closed-frames', type=int, default=6, help='Consecutive closed frames to trigger')
	parser.add_argument('--cooldown', type=float, default=10.0, help='Cooldown seconds between triggers')
	parser.add_argument('--blackout-time', type=float, default=2.0, help='Seconds of blackout after trigger')
	args, _ = parser.parse_known_args()
	# SCALE increases internal pixel density; set to 1 (original), 2 (double), or 3 (triple)
	SCALE = 1
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
	# Overlay brightness: 1.0 = unchanged, >1.0 makes the overlay text/brighter
	OVERLAY_BRIGHTNESS = 1.6
	screen_w, screen_h = 800 * SCALE, 600 * SCALE
	screen = pygame.display.set_mode((screen_w, screen_h))
	pygame.display.set_caption("Eye Maze")
	clock = pygame.time.Clock()
	
	# 初始化菜单管理器
	menu_manager = None
	if MenuManager:
		try:
			menu_manager = MenuManager(screen_w, screen_h)
			print("✅ 菜单系统初始化成功")
		except Exception as e:
			print(f"⚠️ 菜单系统初始化失败: {e}")
	
	# small persistent ESC hint in top-left (rendered each frame)
	try:
		esc_ui_font = pygame.font.SysFont(None, 18 * SCALE)
	except Exception:
		esc_ui_font = pygame.font.SysFont(None, 18)

	# load textures via the textures module (extracted to Main_Game_Scene/textures.py)
	try:
		import Main_Game_Scene.textures as textures_mod
	except Exception:
		# fallback: try importing as a local module
		import textures as textures_mod

	tex_dir = os.path.join(os.path.dirname(__file__), 'textures')
	tex_res = textures_mod.load_textures(tex_dir, overlay_brightness=OVERLAY_BRIGHTNESS)
	textures = tex_res.get('textures', [])
	floor_tex = tex_res.get('floor_tex')
	ceil_tex = tex_res.get('ceil_tex')
	overlay_candidate = tex_res.get('overlay_candidate')
	overlay_image = tex_res.get('overlay_image')
	official_anim_frames = tex_res.get('official_anim_frames')
	official_anim_durations = tex_res.get('official_anim_durations')

	# maze params
	map_w, map_h = 21, 15  # odd sizes
	maze = generate_maze(map_w, map_h)

	# camera / eye mech
	try:
		import cv2
	except Exception:
		cv2 = None

	if not args.no_camera and cv2 is not None:
		cap = cv2.VideoCapture(0)
	else:
		cap = None

	if args.no_camera or EyeCapture is None:
		class _DummyEye:
			"""Enhanced DummyEye for keyboard-driven blink simulation and debug panel.
			Attributes are intentionally public so the main loop can read/update them.
			"""
			def __init__(self):
				self.blackout = False
				self.enemy = False
				self.ear = 0.32
				self.consecutive_closed = 0
				self.blackout_frames = 0
				self.BLACKOUT_DURATION = max(1, int(args.blackout_time * 60))
				self.show_instructions = True

			def update(self, frame):
				# simulate a small EAR oscillation so tests that read ear can observe changes
				try:
					import math, pygame as _pg
					self.ear = 0.32 + 0.02 * math.sin(_pg.time.get_ticks() / 300.0)
				except Exception:
					self.ear = 0.32
				# decrement blackout frame counter if active
				if self.blackout_frames > 0:
					self.blackout_frames -= 1
					self.blackout = True
				else:
					self.blackout = False
				return {"blackout": self.blackout, "enemy": self.enemy, "ear": self.ear, "consecutive_closed": self.consecutive_closed}

		eye_mech = _DummyEye()
		print('EyeCapture not available or --no-camera set; using DummyEyeCapture (keyboard simulation enabled)')
	else:
		eye_mech = EyeCapture(ear_threshold=args.ear_threshold, closed_frames=args.closed_frames, cooldown=args.cooldown, blackout_time=args.blackout_time)
		print('Using EyeCapture for blink detection')

	# 初始化声音管理器
	sound_manager = None
	if SoundManager:
		try:
			sound_manager = SoundManager(
				music_file='background_music.mp3',
				music_volume=0.1
			)
			print("✅ 声音系统初始化成功")
			
			# 播放背景音乐（无限循环，2秒淡入）
			sound_manager.play_music(loops=-1, fade_ms=2000)
			
		except Exception as e:
			print(f"⚠️ 声音系统初始化失败: {e}")

	# player (initial position)
	px, py = 1.5, 1.5
	pa = 0.0

	# minimap state: track visited integer cells (minimap shown in top-left)
	visited_cells = set()
	visited_cells.add((int(px), int(py)))

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
	# build graffiti overlays (if any) using the textures helper
	try:
		graffiti_overlays = textures_mod.make_graffiti_overlays(textures, overlay_candidate, overlay_image, maze, start_ix, start_iy, overlay_brightness=OVERLAY_BRIGHTNESS, scale=SCALE)
	except Exception:
		graffiti_overlays = {}

	# if no adjacent wall, don't place graffiti (could extend to floor later)

	move_speed = 3.0 * SCALE
	rot_speed = 2.0

	fov = math.pi / 3
	half_fov = fov / 2
	num_rays = 200 * SCALE
	max_depth = 20
	wall_height = 120 * SCALE

	running = True
	frame_count = 0
	start_time = pygame.time.get_ticks()
	is_official = False
	# preferred handwritten font family names (try these in order, fall back to default)
	HANDWRITTEN_FONTS = ['Segoe Script', 'Brush Script MT', 'Bradley Hand', 'Kristen ITC', 'Comic Sans MS']

	def get_handwritten_font(size, bold=False):
		# pygame.font.SysFont will fall back to a default if the name isn't found,
		# but trying several common handwriting fonts increases the chance of a
		# handwriting-like appearance on the user's system.
		for name in HANDWRITTEN_FONTS:
			try:
				f = pygame.font.SysFont(name, size, bold=bold)
				# heuristic: if the returned font reports the same name or the name
				# appears in the family (best-effort), accept it. Otherwise continue.
				# Note: SysFont always returns a font object; this check is soft.
				return f
			except Exception:
				continue
		# fallback
		return pygame.font.SysFont(None, size, bold=bold)
	while running:
		dt = clock.tick(60) / 1000.0
		
		# 更新菜单动画
		if game_state == 'menu' and menu_manager:
			menu_manager.update(dt)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			
			# 菜单事件处理
			if game_state == 'menu' and menu_manager:
				action = menu_manager.handle_event(event)
				if action == 'start_game':
					game_state = 'playing'
					menu_manager.hide()
					print("🎮 游戏开始！")
					continue
			
			# 游戏中按 ESC 返回菜单
			elif game_state == 'playing' and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				game_state = 'menu'
				if menu_manager:
					menu_manager.show_start_screen()
				print("📋 返回菜单")
				continue
			# Debug-key handling for DummyEye (only when no camera / using Dummy)
			elif event.type == pygame.KEYDOWN:
				if (args.no_camera or EyeCapture is None) and hasattr(eye_mech, 'blackout_frames'):
					# E: 模拟眨眼触发黑屏
					if event.key == pygame.K_e:
						try:
							eye_mech.blackout_frames = eye_mech.BLACKOUT_DURATION
						except Exception:
							eye_mech.blackout_frames = int(args.blackout_time * 60)
						# debug trace for key press
						eye_mech.last_action = f'E pressed @ {pygame.time.get_ticks()}'
						print('[DEBUG] Simulated blink: blackout_frames set to', eye_mech.blackout_frames)
					# R: 切换 enemy 标志
					elif event.key == pygame.K_r:
						eye_mech.enemy = not getattr(eye_mech, 'enemy', False)
						eye_mech.last_action = f'R pressed @ {pygame.time.get_ticks()}'
						print('[DEBUG] Enemy toggled ->', eye_mech.enemy)
					# I: 切换说明显示
					elif event.key == pygame.K_i:
						eye_mech.show_instructions = not getattr(eye_mech, 'show_instructions', True)
					eye_mech.last_action = f'I pressed @ {pygame.time.get_ticks()}'
					print('[DEBUG] Instructions toggled ->', eye_mech.show_instructions)
		# (removed runtime F toggle; perspective floor is enabled by default)

		# 只在游戏进行时处理游戏逻辑
		if game_state == 'playing':
			keys = pygame.key.get_pressed()
			# also support direct key-state quit in case KEYDOWN events are missed
			try:
				if keys[pygame.K_ESCAPE]:
					running = False
					continue
			except Exception:
				# if something odd happens with key state, fall back to event handling
				pass
			if keys[pygame.K_a]:
				pa -= rot_speed * dt
			if keys[pygame.K_d]:
				pa += rot_speed * dt
			
			# 检测玩家移动
			is_moving = False
			dx = math.cos(pa) * move_speed * dt
			dy = math.sin(pa) * move_speed * dt
			if keys[pygame.K_w]:
				nx, ny = px + dx, py + dy
				if maze[int(ny)][int(nx)] == 0:
					px, py = nx, ny
					is_moving = True
			if keys[pygame.K_s]:
				nx, ny = px - dx, py - dy
				if maze[int(ny)][int(nx)] == 0:
					px, py = nx, ny
					is_moving = True

			# 更新脚步声
			if sound_manager:
				sound_manager.update_footsteps(is_moving, dt)		# record visited cells when player enters a new integer cell
		try:
			cur_cell = (int(px), int(py))
			if cur_cell not in visited_cells:
				visited_cells.add(cur_cell)
		except Exception:
			pass

		# camera frame + eye state
		if cap is not None:
			ret, frame = cap.read()
			if not ret:
				frame = None
		else:
			try:
				import numpy as np
				frame = np.zeros((480, 640, 3), dtype=np.uint8)
			except Exception:
				frame = None

		# obtain eye state (blackout/enemy/ear)
		try:
			state = eye_mech.update(frame)
		except Exception:
			state = {"blackout": False, "enemy": False, "ear": None}

		# if blackout triggered, show black screen this frame and skip heavy rendering
		if state.get('blackout'):
			# Announce blackout once when it starts (for debug visibility)
			try:
				if not getattr(eye_mech, '_debug_blackout_announced', False):
					print('[DEBUG] BLACKOUT started')
					eye_mech._debug_blackout_announced = True
			except Exception:
				pass
			screen.fill((0, 0, 0))
			pygame.display.flip()
			frame_count += 1
			continue

		# If using DummyEye, render debug panel on the right and show simulated data
		# panel will be 220px wide aligned to the right edge of the screen
		if (args.no_camera or EyeCapture is None) and hasattr(eye_mech, 'blackout_frames'):
			# ensure some attributes exist
			blackout_frames = getattr(eye_mech, 'blackout_frames', 0)
			consec = getattr(eye_mech, 'consecutive_closed', 0)
			ear_val = getattr(eye_mech, 'ear', None)
			enemy_flag = getattr(eye_mech, 'enemy', False)
			show_inst = getattr(eye_mech, 'show_instructions', True)
			# draw right panel
			panel_w = 220
			panel_x = screen_w - panel_w
			pygame.draw.rect(screen, (18, 18, 18), (panel_x, 0, panel_w, screen_h))
			try:
				# small helper for text
				def _draw_text(surf, text, x, y, size=20, col=(255,255,255)):
					f = pygame.font.SysFont(None, size)
					surf.blit(f.render(text, True, col), (x, y))
				_y = 12
				_draw_text(screen, 'Debug Blink 状态', panel_x + 12, _y, 22)
				_y += 34
				_draw_text(screen, f'BLACKOUT: {bool(blackout_frames>0)}', panel_x + 12, _y)
				_y += 24
				_draw_text(screen, f'blackout_frames: {int(blackout_frames)}', panel_x + 12, _y)
				_y += 24
				_draw_text(screen, f'EAR (sim): {ear_val:.3f}' if ear_val is not None else 'EAR: N/A', panel_x + 12, _y)
				_y += 24
				_draw_text(screen, f'Enemy flag: {enemy_flag}', panel_x + 12, _y)
				_y += 24
				_draw_text(screen, f'Consec closed: {consec}', panel_x + 12, _y)
				_y += 28
				_draw_text(screen, 'Keys: E=blink  R=enemy  I=tips', panel_x + 12, _y, 16, (200,200,200))
				_y += 24
				# last action display for debugging
				last_act = getattr(eye_mech, 'last_action', '')
				if last_act:
					_draw_text(screen, f'Last: {last_act}', panel_x + 12, _y, 14, (180,180,255))
			except Exception:
				pass

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
				# choose texture: if we're in the official level and an animated GIF was
				# provided, use the appropriate animation frame; otherwise use textures[0].
				if is_official and official_anim_frames:
					# choose current frame based on time and frame durations
					try:
						cur_ms = pygame.time.get_ticks() - start_time
						# accumulate durations to find frame index
						total = sum(official_anim_durations) if official_anim_durations else 100
						pos = cur_ms % total
						running = 0
						idx = 0
						for i, d in enumerate(official_anim_durations):
							running += d
							if pos < running:
								idx = i
								break
						tex = official_anim_frames[idx]
					except Exception:
						tex = official_anim_frames[0]
				else:
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
					# draw the wall slice
					screen.blit(col_surf, (x, screen_h // 2 - proj_height // 2))
					# if a graffiti overlay exists for this wall tile, draw its column on top
					try:
						if (mpx, mpy) in graffiti_overlays:
							over = graffiti_overlays[(mpx, mpy)]
							# extract matching column from overlay and scale to slice
							ov_col = over.subsurface((u, 0, 1, th)).copy()
							ov_col = pygame.transform.scale(ov_col, (slice_w, proj_height)).convert_alpha()
							# determine if we need to horizontally flip the overlay column so text reads correctly
							try:
								# determine flip by comparing wall tangent with player's right vector
								# wall tangent: side==0 -> (0,1) (y increases), side==1 -> (1,0) (x increases)
								# player's right vector = (-sin(pa), cos(pa))
								right_x = -math.sin(pa)
								right_y = math.cos(pa)
								flip_h = False
								# Previously we flipped when the dot was negative which produced
								# mirrored text for the player's normal view; invert the sign so
								# graffiti reads correctly from the player's perspective.
								if side == 0:
									# tangent (0,1) -> dot = right_y
									if right_y > 0:
										flip_h = True
								else:
									# tangent (1,0) -> dot = right_x
									if right_x > 0:
										flip_h = True
								# no per-column flip here; overlay surfaces are pre-oriented at
								# creation time so text reads correctly from the player's side.
							except Exception:
								pass
							screen.blit(ov_col, (x, screen_h // 2 - proj_height // 2))
					except Exception:
						pass
				except Exception:
					color_val = max(30, 255 - int(depth * 12))
					col = (color_val, color_val, color_val)
					pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2, slice_w, proj_height))
			else:
				color_val = max(0, 255 - int(depth * 12))
				col = (color_val, color_val, color_val)
				pygame.draw.rect(screen, col, (x, screen_h // 2 - proj_height // 2, slice_w, proj_height))

		# mini-map (moved to maze.draw_minimap) — always draw in top-left
		# reveal walls only locally around visited cells (radius=1)
		mm_rect = draw_minimap(screen, maze, px, py, exit_x, exit_y, SCALE, visited=visited_cells, show_walls=True, wall_reveal_radius=1)
		# If we're still in the tutorial (not official), show an objective UI centered beneath the mini-map
		if not is_official:
			try:
				# slightly smaller handwritten-style font for objective label and center it beneath the mini-map
				obj_font = get_handwritten_font(int(14 * SCALE), bold=True)
				txt_obj = obj_font.render('Objective: Exit the maze', True, (255, 255, 255))
				# center horizontally under the minimap and place a small vertical gap
				obj_x = mm_rect.left + (mm_rect.width - txt_obj.get_width()) // 2
				obj_y = mm_rect.bottom + int(6 * SCALE)
				# keep a small minimum top margin in case the map is very low
				if obj_y < 4 * SCALE:
					obj_y = 4 * SCALE
				screen.blit(txt_obj, (obj_x, obj_y))
			except Exception:
				pass

		# debug: print integer player cell and exit cell on first frame
		if frame_count == 0:
			print(f"DEBUG: Player int cell: ({int(px)}, {int(py)}), Exit cell: ({exit_x}, {exit_y})")

		# check win condition: player reached exit cell
		if int(px) == exit_x and int(py) == exit_y:
			# Show end-of-tutorial black result screen with elapsed time and a "Next Level" button.
			elapsed_ms = pygame.time.get_ticks() - start_time
			elapsed_s = elapsed_ms / 1000.0
			mins = int(elapsed_s // 60)
			secs = elapsed_s % 60
			# build message
			# English end-of-tutorial message (use English throughout the game)
			msg = (
				"You have understood the rules here. It will be drawn to sudden darkness..."
				" Now keep your eyes open, no matter how difficult it gets."
			)
			# fonts (prefer a handwritten-style system font)
			title_f = get_handwritten_font(48 * SCALE, bold=True)
			msg_f = get_handwritten_font(24 * SCALE)
			time_f = get_handwritten_font(36 * SCALE, bold=True)
			button_f = get_handwritten_font(30 * SCALE)
			in_end = True
			while in_end:
				for ev in pygame.event.get():
					if ev.type == pygame.QUIT:
						running = False
						in_end = False
						break
					# allow ESC to quit from the end screen as a convenience
					if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
						running = False
						in_end = False
						break
					if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
						mx, my = ev.pos
						# check button click
						if btn_rect.collidepoint(mx, my):
							# start official level: copy current maze and reset player/time
							maze = [row[:] for row in maze]
							px, py = 1.5, 1.5
							pa = 0.0
							start_time = pygame.time.get_ticks()
							frame_count = 0
							is_official = True
							# clear any graffiti overlays so the official level walls are
							# entirely the animated GIF (no text overlays)
							try:
								graffiti_overlays.clear()
							except Exception:
								graffiti_overlays = {}
							in_end = False
							break
				# render end screen
				screen.fill((0, 0, 0))
				# time
				time_surf = time_f.render(f"Completion time: {mins:d}:{secs:05.2f}", True, (255, 255, 255))
				tw, th = time_surf.get_size()
				screen.blit(time_surf, (screen_w // 2 - tw // 2, screen_h // 2 - 140 * SCALE))
				# message (wrap if needed)
				# naive split: split into lines of approx 40 chars
				lines = []
				line_len = 40
				for i in range(0, len(msg), line_len):
					lines.append(msg[i:i+line_len])
				for i, ln in enumerate(lines):
					ms = msg_f.render(ln, True, (220, 220, 220))
					screen.blit(ms, (screen_w // 2 - ms.get_width() // 2, screen_h // 2 - 80 * SCALE + i * (28 * SCALE)))
				# draw Next Level button
				btn_w, btn_h = 240 * SCALE, 64 * SCALE
				btn_x = screen_w // 2 - btn_w // 2
				btn_y = int(screen_h // 2 + 40 * SCALE)
				btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
				pygame.draw.rect(screen, (200, 200, 200), btn_rect)
				pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2)
				bt = button_f.render('Next Level', True, (10, 10, 10))
				screen.blit(bt, (btn_x + btn_w // 2 - bt.get_width() // 2, btn_y + btn_h // 2 - bt.get_height() // 2))
				pygame.display.flip()
				clock.tick(30)

			frame_count += 1
			# draw persistent ESC hint in top-right so players know they can quit anytime
			try:
				txt = esc_ui_font.render('× ESC', True, (255, 255, 255))
				pad = 6 * SCALE
				bg_w = txt.get_width() + pad * 2
				bg_h = txt.get_height() + pad * 2
				bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
				# semi-transparent black background
				bg.fill((0, 0, 0, 160))
				bg.blit(txt, (pad, pad))
				# position top-right with small margin
				screen.blit(bg, (screen_w - bg_w - 8 * SCALE, 8 * SCALE))
			except Exception:
				pass
		
		# 渲染菜单或游戏画面
		if game_state == 'menu' and menu_manager:
			menu_manager.draw(screen)
		
		pygame.display.flip()
	
	pygame.quit()


if __name__ == '__main__':
	main()


# -------------------------
# Debug helpers (placed at file bottom)
# These helpers are used by the DummyEye simulation and the in-game
# right-side debug panel. They are purposely appended at the end of
# the file so maintainers can quickly find and edit simulation helpers.
def _draw_text(surface, text, x, y, size=20, col=(255, 255, 255)):
	try:
		f = pygame.font.SysFont(None, size)
		surface.blit(f.render(text, True, col), (x, y))
	except Exception:
		# last-resort: ignore render failures
		pass

# End of file