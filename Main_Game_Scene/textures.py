import os
import pygame
import random
import json
from utils import resource_path

def _apply_blood_overlay(surf, droplets=6, alpha=80, seed=None):
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
        try:
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        except Exception:
            surf.blit(overlay, (0, 0))
    except Exception:
        return


def load_textures(tex_dir, overlay_brightness=1.0):
    """Load textures from tex_dir. Returns a dict with keys:
    textures (list), floor_tex, ceil_tex, overlay_candidate, overlay_image,
    official_anim_frames, official_anim_durations
    """
    textures = []
    floor_tex = None
    ceil_tex = None
    floor_src = None
    ceil_src = None
    overlay_candidate = None
    overlay_image = None
    official_anim_frames = None
    official_anim_durations = None

    # Load optional manifest for exact resource list
    manifest_path = resource_path(os.path.join('resources', 'texture_manifest.json'))
    manifest_list = None
    try:
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as mf:
                data = json.load(mf)
                if isinstance(data, dict):
                    manifest_list = data.get('textures')
    except Exception:
        manifest_list = None

    # Debug: report manifest usage and resolved manifest path
    try:
        if manifest_list:
            print(f"[debug] Using texture manifest: {manifest_path} (entries={len(manifest_list)})")
        else:
            print(f"[debug] No texture manifest found at: {manifest_path}")
    except Exception:
        pass

    # Resolve tex_dir for both dev and bundled runtimes
    try:
        resolved_tex_dir = resource_path(tex_dir)
        tex_dir = resolved_tex_dir
    except Exception:
        resolved_tex_dir = tex_dir
        try:
            tex_dir = resource_path(tex_dir)
        except Exception:
            pass

    if not os.path.isdir(tex_dir) and not manifest_list:
        return {
            'textures': textures,
            'floor_tex': floor_tex,
            'ceil_tex': ceil_tex,
            'overlay_candidate': overlay_candidate,
            'overlay_image': overlay_image,
            'official_anim_frames': official_anim_frames,
            'official_anim_durations': official_anim_durations,
        }

    wall_candidates = []
    # If manifest provided, load files listed there (in order). Skip non-image entries.
    gif_manifest = []
    if manifest_list:
        for rel in manifest_list:
            lname = rel.lower()
            try:
                p = resource_path(rel)
            except Exception:
                p = rel
            # Fallback: if manifest entry didn't resolve, try basename in the resolved tex_dir
            if not os.path.exists(p):
                try:
                    fallback = os.path.join(resolved_tex_dir, os.path.basename(rel))
                    if os.path.exists(fallback):
                        try:
                            print(f"[debug] manifest fallback used: {fallback}")
                        except Exception:
                            pass
                        p = fallback
                except Exception:
                    pass
            try:
                print(f"[debug] manifest entry resolved: {rel} -> {p}")
            except Exception:
                pass
            if not os.path.exists(p):
                print(f"Warning: manifest resource not found: {rel} (resolved {p})")
                continue
            # Image files
            if lname.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                try:
                    raw = pygame.image.load(p)
                    fn = os.path.basename(p)
                    try:
                        print(f"[debug] loaded image (manifest): {p} -> fn={fn} size={raw.get_size()} flags={raw.get_flags()}")
                    except Exception:
                        pass
                    if fn.lower().endswith('.png'):
                        surf = raw.convert_alpha()
                    else:
                        surf = raw.convert()

                    try:
                        if 'eyes' in fn.lower():
                            EYES_DARKEN = 0.35
                            v = max(0, min(255, int(255 * EYES_DARKEN)))
                            dark = pygame.Surface(surf.get_size(), pygame.SRCALPHA).convert_alpha()
                            dark.fill((v, v, v, 255))
                            try:
                                surf.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            except Exception:
                                surf.blit(dark, (0, 0))
                    except Exception:
                        pass

                    if any(k in fn.lower() for k in ('trust', 'text', 'graff', 'overlay')):
                        overlay_image = surf
                        continue

                    # For floor/ceiling textures we prefer an opaque surface so
                    # any PNG alpha does not make the rendered floor appear
                    # transparent in bundled runtimes. Composite alpha onto
                    # an opaque surface and convert to a non-alpha format.
                    if 'floor' in fn.lower():
                        floor_src = p
                        try:
                            if surf.get_flags() & pygame.SRCALPHA:
                                tmp = pygame.Surface(surf.get_size())
                                tmp.blit(surf, (0, 0))
                                floor_tex = tmp.convert()
                            else:
                                floor_tex = surf.convert()
                        except Exception:
                            floor_tex = surf
                    elif 'ceiling' in fn.lower() or 'ceil' in fn.lower():
                        ceil_src = p
                        try:
                            if surf.get_flags() & pygame.SRCALPHA:
                                tmp2 = pygame.Surface(surf.get_size())
                                tmp2.blit(surf, (0, 0))
                                ceil_tex = tmp2.convert()
                            else:
                                ceil_tex = surf.convert()
                        except Exception:
                            ceil_tex = surf
                    else:
                        wall_candidates.append((fn, surf))
                except Exception as e:
                    print(f"Warning: failed loading texture {rel}: {e}")
            elif lname.endswith('.gif'):
                gif_manifest.append(rel)

    else:
        files = [fn for fn in os.listdir(tex_dir) if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        files.sort(key=lambda n: (0 if 'eyes' in n.lower() else (1 if 'eye' in n.lower() else 2), n.lower()))
        for fn in files:
            path = os.path.join(tex_dir, fn)
            try:
                print(f"[debug] scanning texture file: {path}")
            except Exception:
                pass
            try:
                raw = pygame.image.load(path)
                lname = fn.lower()
                try:
                    print(f"[debug] loaded image (scan): {path} -> fn={fn} size={raw.get_size()} flags={raw.get_flags()}")
                except Exception:
                    pass
                if fn.lower().endswith('.png'):
                    surf = raw.convert_alpha()
                else:
                    surf = raw.convert()

                try:
                    if 'eyes' in lname:
                        EYES_DARKEN = 0.35
                        v = max(0, min(255, int(255 * EYES_DARKEN)))
                        dark = pygame.Surface(surf.get_size(), pygame.SRCALPHA).convert_alpha()
                        dark.fill((v, v, v, 255))
                        try:
                            surf.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        except Exception:
                            surf.blit(dark, (0, 0))
                except Exception:
                    pass

                if any(k in lname for k in ('trust', 'text', 'graff', 'overlay')):
                    overlay_image = surf
                    continue

                # For floor/ceiling textures, ensure they are opaque surfaces
                if 'floor' in lname:
                    floor_src = path
                    try:
                        if surf.get_flags() & pygame.SRCALPHA:
                            tmp = pygame.Surface(surf.get_size())
                            tmp.blit(surf, (0, 0))
                            floor_tex = tmp.convert()
                        else:
                            floor_tex = surf.convert()
                    except Exception:
                        floor_tex = surf
                elif 'ceiling' in lname or 'ceil' in lname:
                    ceil_src = path
                    try:
                        if surf.get_flags() & pygame.SRCALPHA:
                            tmp2 = pygame.Surface(surf.get_size())
                            tmp2.blit(surf, (0, 0))
                            ceil_tex = tmp2.convert()
                        else:
                            ceil_tex = surf.convert()
                    except Exception:
                        ceil_tex = surf
                else:
                    wall_candidates.append((fn, surf))
            except Exception as e:
                print(f"Warning: failed loading texture {fn}: {e}")

    wall_candidates.sort(key=lambda t: (0 if 'eyes' in t[0].lower() else (1 if 'eye' in t[0].lower() else 2), t[0].lower()))
    textures = [t[1] for t in wall_candidates]
    if overlay_image is None and len(textures) > 1:
        overlay_candidate = textures[1]
    if textures:
        print(f"Loaded {len(textures)} wall texture(s) from {tex_dir}")

    # animated GIF handling: prefer .gif in the same dir
    try:
        gif_files = [fn for fn in os.listdir(tex_dir) if fn.lower().endswith('.gif')]
    except Exception:
        gif_files = []
    if gif_files:
        gif_path = os.path.join(tex_dir, gif_files[0])
        try:
            # resolve path (useful for bundled runtimes)
            gif_path = resource_path(gif_path)
            try:
                print(f"[debug] found GIF animation at: {gif_path}")
            except Exception:
                pass
            from PIL import Image
            im = Image.open(gif_path)
            frames = []
            durations = []
            MAX_DIM = 512
            for frame_index in range(0, getattr(im, 'n_frames', 1)):
                im.seek(frame_index)
                fr = im.convert('RGBA')
                w, h = fr.size
                if max(w, h) > MAX_DIM:
                    scale = MAX_DIM / float(max(w, h))
                    fr = fr.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
                d = fr.info.get('duration', im.info.get('duration', 100)) if hasattr(fr, 'info') else im.info.get('duration', 100)
                mode = fr.mode
                data = fr.tobytes()
                ps = pygame.image.fromstring(data, fr.size, mode)
                frames.append(ps.convert_alpha())
                durations.append(d)
            official_anim_frames = frames
            official_anim_durations = durations
        except Exception:
            try:
                img = pygame.image.load(gif_path)
                if gif_path.lower().endswith('.gif'):
                    official_anim_frames = [img.convert_alpha() if img.get_flags() & pygame.SRCALPHA else img.convert()]
                official_anim_durations = [100]
            except Exception as e:
                print(f"Warning: failed to load animated GIF {gif_path}: {e}")

    if floor_tex:
        try:
            # Final normalization: ensure floor texture is an opaque, display-format surface
            if floor_tex.get_flags() & pygame.SRCALPHA:
                tmpf = pygame.Surface(floor_tex.get_size())
                tmpf.blit(floor_tex, (0, 0))
                floor_tex = tmpf.convert()
            else:
                floor_tex = floor_tex.convert()
            print('Loaded floor texture')
            print(f"[debug] floor_tex flags={floor_tex.get_flags()} size={floor_tex.get_size()}")
        except Exception as e:
            print(f"[debug] floor_tex normalization failed: {e}")
    if ceil_tex:
        print('Loaded ceiling texture')
        try:
            print(f"[debug] floor source: {floor_src}")
            print(f"[debug] ceil source: {ceil_src}")
        except Exception:
            pass

    return {
        'textures': textures,
        'floor_tex': floor_tex,
        'ceil_tex': ceil_tex,
        'overlay_candidate': overlay_candidate,
        'overlay_image': overlay_image,
        'official_anim_frames': official_anim_frames,
        'official_anim_durations': official_anim_durations,
    }


def make_graffiti_overlays(textures, overlay_candidate, overlay_image, maze, start_ix, start_iy, overlay_brightness=1.0, scale=1):
    graffiti_overlays = {}
    GRAFFITI_TEXT = "Trust your eyes... but don't rely on them."
    adj_dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    placed = False
    map_w = len(maze[0]) if maze else 0
    map_h = len(maze)
    for dx, dy in adj_dirs:
        gx, gy = start_ix + dx, start_iy + dy
        if 0 <= gx < map_w and 0 <= gy < map_h and maze[gy][gx] == 1:
            chosen_overlay = overlay_image if overlay_image is not None else overlay_candidate
            if chosen_overlay is not None:
                try:
                    base_tw, base_th = (textures[0].get_size() if textures else (128, 128))
                    ow, oh = chosen_overlay.get_size()
                    if ow == 0 or oh == 0:
                        sc = 1.0
                    else:
                        sc = min(base_tw / ow, base_th / oh)
                    new_w = max(1, int(ow * sc))
                    new_h = max(1, int(oh * sc))
                    scaled = pygame.transform.smoothscale(chosen_overlay, (new_w, new_h))
                    over = pygame.Surface((base_tw, base_th), pygame.SRCALPHA)
                    if textures:
                        over.blit(textures[0], (0, 0))
                        ox = (base_tw - new_w) // 2
                        oy = (base_th - new_h) // 2
                        over.blit(scaled, (ox, oy))
                        try:
                            over = pygame.transform.flip(over, True, False)
                        except Exception:
                            pass
                    if overlay_brightness != 1.0:
                        try:
                            mul = pygame.Surface((base_tw, base_th), pygame.SRCALPHA)
                            v = max(0, min(255, int(255 * overlay_brightness)))
                            mul.fill((v, v, v, 255))
                            try:
                                over.blit(mul, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            except Exception:
                                over.blit(mul, (0, 0))
                        except Exception:
                            pass
                    graffiti_overlays[(gx, gy)] = over
                    placed = True
                    break
                except Exception:
                    pass

            if textures:
                base_tw, base_th = textures[0].get_size()
            else:
                base_tw, base_th = 128, 128
            over = pygame.Surface((base_tw, base_th), pygame.SRCALPHA)
            try:
                f = pygame.font.SysFont('Segoe Script', max(12, base_th // 8))
            except Exception:
                f = pygame.font.SysFont(None, max(12, base_th // 8))
            lines = [GRAFFITI_TEXT]
            yoff = base_th // 3
            for i, line in enumerate(lines):
                base_color = (220, 30, 30)
                try:
                    tc = (
                        min(255, int(base_color[0] * overlay_brightness)),
                        min(255, int(base_color[1] * 0.9)),
                        min(255, int(base_color[2] * 0.9)),
                    )
                except Exception:
                    tc = base_color
                txt = f.render(line, True, tc)
                tw, th = txt.get_size()
                if tw > base_tw - 10:
                    scale_s = (base_tw - 10) / tw
                    txt = pygame.transform.smoothscale(txt, (int(tw * scale_s), int(th * scale_s)))
                txt = pygame.transform.rotate(txt, random.uniform(-8, 8))
                over.blit(txt, (max(2, base_tw//8 - tw//8), yoff + i * (th + 2)))
            try:
                _apply_blood_overlay(over, droplets=2, alpha=30, seed=None)
            except Exception:
                pass
            graffiti_overlays[(gx, gy)] = over
            placed = True
            break

    return graffiti_overlays
