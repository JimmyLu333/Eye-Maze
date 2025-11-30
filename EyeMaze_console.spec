# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Main_Game_Scene\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('Main_Game_Scene\\textures', 'Main_Game_Scene\\textures'), ('Main_Game_Scene\\menu_art', 'Main_Game_Scene\\menu_art'), ('Music_And_SFX', 'Music_And_SFX'), ('resources\\texture_manifest.json', 'resources'), ('Main_Game_Scene\\textures\\Andreion de Castro - Freelance Designer and Creative Coder in London, United Kingdom.gif', 'Main_Game_Scene\\textures'), ('Main_Game_Scene\\textures\\eyes_pattern 2.png', 'Main_Game_Scene\\textures'), ('Main_Game_Scene\\textures\\floor_pattern.png', 'Main_Game_Scene\\textures'), ('Main_Game_Scene\\textures\\Trust your sight. But beware its lies..png', 'Main_Game_Scene\\textures'), ('Music_And_SFX\\background_music.mp3', 'Music_And_SFX'), ('Music_And_SFX\\footsteps.wav', 'Music_And_SFX'), ('Music_And_SFX\\heart_beat.mp3', 'Music_And_SFX')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EyeMaze_console',
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
    name='EyeMaze_console',
)
