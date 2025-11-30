@echo off
REM Build script for Eye Maze (Windows)
REM Usage: double-click this file or run in cmd from project root.
REM It assumes you have Python and PyInstaller installed in the environment you run this from.











necho.
necho Build finished. See dist\EyeMaze\ for the output.
necho To run from command line (recommended for debugging):
necho    dist\EyeMaze\EyeMaze.exe
necho.
necho Press any key to exit.
npause >nul  Main_Game_Scene\main.py  --add-data "Music_And_SFX;Music_And_SFX" ^  --add-data "Main_Game_Scene\menu_art;Main_Game_Scene\menu_art" ^  --add-data "Main_Game_Scene\textures;Main_Game_Scene\textures" ^
em pyinstaller command (onedir) - adjust --add-data paths as needed
npyinstaller --noconfirm --clean --onedir --name "EyeMaze" --windowed ^
emove previous build/dist folders for a clean build
nif exist build rmdir /s /q build
nif exist dist rmdir /s /q dist
nif exist __pycache__ rmdir /s /q __pycache__
necho Building EyeMaze (onedir) with PyInstaller...:: --- Optional: activate virtualenv if present ---
:: Uncomment / edit the next line if you use a venv named .venv
:: call .\.venv\Scripts\activate.bat