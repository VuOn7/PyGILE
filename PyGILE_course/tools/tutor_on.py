"""Turns on the PyGILE tutor for this notebook. Use it from a lesson with:

    %run ../tools/tutor_on.py
"""
import sys
from pathlib import Path

_tools = str(Path(__file__).resolve().parent)
if _tools not in sys.path:
    sys.path.insert(0, _tools)

from IPython import get_ipython  # noqa: E402

get_ipython().extension_manager.load_extension("pygile_tutor")
print("✅ Answer checking is on. Run an answer cell to see your mark. "
      "Type %tutor for options.")
