import sys, importlib, traceback
sys.path.append(r'.')
ok = True
try:
    importlib.import_module('Main_Game_Scene.textures')
    importlib.import_module('Music_And_SFX.Music')
    print('Imported modules OK')
except Exception as e:
    ok = False
    traceback.print_exc()
    print('Import failed:', e)
raise SystemExit(0 if ok else 1)
