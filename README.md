# PyGILE - Python GeoInformatics Lab Environment

<!-- When this version replaces Geoinformatics-Lab/PyGILE, change VuOn7 to Geoinformatics-Lab in the two links below. -->
[![Test notebooks](https://github.com/VuOn7/PyGILE/actions/workflows/test-notebooks.yml/badge.svg)](https://github.com/VuOn7/PyGILE/actions/workflows/test-notebooks.yml)

PyGILE makes it easy to learn and apply geospatial analysis with Python. It comes with pre-configured Jupyter notebooks and works on Windows, Mac, and Linux. Whether you're a student, teacher, or researcher, PyGILE provides everything you need to start working with geospatial data.

## Watch PyGILE in Action

**Want to learn Python for geospatial science but don't know where to begin?**

Start with this short introduction to setting up PyGILE and exploring its interactive Jupyter notebooks.

https://github.com/user-attachments/assets/f2a470af-96b3-43a3-b045-96d0c5ee30c6

Watch the full YouTube video for installation, setup and usage via the following link:

https://www.youtube.com/watch?v=aimkNzOxtaQ

## What is PyGILE?

PyGILE is an educational/application toolkit that includes:

-  Interactive Jupyter notebooks with GIS tutorials
-  Pre-installed geospatial Python libraries
-  Cross-platform support (Windows, Mac, Linux)
-  Learning materials for students and educators

## New: the PyGILE Course

A step-by-step course for absolute beginners, in [`PyGILE_course/`](PyGILE_course/README.md). Every step has theory, a worked example on Nepal data, and practice questions with worked solutions; the lessons are linked in order like a book. **Complete: Part A · Python (12 lessons), Part B · Vector GIS (12 lessons), Part C · Rasters (9 lessons) and Part D · Satellite imagery (6 lessons), with 1,061 practice questions.** PyGILE-Plus continues from there, with landslide susceptibility modelling and deep learning.

Every answer is **marked automatically** as you run it, offline and with no account, and an optional **free AI tutor** can add a personal hint. See [the tutor guide](PyGILE_course/AI_TUTOR.md).

## Getting Started

Choose one of three ways. Options 1 and 2 install the same libraries; option 3 uses a ready-made Docker image.

### Option 1: Step-by-step installer (recommended for learners)

Learn how a Python environment is built, one group of packages at a time, using **Miniforge Prompt** (Windows) or **Terminal** (macOS/Linux).

- **Windows:** follow the [Windows guide](environments/windows/README.md)
- **Linux:** follow the [Linux guide](environments/linux/README.md)
- **macOS:** follow the [macOS guide](environments/mac/README.md)

Each installer asks before replacing an existing `pygile` environment, and is tested every week on a fresh Miniforge.

### Option 2: One command

Already comfortable with Miniforge? Open **Miniforge Prompt** (Windows) or **Terminal** (macOS/Linux) in the PyGILE folder and run:

```bash
mamba env create -f environment.yml
mamba activate pygile
jupyter lab
```

The [`environment.yml`](environment.yml) file is what the automatic notebook tests use. Supported: Windows 10/11, Linux, and macOS 11 or newer (Intel and Apple Silicon). (Using git? `git clone --depth 1 https://github.com/Geoinformatics-Lab/PyGILE` downloads much less.)

### Option 3: Docker, using the PyGILE-Plus image

The [PyGILE-Plus](https://github.com/Geoinformatics-Lab/PyGILE-Plus) Docker image contains every library the PyGILE notebooks use, so you can run PyGILE in it without installing anything else. Install Docker Desktop, open a terminal **inside the PyGILE folder**, and run:

```bash
docker pull dockagile/pygile-plus
docker run -it --name pygile -p 127.0.0.1:8888:8888 -v "${PWD}:/workspace/PyGILE" dockagile/pygile-plus
```

(Windows Command Prompt: replace `${PWD}` with `%cd%`.) Then open http://localhost:8888 and go to the `PyGILE` folder. Your work is saved in your own PyGILE folder.

One small library is missing from the image: `matplotlib-scalebar`, which draws the scale bars in Lessons B11 and D3. Add it once, from a terminal in JupyterLab (**File → New → Terminal**):

```bash
pip install matplotlib-scalebar
```

Note: the image is large, because PyGILE-Plus also includes SAGA, GRASS, Orfeo ToolBox and deep-learning libraries. On a slow connection, Option 1 or 2 is quicker. The `127.0.0.1` part keeps Jupyter visible only on your own computer, which matters on shared Wi-Fi.

## How to Use PyGILE

Once you've completed the installation:

1. **Start Jupyter Lab** - This opens your web-based coding environment
2. **Open the course** - Go to [`PyGILE_course/`](PyGILE_course/README.md) and start with Lesson A1
3. **Start learning!** - Each lesson links to the next

Files the lessons create are saved in `PyGILE_course/outputs/`. Git ignores that folder, so your outputs never get mixed into the course files.

## Need Help?

-  **Found a bug?** Create an issue on GitHub
-  **Have an idea?** We welcome contributions!
-  **Want to contribute?** Fork the project, make your changes, and submit a pull request

## Contributing

Fork → Make changes → Pull request. All contributions welcome!

If you change a lesson, run these two checks before you open the pull request (the automatic tests run them too):

```bash
python PyGILE_course/tools/check_repo.py                   # outputs cleared, navigation, installers, question counts
python PyGILE_course/tools/qa.py PyGILE_course/A_Python/A01_Python_as_your_calculator.ipynb   # the lesson and all its solutions run
```

If you add or remove a package, change [`environment.yml`](environment.yml) and the three installers in [`environments/`](environments/) together.

## Credits

Enhanced from [mmann1123/pyGIS](https://github.com/mmann1123/pyGIS) by Geoinformatics Lab.

## Reference & Citation

Awasthi, B., Ninsawat, S., Raghavan, V., & Nemoto, T. (2025). PyGILE - Python GeoInformatics Lab Environment (1.0). Zenodo. https://doi.org/10.5281/zenodo.16144781

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16144781.svg)](https://doi.org/10.5281/zenodo.16144781)

The same reference is in [`CITATION.cff`](CITATION.cff), so GitHub's **Cite this repository** button gives it in APA and BibTeX.

## License

PyGILE is free software under the [GNU General Public License, version 3 or later](LICENSE).

- Copyright (C) 2021 Michael Mann and contributors ([pyGIS](https://github.com/mmann1123/pyGIS), from which PyGILE grew)
- Copyright (C) 2025–2026 Geoinformatics Lab and the PyGILE contributors

The datasets in `PyGILE_course/data/` keep their own licences and credits, listed in [`PyGILE_course/data/README.md`](PyGILE_course/data/README.md).
