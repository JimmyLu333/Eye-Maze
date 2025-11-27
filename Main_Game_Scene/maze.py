import random
import pygame


def draw_minimap(screen, maze, px, py, exit_x, exit_y, scale=1, top_left=(0, 0), visited=None, show_walls=True, wall_reveal_radius=1):
    """Draw a fog-of-war minimap showing only visited cells and current position.

    - The map is initially black. Only cells in `visited` are shown as small markers.
    - The player's current cell is shown as a brighter red dot.

    Parameters:
      screen - pygame Surface
      maze - 2D list where 1=wall,0=free
      px,py - player float position
      exit_x, exit_y - exit coords (not revealed on this minimap)
      scale - global SCALE used by main
      top_left - (x,y) origin of minimap
      visited - set of (ix,iy) cells that have been visited

    Returns pygame.Rect for the minimap area.
    """
    if visited is None:
        visited = set()
    map_h = len(maze)
    map_w = len(maze[0]) if map_h > 0 else 0
    mm_scale = 8 * scale
    mm_w = map_w * mm_scale
    mm_h = map_h * mm_scale
    ox, oy = top_left
    mm_rect = pygame.Rect(ox, oy, mm_w, mm_h)
    # black background (fog)
    try:
        pygame.draw.rect(screen, (0, 0, 0), mm_rect)
    except Exception:
        pass

    # draw visited breadcrumbs as small dark-red squares
    dot_w = max(2, mm_scale // 3)
    for (vx, vy) in visited:
        try:
            vx_px = ox + vx * mm_scale + mm_scale // 2 - dot_w // 2
            vy_px = oy + vy * mm_scale + mm_scale // 2 - dot_w // 2
            pygame.draw.rect(screen, (120, 20, 20), (vx_px, vy_px, dot_w, dot_w))
        except Exception:
            pass

    # current player cell as bright red circle
    try:
        cur_ix, cur_iy = int(px), int(py)
        cx = ox + int(px * mm_scale)
        cy = oy + int(py * mm_scale)
        pygame.draw.circle(screen, (255, 0, 0), (cx, cy), max(2, 3 * scale))
    except Exception:
        pass

    # draw walls. If show_walls is True and wall_reveal_radius <= 0, draw all walls.
    # If wall_reveal_radius > 0, only reveal wall cells within radius of visited cells.
    wall_col = (40, 40, 40)
    try:
        if show_walls and (wall_reveal_radius is None or wall_reveal_radius <= 0):
            # draw all walls
            for y in range(map_h):
                for x in range(map_w):
                    if maze[y][x] == 1:
                        rx = ox + x * mm_scale
                        ry = oy + y * mm_scale
                        try:
                            pygame.draw.rect(screen, wall_col, (rx, ry, mm_scale - 1, mm_scale - 1))
                        except Exception:
                            pass
        elif show_walls and wall_reveal_radius and wall_reveal_radius > 0:
            # reveal walls only near visited cells
            walls_to_draw = set()
            r = int(wall_reveal_radius)
            for (vx, vy) in visited:
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        nx = vx + dx
                        ny = vy + dy
                        if 0 <= ny < map_h and 0 <= nx < map_w and maze[ny][nx] == 1:
                            walls_to_draw.add((nx, ny))
            for (wx, wy) in walls_to_draw:
                try:
                    rx = ox + wx * mm_scale
                    ry = oy + wy * mm_scale
                    pygame.draw.rect(screen, wall_col, (rx, ry, mm_scale - 1, mm_scale - 1))
                except Exception:
                    pass
    except Exception:
        pass

    return mm_rect



def generate_maze(w, h):
    """Generate a randomized DFS maze.

    Maze is a 2D list where 1 represents a wall and 0 represents empty space.
    Odd dimensions are recommended so corridors line up on odd indices.
    """
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
