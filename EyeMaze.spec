# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

tmp_ret = collect_all('mediapipe')
datas = [('Main_Game_Scene\\textures', 'Main_Game_Scene\\textures'), ('Main_Game_Scene\\menu_art', 'Main_Game_Scene\\menu_art'), ('Music_And_SFX', 'Music_And_SFX')]
datas += tmp_ret[0]
binaries = []
binaries += tmp_ret[1]
hiddenimports = []
hiddenimports += tmp_ret[2]


a = Analysis(
    ['Main_Game_Scene\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rthook_mock_matplotlib.py'],
    excludes=['matplotlib', 'scipy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EyeMaze',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EyeMaze',
)
