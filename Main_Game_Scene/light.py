import pygame
import math


class LightSystem:
    """Simple light/darkness overlay system.

    Usage:
        ls = LightSystem(darkness=0.25, vignette=True, vignette_strength=0.6)
        ls.apply(screen)

    - darkness: fraction 0.0..1.0 of how dark the screen becomes (0 = unchanged, 1 = fully black)
    - vignette: enable a radial bright-spot in the center to simulate a torch/eye-limited view
    - vignette_strength: 0.0..1.0 how strong the vignette effect is (0 = no vignette)
    """

    def __init__(self, darkness=0.25, vignette=False, vignette_strength=0.5, color=(0, 0, 0)):
        self.darkness = max(0.0, min(1.0, float(darkness)))
        self.vignette = bool(vignette)
        self.vignette_strength = max(0.0, min(1.0, float(vignette_strength)))
        self.color = color
        self._cached_size = None
        self._vignette_surf = None

    def _create_vignette(self, size):
        """Create a radial vignette surface for the given size.
        The vignette surface has black pixels with alpha values higher toward the edges.
        """
        w, h = size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        max_r = math.hypot(cx, cy)
        # We'll draw a series of concentric circles to approximate a smooth radial alpha.
        steps = max(16, int(max_r // 4))
        # Edge alpha target (scaled by vignette_strength)
        edge_alpha = int(255 * self.vignette_strength)
        for i in range(steps, 0, -1):
            frac = i / float(steps)
            r = int(frac * max_r)
            # Alpha grows toward the edge: near center alpha close to 0, near edge close to edge_alpha
            a = int(edge_alpha * (1.0 - frac))
            if a <= 0:
                continue
            col = (*self.color, a)
            try:
                pygame.draw.circle(surf, col, (cx, cy), r)
            except Exception:
                # fallback: fill entire surface with lower alpha
                surf.fill(col)
                break
        return surf

    def apply(self, target_surf):
        """Apply the darkness overlay to target_surf in-place."""
        try:
            w, h = target_surf.get_size()
        except Exception:
            return

        # base overlay
        if self.darkness <= 0.0 and not self.vignette:
            return

        base_alpha = int(255 * max(0.0, min(1.0, self.darkness)))
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((*self.color, base_alpha))

        # vignette: subtract a radial alpha to keep center brighter
        if self.vignette and self.vignette_strength > 0.0:
            if self._cached_size != (w, h) or self._vignette_surf is None:
                try:
                    self._vignette_surf = self._create_vignette((w, h))
                    self._cached_size = (w, h)
                except Exception:
                    self._vignette_surf = None
            if self._vignette_surf:
                # Blend the vignette by subtracting its alpha from the overlay
                try:
                    overlay.blit(self._vignette_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                except Exception:
                    # fallback: simply blit without special flags
                    overlay.blit(self._vignette_surf, (0, 0))

        # apply overlay on top
        try:
            target_surf.blit(overlay, (0, 0))
        except Exception:
            pass
