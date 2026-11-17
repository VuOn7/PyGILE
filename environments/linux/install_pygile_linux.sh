#!/bin/bash
# ============================================================
#   PYGILE ENVIRONMENT INSTALLER (Linux and macOS)
#   Builds the pygile environment step by step, one group of
#   packages at a time, so you can see what each group is for.
#
#   It installs exactly the packages in environment.yml, the
#   file the automatic notebook tests use. Prefer one command?
#   From the PyGILE folder run:
#       mamba env create -f environment.yml
#
#   If "pygile" already exists, it asks before replacing it. To answer
#   in advance (for automatic tests): PYGILE_REPLACE=yes (or no).
#
#   Maintainers: if you change a package here, change it in
#   environment.yml and the other installers too. The check in
#   PyGILE_course/tools/check_repo.py fails if they differ.
# ============================================================

LOGFILE="pygile_install.log"
ERRORLOG="pygile_errors.log"
ERROR_COUNT=0
STEP_COUNT=0

echo "Installation started at $(date)" > "$LOGFILE"
echo "Error summary" > "$ERRORLOG"

# ------------------------------------------------------------
# [1/7] Find mamba (faster) or conda from Miniforge
# ------------------------------------------------------------
echo "[1/7] Looking for Miniforge (mamba or conda)..."
if command -v mamba &> /dev/null; then
    INSTALLER="mamba"
elif command -v conda &> /dev/null; then
    INSTALLER="conda"
else
    echo "ERROR: neither mamba nor conda was found."
    echo "Install Miniforge first: https://github.com/conda-forge/miniforge"
    exit 1
fi
echo "      Using: $INSTALLER"

# Install one group of packages from conda-forge and report the result
install_group() {
    local step="$1" description="$2"; shift 2
    echo "[$step] Installing $description..."
    echo "      $*"
    if $INSTALLER install -n pygile --override-channels -c conda-forge "$@" -y >> "$LOGFILE" 2>&1; then
        echo "      Done: $description"
        STEP_COUNT=$((STEP_COUNT + 1))
    else
        echo "      WARNING: $description had problems (see $LOGFILE). Continuing."
        echo "FAILED: $description ($*)" >> "$ERRORLOG"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
}

# ------------------------------------------------------------
# [2/7] Fresh environment with Python 3.12
# ------------------------------------------------------------
# The JSON list looks the same in conda and in every version of mamba
if $INSTALLER env list --json 2>/dev/null | grep -qE 'envs[/\\]+pygile"'; then
    echo ""
    echo "An environment called 'pygile' already exists on this computer."
    echo "Continuing will DELETE it and build a new one."
    ANSWER="${PYGILE_REPLACE:-}"           # answer in advance, for automatic tests
    if [ -z "$ANSWER" ]; then
        read -r -p "Replace it? Type y and press Enter to continue, anything else to stop: " ANSWER
    else
        echo "Answer taken from PYGILE_REPLACE: $ANSWER"
    fi
    if [[ ! "$ANSWER" =~ ^[Yy] ]]; then
        echo "Stopped. Your existing pygile environment was not changed."
        echo "(To update it instead: $INSTALLER env update -n pygile -f ../../environment.yml --prune)"
        exit 0
    fi
    $INSTALLER env remove -n pygile -y >> "$LOGFILE" 2>&1
fi

echo "[2/7] Creating a fresh pygile environment with Python 3.12..."
if ! $INSTALLER create -n pygile --override-channels -c conda-forge "python=3.12" -y >> "$LOGFILE" 2>&1; then
    echo "CRITICAL: could not create the environment. See $LOGFILE."
    exit 1
fi
echo "      Done: environment created"

# ------------------------------------------------------------
# [3/7] to [7/7] Package groups (the same groups as environment.yml
# and the Windows installer)
# ------------------------------------------------------------
install_group "3/7" "core scientific Python (NumPy, pandas, SciPy, Matplotlib, scikit-learn)" \
    numpy pandas scipy matplotlib scikit-learn

install_group "4/7" "vector data (GeoPandas, Shapely, PyProj, pyogrio, mapclassify, OSMnx)" \
    "geopandas>=1.0" "shapely>=2.0" pyproj pyogrio mapclassify "osmnx>=2.0"

install_group "5/7" "rasters and remote sensing (Rasterio, rioxarray, Xarray, Dask, STAC tools)" \
    rasterio rioxarray xarray dask netcdf4 rasterstats xarray-spatial \
    pystac-client odc-stac planetary-computer

install_group "6/7" "maps and interpolation (Contextily, Folium, scale bars, PyKrige)" \
    contextily folium matplotlib-scalebar pykrige

install_group "7/7" "JupyterLab" \
    jupyterlab ipykernel ipywidgets

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------
echo ""
echo "Checking that the main libraries work..."
if $INSTALLER run -n pygile python -c "import numpy, pandas, geopandas, rasterio, rioxarray, xarray, matplotlib, osmnx, folium; print('ok')" 2>> "$LOGFILE" | grep -q ok; then
    echo "SUCCESS: the pygile environment is ready ($STEP_COUNT groups installed, $ERROR_COUNT problems)."
else
    echo "WARNING: a core library failed to import. See $LOGFILE and $ERRORLOG."
fi

echo ""
echo "============================================================"
echo "  HOW TO START WORKING"
echo "============================================================"
echo "  $INSTALLER activate pygile"
echo "  jupyter lab"
echo ""
echo "Logs: $LOGFILE   Errors: $ERRORLOG"
