import os
import sys

def resource_path(rel_path):
    """
    Return an absolute path to a resource, working for dev and for PyInstaller bundles.
    If the resource exists in the PyInstaller _MEIPASS bundle, return that path.
    Otherwise try relative to this file, then absolute.
    If none exist, return the original rel_path (caller should handle exceptions).
    """
    if not rel_path:
        return rel_path
    # If already absolute and exists, return it
    try:
        if os.path.isabs(rel_path) and os.path.exists(rel_path):
            return rel_path
    except Exception:
        pass

    candidates = []
    # If running from a PyInstaller bundle, resources are extracted to _MEIPASS
    base = getattr(sys, '_MEIPASS', None)
    if base:
        candidates.append(os.path.join(base, rel_path))

    # Relative to this repository file
    this_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(this_dir, rel_path))

    # Relative to current working directory
    candidates.append(os.path.abspath(rel_path))

    for p in candidates:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            continue

    # Fallback: return the original path (may be handled by caller)
    return rel_path
