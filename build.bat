@echo off
REM Build script for Eye Maze (Windows)
REM Usage: double-click this file or run in cmd from project root.
REM It assumes you have Python and PyInstaller installed in the environment you run this from.
:: Optional: activate virtualenv if present (uncomment if you use .venv)
IF EXIST ".venv\Scripts\activate.bat" (
	call ".venv\Scripts\activate.bat"
)

echo Cleaning previous build/dist folders...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo Building EyeMaze (onedir) with PyInstaller...
REM Prefer a dedicated build venv (.venv_build) if present, else fall back to project .venv, then system `python`.
set "PYRUN=python"
if exist ".venv_build\Scripts\python.exe" (
	echo Found .venv_build - trying that first...
	2>nul ".venv_build\Scripts\python.exe" -c "import importlib; importlib.import_module('PyInstaller')"
	if %errorlevel%==0 (
		set "PYRUN=.venv_build\Scripts\python.exe"
	) else (
		echo PyInstaller not found in .venv_build. Attempting to install into .venv_build now...
		2>nul ".venv_build\Scripts\python.exe" -m ensurepip --upgrade
		2>nul ".venv_build\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
		2>nul ".venv_build\Scripts\python.exe" -m pip install pyinstaller
		2>nul ".venv_build\Scripts\python.exe" -c "import importlib; importlib.import_module('PyInstaller')"
		if %errorlevel%==0 (
			set "PYRUN=.venv_build\Scripts\python.exe"
		) else (
			echo Failed to install PyInstaller into .venv_build; falling back to other options.
		)
	)
)
if "%PYRUN%"=="python" (
	if exist ".venv\Scripts\python.exe" (
		:: Try to use project venv python if PyInstaller is already available
		2>nul ".venv\Scripts\python.exe" -c "import importlib; importlib.import_module('PyInstaller')"
		if %errorlevel%==0 (
			set "PYRUN=.venv\Scripts\python.exe"
		) else (
			echo PyInstaller not found in .venv. Attempting to install into the venv now...
			2>nul ".venv\Scripts\python.exe" -m ensurepip --upgrade
			2>nul ".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
			2>nul ".venv\Scripts\python.exe" -m pip install pyinstaller
			2>nul ".venv\Scripts\python.exe" -c "import importlib; importlib.import_module('PyInstaller')"
			if %errorlevel%==0 (
				set "PYRUN=.venv\Scripts\python.exe"
			) else (
				echo Failed to install PyInstaller into .venv; will use system python instead.
			)
		)
	)
)
REM Adjust --add-data paths as needed. Windows uses semicolon to separate src;dest
%PYRUN% -m PyInstaller --noconfirm --clean --onedir --name "EyeMaze" --windowed ^
	--add-data "Main_Game_Scene\textures;Main_Game_Scene\textures" ^
	--add-data "Main_Game_Scene\menu_art;Main_Game_Scene\menu_art" ^
	--add-data "Music_And_SFX;Music_And_SFX" ^
	Main_Game_Scene\main.py

echo.
echo Build finished. See dist\EyeMaze\ for the output.
echo To run from command line (recommended for debugging):
echo    dist\EyeMaze\EyeMaze.exe
echo.
echo Press any key to exit.
pause >nul