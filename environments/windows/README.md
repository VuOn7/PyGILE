# PyGILE Windows Installation Guide

This guide builds the `pygile` environment step by step on Windows 10 or 11. It takes 10 to 30 minutes, depending on your internet connection.

## 1. Download PyGILE

Go to the PyGILE page on GitHub, click the green **Code** button, then **Download ZIP**. Unzip it, for example into your `Documents` folder. You get a folder called `PyGILE-main`.

## 2. Install Miniforge

Download the Windows installer from [conda-forge.org/download](https://conda-forge.org/download/) and run it. The default choices are fine: install for **Just Me**, in the suggested folder.

Miniforge gives you **Miniforge Prompt**, a terminal that knows about `mamba` and `conda`. Use it for every step below.

## 3. Run the installer

Open **Miniforge Prompt** from the Start menu. Go to the Windows installer folder inside PyGILE. If you unzipped PyGILE into `Documents`:

```bat
cd %USERPROFILE%\Documents\PyGILE-main\environments\windows
```

Then run the installer:

```bat
install_pygile_windows.bat
```

It creates the `pygile` environment and installs the packages in five groups, printing what each group is for. Two log files appear in the same folder while it works: `pygile_installation.log` (everything) and `pygile_errors.log` (only problems). If an environment called `pygile` already exists, the installer asks before replacing it.

At the end you should see `SUCCESS: the pygile environment is ready`.

## 4. Start JupyterLab

In Miniforge Prompt:

```bat
mamba activate pygile
cd %USERPROFILE%\Documents\PyGILE-main
jupyter lab
```

The prompt now starts with `(pygile)`. JupyterLab opens in your browser. Open `PyGILE_course` and start with Lesson A1.

## Every time after that

Open Miniforge Prompt, then:

```bat
mamba activate pygile
cd %USERPROFILE%\Documents\PyGILE-main
jupyter lab
```

## Installed packages

The installer installs exactly the packages in [`environment.yml`](../../environment.yml), the file the automatic notebook tests use. To do the same in one command, run this from the PyGILE folder:

```bat
mamba env create -f environment.yml
```

## Older guide and video

[`environment_install_windows.pdf`](environment_install_windows.pdf) and [`pyGILE_Installation.mp4`](pyGILE_Installation.mp4) show an earlier version of the installer. Their screenshots of Miniforge are still useful, but some names have changed: the installer is now `install_pygile_windows.bat`, so there is no `.txt` file to rename, and the environment is called `pygile`, not `pygile_base`. You also no longer need to install `ipykernel` yourself.
