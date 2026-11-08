@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

REM ============================================================
REM   PYGILE ENVIRONMENT INSTALLER (Windows)
REM   Builds the pygile environment step by step, one group of
REM   packages at a time, so you can see what each group is for.
REM
REM   Run it from Miniforge Prompt, inside this folder:
REM       install_pygile_windows.bat
REM
REM   It installs exactly the packages in environment.yml, the
REM   file the automatic notebook tests use. Prefer one command?
REM   From the PyGILE folder run:
REM       mamba env create -f environment.yml
REM
REM   If "pygile" already exists, it asks before replacing it. To answer
REM   in advance (for automatic tests): set PYGILE_REPLACE=yes (or no).
REM
REM   Maintainers: if you change a package here, change it in
REM   environment.yml and the other installers too. The check in
REM   PyGILE_course\tools\check_repo.py fails if they differ.
REM ============================================================

set "LOGFILE=pygile_installation.log"
set "ERRORLOG=pygile_errors.log"
set ERROR_COUNT=0
set STEP_COUNT=0

echo.
echo ====================================================
echo       PYGILE ENVIRONMENT INSTALLER
echo ====================================================
echo Log file:   %LOGFILE%
echo Error log:  %ERRORLOG%
echo.
echo Installation started at %date% %time% > "%LOGFILE%"
echo Error summary > "%ERRORLOG%"

REM ------------------------------------------------------------
REM [1/7] Find mamba (faster) or conda from Miniforge
REM ------------------------------------------------------------
echo [1/7] Looking for Miniforge (mamba or conda)...
set "INSTALLER="
where mamba >nul 2>&1 && set "INSTALLER=mamba"
if not defined INSTALLER where conda >nul 2>&1 && set "INSTALLER=conda"

REM Not run from Miniforge Prompt? Try the usual install folders.
if not defined INSTALLER (
    for %%D in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3" "C:\miniforge3") do (
        if not defined INSTALLER (
            if exist "%%~D\Scripts\mamba.exe" (
                set "INSTALLER=%%~D\Scripts\mamba.exe"
            ) else if exist "%%~D\condabin\conda.bat" (
                set "INSTALLER=%%~D\condabin\conda.bat"
            )
        )
    )
)

if not defined INSTALLER (
    echo ============================================================
    echo ERROR: Miniforge was not found.
    echo Install Miniforge first: https://conda-forge.org/download/
    echo Then open "Miniforge Prompt" from the Start menu and run
    echo this installer again from that window.
    echo ============================================================
    pause
    exit /b 1
)
echo       Using: !INSTALLER!
echo Using: !INSTALLER! >> "%LOGFILE%"

REM ------------------------------------------------------------
REM [2/7] Fresh environment with Python 3.12
REM ------------------------------------------------------------
REM The JSON list looks the same in conda and in every version of mamba.
REM It goes through a file, not a pipe: !variables! are not expanded in pipes.
set "ENVLIST=%TEMP%\pygile_env_list.json"
call "!INSTALLER!" env list --json > "!ENVLIST!" 2>nul
findstr /R /C:"envs.*pygile[^a-zA-Z0-9_.-]" "!ENVLIST!" >nul
set FOUND=!errorlevel!
del "!ENVLIST!" >nul 2>&1
if !FOUND! equ 0 (
    echo.
    echo An environment called "pygile" already exists on this computer.
    echo Continuing will DELETE it and build a new one.
    if defined PYGILE_REPLACE (
        echo Answer taken from PYGILE_REPLACE: !PYGILE_REPLACE!
        if /I not "!PYGILE_REPLACE!"=="yes" goto :keep_existing
    ) else (
        choice /C YN /M "Replace it"
        if errorlevel 2 goto :keep_existing
    )
    call "!INSTALLER!" env remove -n pygile -y >> "%LOGFILE%" 2>&1
)

echo [2/7] Creating a fresh pygile environment with Python 3.12...
call "!INSTALLER!" create -n pygile --override-channels -c conda-forge "python=3.12" -y >> "%LOGFILE%" 2>&1
if !errorlevel! neq 0 (
    echo CRITICAL: could not create the environment. See %LOGFILE%.
    echo CRITICAL: environment creation failed >> "%ERRORLOG%"
    pause
    exit /b 1
)
echo       Done: environment created

REM ------------------------------------------------------------
REM [3/7] to [7/7] Package groups (the same groups as environment.yml
REM and the Linux and macOS installer). Keep each group on ONE line.
REM ------------------------------------------------------------
call :install_group "3/7" "core scientific Python (NumPy, pandas, SciPy, Matplotlib, scikit-learn)" numpy pandas scipy matplotlib scikit-learn
call :install_group "4/7" "vector data (GeoPandas, Shapely, PyProj, pyogrio, mapclassify, OSMnx)" "geopandas>=1.0" "shapely>=2.0" pyproj pyogrio mapclassify "osmnx>=2.0"
call :install_group "5/7" "rasters and remote sensing (Rasterio, rioxarray, Xarray, Dask, STAC tools)" rasterio rioxarray xarray dask netcdf4 rasterstats xarray-spatial pystac-client odc-stac planetary-computer
call :install_group "6/7" "maps and interpolation (Contextily, Folium, scale bars, PyKrige)" contextily folium matplotlib-scalebar pykrige
call :install_group "7/7" "JupyterLab" jupyterlab ipykernel ipywidgets

REM ------------------------------------------------------------
REM Verification
REM ------------------------------------------------------------
echo.
echo Checking that the main libraries work...
call "!INSTALLER!" run -n pygile python -c "import numpy, pandas, geopandas, rasterio, rioxarray, xarray, matplotlib, osmnx, folium; print('ok')" >> "%LOGFILE%" 2>&1
if !errorlevel! neq 0 (
    echo WARNING: a core library failed to import. See %LOGFILE% and %ERRORLOG%.
    echo VERIFY FAILED: core libraries >> "%ERRORLOG%"
    set /a ERROR_COUNT+=1
) else (
    echo SUCCESS: the pygile environment is ready ^(!STEP_COUNT! groups installed, !ERROR_COUNT! problems^).
)

echo.
echo ============================================================
echo   HOW TO START WORKING
echo ============================================================
echo   mamba activate pygile
echo   cd to your PyGILE folder
echo   jupyter lab
echo.
echo Logs: %LOGFILE%   Errors: %ERRORLOG%
pause
exit /b 0

:keep_existing
echo Stopped. Your existing pygile environment was not changed.
echo To update it instead: mamba env update -n pygile -f ..\..\environment.yml --prune
pause
exit /b 0

REM ------------------------------------------------------------
REM Install one group of packages from conda-forge and report the result.
REM %1 step, %2 description, then one argument per package. A package with
REM a version, such as "geopandas>=1.0", must be in quotes, or Windows reads
REM ">" as "write to a file". The quotes are kept all the way to mamba.
REM ------------------------------------------------------------
:install_group
set "STEP=%~1"
set "DESC=%~2"
set PKGS=
:collect_packages
if "%~3"=="" goto :run_group
set PKGS=!PKGS! %3
shift /3
goto :collect_packages
:run_group
echo [!STEP!] Installing !DESC!...
echo      !PKGS!
call "!INSTALLER!" install -n pygile --override-channels -c conda-forge !PKGS! -y >> "%LOGFILE%" 2>&1
if !errorlevel! neq 0 (
    echo       WARNING: !DESC! had problems ^(see %LOGFILE%^). Continuing.
    echo FAILED: !DESC! ^(!PKGS!^) >> "%ERRORLOG%"
    set /a ERROR_COUNT+=1
) else (
    echo       Done: !DESC!
    set /a STEP_COUNT+=1
)
exit /b 0
