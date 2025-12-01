import sys
try:
    from unittest.mock import MagicMock
except ImportError:
    # Fallback if unittest.mock is not available (unlikely in stdlib)
    class MagicMock:
        def __getattr__(self, name):
            return MagicMock()
        def __call__(self, *args, **kwargs):
            return MagicMock()

# Mock matplotlib and common submodules
m = MagicMock()
sys.modules['matplotlib'] = m
sys.modules['matplotlib.pyplot'] = m
sys.modules['matplotlib.animation'] = m
sys.modules['matplotlib.image'] = m
sys.modules['matplotlib.widgets'] = m
sys.modules['matplotlib.collections'] = m
sys.modules['matplotlib.patch'] = m
sys.modules['matplotlib.lines'] = m
sys.modules['matplotlib.colors'] = m
