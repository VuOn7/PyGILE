# PyGILE macOS Installation Guide

## 1. Download PyGILE Repository

Go to https://github.com/Geoinformatics-Lab/PyGILE

Click green Code button and Download ZIP

Extract to home directory to get PyGILE-main folder

## 2. Download Miniforge3

Go to https://github.com/conda-forge/miniforge/releases/latest/

**For Intel Macs:** Download `Miniforge3-MacOSX-x86_64.sh`

**For Apple Silicon Macs (M1/M2/M3):** Download `Miniforge3-MacOSX-arm64.sh`

To check your Mac: Apple menu → About This Mac

## 3. Install Miniforge3

Open Terminal (Cmd+Space, type Terminal)

Navigate to Downloads:

```bash
cd ~/Downloads
```

**For Intel Macs:**
```bash
chmod +x Miniforge3-MacOSX-x86_64.sh
./Miniforge3-MacOSX-x86_64.sh
```

**For Apple Silicon Macs:**
```bash
chmod +x Miniforge3-MacOSX-arm64.sh
./Miniforge3-MacOSX-arm64.sh
```

During installation:
- Press Enter to continue
- Press Enter after reading license
- Type yes and press Enter
- Press Enter for default location
- **🚨⚠️🛑 CRITICAL: Type NO when asked about shell profile 🛑⚠️🚨**

## 4. Initialize Miniforge3 Manually

```bash
eval "$(/Users/$USER/miniforge3/bin/conda shell.bash hook)"
conda init
```

For zsh users (default on newer macOS):
```bash
conda init zsh
exec zsh -l
```

For bash users:
```bash
conda init bash
```

Test installation:
```bash
mamba --version
```

## 5. Create PyGILE Environment

Navigate to setup folder:

```bash
cd PyGILE-main/environments/mac
```

Run the installation script:
```bash
chmod +x install_pygile_macos.sh
./install_pygile_macos.sh
```

## 6. Activate Environment

```bash
mamba activate pygile
```

## 7. Test Installation

```bash
python -c 'import geopandas, rasterio, xarray, matplotlib, numpy, pandas, folium; print("All packages working!")'
```

Should show: All packages working!

## Daily Usage

```bash
mamba activate pygile
jupyter lab
```

Navigate to the PyGILE folder, open PyGILE_course and start with Lesson A1

## Installed Packages

The installer installs exactly the packages in [`environment.yml`](../../environment.yml), the file the automatic notebook tests use, in five groups: core scientific Python, vector data, rasters and remote sensing, maps and interpolation, and JupyterLab. If an environment called `pygile` already exists, the installer asks before replacing it.

To do the same in one command, run this from the PyGILE folder:

```bash
mamba env create -f environment.yml
```
