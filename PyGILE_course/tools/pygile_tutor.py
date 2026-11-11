"""PyGILE tutor: marks practice answers inside the lesson notebooks.

Turn it on with one cell at the top of a lesson:

    %run ../tools/tutor_on.py

Then, every time a learner runs an answer cell (one that starts with
"# Q1: your answer", "# Q2", "# Q3" or "# Your answer"), a small card appears
under it:

    ✅ Correct        the result matches the course's own solution
    🟡 Nearly there   part of the result matches
    🔴 Not yet        an error, or nothing matches yet
    ▶️ It ran         the answer cannot be checked automatically (a plot, a map)

Marking needs no internet and no account. It compares the learner's printed
output, displayed value and variables with answer_key.json, which
build_answer_key.py makes by running every hidden solution.

An AI tutor can add a few warm, personal sentences of feedback. It is optional
and off until the learner types  %tutor setup  in a cell, which walks them step
by step through making a free key (Google Gemini or Groq, or OpenRouter) or a
very cheap paid one (DeepSeek). Several services can be saved: when one reaches
its free daily limit, the tutor moves to the next one. Keys are stored in
~/.pygile/tutor.json on the learner's computer, never in the notebook.
The beginner's guide is PyGILE_course/AI_TUTOR.md.

Commands:  %tutor (status) · %tutor setup · %tutor help · %tutor remove NAME
·  %tutor ai off / on · %tutor off / on · %tutor progress · %tutor reset
Advanced: change a service's "model" (or add a "url" for any OpenAI-style
server, such as Ollama) by editing ~/.pygile/tutor.json.
"""
import ast
import html
import json
import math
import os
import random
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
COURSE = TOOLS.parent
KEY_FILE = TOOLS / "answer_key.json"
HOME = Path.home() / ".pygile"
CONFIG_FILE = HOME / "tutor.json"
PROGRESS_FILE = HOME / "progress.json"

ANSWER_STARTS = ("# Q1", "# Q2", "# Q3", "# Your answer")

# The beginner's guide. When the repository moves to Geoinformatics-Lab,
# change VuOn7 to Geoinformatics-Lab here (as in the main README).
GUIDE_URL = "https://github.com/VuOn7/PyGILE/blob/main/PyGILE_course/AI_TUTOR.md"

# AI services that all speak the same (OpenAI-style) language. Facts checked
# November 2026; services change their limits, so the guide says how to check.
PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "cost": "Free. About 500 feedback messages a day. No credit card.",
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-3.5-flash-lite",
        "anchor": "1-google-gemini-free",
        "reset": "Gemini's free limit starts again every day at midnight in California: "
                 "about 1:45 pm in Nepal (12:45 pm from mid-March to early November).",
        "steps": [
            'Open <a href="https://aistudio.google.com/apikey" target="_blank">'
            "aistudio.google.com/apikey</a> (it opens in a new tab).",
            "Sign in with your Google account (the one you use for Gmail or YouTube).",
            "If it asks you to accept the terms, read them and accept.",
            "Click the button <b>Create API key</b>.",
            "A long code appears. That is your key. Click <b>Copy</b> next to it.",
        ],
    },
    "groq": {
        "name": "Groq",
        "cost": "Free. About 1,000 feedback messages a day. No credit card.",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "openai/gpt-oss-120b",
        "anchor": "2-groq-free-a-good-backup",
        "reset": "Groq's free daily limit starts again the next day.",
        "steps": [
            'Open <a href="https://console.groq.com/keys" target="_blank">'
            "console.groq.com/keys</a> (it opens in a new tab).",
            "Sign in with Google, GitHub or your email address.",
            "Click <b>Create API Key</b>. Type the name <code>PyGILE</code> and click <b>Submit</b>.",
            "Click <b>Copy</b>. Copy it now: Groq shows the key only once.",
        ],
    },
    "openrouter": {
        "name": "OpenRouter",
        "cost": "Free models. About 50 feedback messages a day. No credit card.",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "openrouter/free",
        "anchor": "3-openrouter-free-a-small-extra-backup",
        "reset": "OpenRouter's free daily limit starts again the next day.",
        "steps": [
            'Open <a href="https://openrouter.ai/keys" target="_blank">'
            "openrouter.ai/keys</a> (it opens in a new tab).",
            "Sign in or sign up (Google, GitHub or email).",
            "Click <b>Create API Key</b>, type the name <code>PyGILE</code> and click <b>Create</b>.",
            "Click <b>Copy</b>. Copy it now: it is shown only once.",
        ],
    },
    "deepseek": {
        "name": "DeepSeek",
        "cost": "Paid, very cheap: about US$1 for 1,500 feedback messages. "
                "You add money first.",
        "url": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-flash",
        "anchor": "4-deepseek-paid-very-cheap",
        "reset": "DeepSeek has no daily limit: it stops when the money you added runs out.",
        "steps": [
            'Open <a href="https://platform.deepseek.com" target="_blank">'
            "platform.deepseek.com</a> and sign up (it opens in a new tab).",
            "Click <b>Top up</b> and add a small amount. US$2 is enough for months of practice.",
            "Click <b>API keys</b> in the menu, then <b>Create new API key</b>. Name it "
            "<code>PyGILE</code>.",
            "Click <b>Copy</b>. Copy it now: it is shown only once.",
        ],
    },
}

PRAISE = [
    "Well done!", "Great work!", "Exactly right!", "Nicely done!",
    "You've got it!", "Spot on!", "Excellent!", "That's it!",
]
NEARLY = [
    "You're close.", "Good start.", "Almost there.", "Part of this is right.",
]
NOT_YET = [
    "Not yet, and that's fine.", "Keep going.", "A good attempt to learn from.",
]

ERROR_HINTS = {
    "NameError": "Python does not know one of the names you used. Check the spelling "
                 "and capital letters, and make sure you ran the example cells above this one.",
    "SyntaxError": "Python could not read the line. Look for a missing bracket, quote "
                   "mark, comma or colon near the place the arrow points to.",
    "IndentationError": "The spaces at the start of a line are not what Python expects. "
                        "Lines inside a loop, `if` or function need four spaces.",
    "TypeError": "Two values of the wrong type met, for example text and a number. "
                 "`type()` shows what each value is.",
    "IndexError": "You asked for a position that does not exist. Remember counting starts at 0.",
    "KeyError": "That key or column name is not there. Check its exact spelling and capitals.",
    "AttributeError": "This kind of value does not have that method or attribute. "
                      "Check the spelling, and the type of the value.",
    "ValueError": "The type is right but the value is not, for example `int('8,849')`.",
    "ZeroDivisionError": "Somewhere a number is divided by zero.",
    "FileNotFoundError": "Python cannot find the file. Check the folder and file name; "
                         "the course data is in `../data`.",
    "ModuleNotFoundError": "This library is not installed in your environment, or its "
                           "name is misspelled.",
}

SYSTEM_PROMPT = """You are the PyGILE tutor, a kind and patient teacher inside a Jupyter \
notebook. The learner is an absolute beginner in Python and GIS, often a student in Nepal. \
English may be their second language.

You get the question, the course's own solution, the learner's code and what it printed, \
and an automatic check of the result. Reply in at most 4 short sentences:
1. First line: exactly one word, CORRECT, NEARLY or NOT_YET (your judgement of the answer).
2. Then say one specific thing the learner did well.
3. If the answer is not fully correct, give ONE hint that moves them forward. Do not paste \
the full solution. Point to the line or idea to change.
4. If it is correct, add one short tip or a "try this next" idea, if a useful one exists.

A different but valid way to solve it is CORRECT: there are many right answers. \
Sentences that are worded differently from the solution are fine if the numbers are right. \
Use plain English and short sentences. Never use the words simply, just, obviously or easy. \
Be warm, never childish, never sarcastic. Do not use Markdown headings."""


# ---------------------------------------------------------------------------
# Fingerprints: a small, comparable summary of any value.
# The answer-key builder uses the same function, so both sides match.
# ---------------------------------------------------------------------------
def fingerprint(obj, depth=0):
    if depth > 3:
        return {"type": type(obj).__name__}
    if obj is None or isinstance(obj, (bool, str)):
        return obj if not isinstance(obj, str) or len(obj) < 2000 else obj[:2000]
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        return None if math.isnan(obj) else round(obj, 4)
    if isinstance(obj, (list, tuple)):
        if len(obj) > 200:
            return {"type": type(obj).__name__, "len": len(obj)}
        return {"type": type(obj).__name__, "items": [fingerprint(x, depth + 1) for x in obj]}
    if isinstance(obj, (set, frozenset)):
        items = sorted((repr(fingerprint(x, depth + 1)) for x in obj))
        return {"type": "set", "items": items[:200], "len": len(obj)}
    if isinstance(obj, dict):
        if len(obj) > 200:
            return {"type": "dict", "len": len(obj)}
        return {"type": "dict",
                "items": {str(k): fingerprint(v, depth + 1) for k, v in obj.items()}}
    mod = type(obj).__module__.split(".")[0]
    name = type(obj).__name__
    try:
        if mod == "numpy" and hasattr(obj, "shape"):
            import numpy as np
            fp = {"type": "ndarray", "shape": list(obj.shape), "dtype": obj.dtype.kind}
            if obj.dtype.kind in "biuf" and obj.size:
                fp["sum"] = round(float(np.nansum(obj.astype(float))), 3)
                fp["nan"] = int(np.isnan(obj.astype(float)).sum())
            return fp
        if mod == "numpy":                                    # numpy scalar
            return fingerprint(obj.item(), depth)
        if name in ("DataFrame", "GeoDataFrame"):
            fp = {"type": name, "shape": list(obj.shape),
                  "columns": [str(c) for c in obj.columns]}
            num = obj.select_dtypes("number")
            if num.size:
                fp["sum"] = round(float(num.sum().sum()), 3)
            return fp
        if name in ("Series", "GeoSeries"):
            fp = {"type": name, "len": len(obj), "name": str(obj.name)}
            if obj.dtype.kind in "biuf" and len(obj):
                fp["sum"] = round(float(obj.sum()), 3)
            return fp
        if name == "DataArray":
            return {"type": name, "shape": list(obj.shape), "dims": list(obj.dims)}
    except Exception:
        pass
    return {"type": name}


def comparable(fp):
    """False for values whose fingerprint says nothing useful (only a type name)."""
    return not (isinstance(fp, dict) and set(fp) == {"type"})


def names_in(code):
    """Names a solution assigns to or changes (trek.append(...) changes trek)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    found = []

    def add(n):
        if n not in found:
            found.append(n)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            add(node.id)
        elif isinstance(node, (ast.Subscript, ast.Attribute)) and isinstance(node.ctx, ast.Store):
            base = node.value
            while isinstance(base, (ast.Subscript, ast.Attribute)):
                base = base.value
            if isinstance(base, ast.Name):
                add(base.id)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and isinstance(node.func.value, ast.Name)
              and node.func.attr in {"append", "extend", "insert", "remove", "pop", "sort",
                                     "reverse", "update", "clear", "add", "discard",
                                     "setdefault"}):
            add(node.func.value.id)
    # loop variables are working names, not results
    loops = {t.id for n in ast.walk(tree) if isinstance(n, (ast.For, ast.comprehension))
             for t in ast.walk(n.target) if isinstance(t, ast.Name)}
    return [n for n in found if n not in loops and not n.startswith("_")]


def mostly_same(a, b):
    """True if two list fingerprints have the same length and at least half the items match."""
    if not (isinstance(a, dict) and isinstance(b, dict) and "items" in a and "items" in b):
        return False
    x, y = a["items"], b["items"]
    if not isinstance(x, list) or len(x) != len(y) or not x:
        return False
    return sum(p == q for p, q in zip(x, y)) * 2 >= len(x)


# ---------------------------------------------------------------------------
# Comparing outputs
# ---------------------------------------------------------------------------
NUM = re.compile(r"-?\d[\d,]*\.?\d*(?:[eE]-?\d+)?")


def norm_text(s):
    s = re.sub(r" at 0x[0-9a-fA-F]+>", ">", s.replace("\r\n", "\n")).strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"" and "\n" not in s:
        s = s[1:-1]                                  # 'abc' (a value) equals abc (printed)
    return re.sub(r"[ \t]+", " ", re.sub(r"\s*\n\s*", "\n", s))


def numbers(s):
    out = []
    for m in NUM.findall(s):
        try:
            out.append(round(float(m.replace(",", "")), 2))
        except ValueError:
            pass
    return out


def mark(expected, got):  # noqa: C901
    """Return (verdict, reason). verdict: correct, nearly, not_yet, ran."""
    exp_out = "" if expected.get("unstable") else norm_text(expected.get("output", ""))
    got_out = norm_text(got["output"])
    all_vars = {k: v for k, v in expected.get("vars", {}).items() if comparable(v)}
    required = expected.get("required", [])
    exp_vars = {k: v for k, v in all_vars.items() if k in required}
    if not exp_vars and not exp_out and not expected.get("unstable"):
        # Nothing named in the question and nothing shown: compare whatever the
        # learner created with the same names as the solution.
        exp_vars = {k: v for k, v in all_vars.items() if k in got["vars"]}

    var_ok = var_bad = var_close = 0
    missing = []
    for name, fp in exp_vars.items():
        if name not in got["vars"]:
            missing.append(name)
        elif got["vars"][name] == fp:
            var_ok += 1
        else:
            var_bad += 1
            var_close += mostly_same(got["vars"][name], fp)

    out_exact = bool(exp_out) and exp_out == got_out
    exp_nums, got_nums = numbers(exp_out), numbers(got_out)
    # Every expected number must appear, and not many more: a sentence may be worded
    # differently, but showing 10 rows when 3 were asked for is not the same answer.
    left = list(got_nums)
    found_all = bool(exp_nums)
    for n in exp_nums:
        if n in left:
            left.remove(n)
        else:
            found_all = False
            break
    nums_ok = found_all and len(left) <= max(2, len(exp_nums) // 5)
    nums_some = bool(exp_nums) and any(n in got_nums for n in exp_nums)

    checks = bool(exp_out) or bool(exp_vars)
    if not checks:
        return "ran", "This answer is a picture or a map, so compare it with the solution."
    vars_all_ok = var_ok == len(exp_vars)

    if vars_all_ok and (not exp_out or out_exact):
        return "correct", "Your result matches the course solution exactly."
    if vars_all_ok and nums_ok:
        return "correct", "Your numbers match the solution. Your wording can differ, that's fine."
    if vars_all_ok and exp_out and not got_out:
        return "nearly", "Your values are right. The question also asks you to show the result."
    if var_ok or var_close or out_exact or nums_some or (nums_ok and not vars_all_ok):
        bits = []
        if out_exact or nums_ok:
            bits.append("Your printed result is right.")
        if var_close:
            bits.append("Most of the values match: check each one against the question.")
        if missing:
            bits.append(f"I could not find {', '.join(f'`{m}`' for m in missing)} yet.")
        if var_bad > var_close:
            bits.append("A value you stored is different from the solution's.")
        if exp_out and not nums_ok:
            bits.append("Some of the printed result differs.")
        return "nearly", " ".join(bits) or "Part of your result matches."
    if missing and not got_out:
        return "not_yet", (f"I was looking for {', '.join(f'`{m}`' for m in missing)}. "
                           "Check the name the question asks for.")
    return "not_yet", "Your result is different from the solution's."


# ---------------------------------------------------------------------------
# Reading the lesson (question and solution text) by cell id
# ---------------------------------------------------------------------------
_KEY = None
_NB_CACHE = {}


def answer_key():
    global _KEY
    if _KEY is None:
        try:
            _KEY = json.loads(KEY_FILE.read_text(encoding="utf-8"))
        except FileNotFoundError:
            _KEY = {"answers": {}, "lessons": {}}
    return _KEY


def lesson_text(lesson, cell_id):
    path = COURSE / lesson
    if path not in _NB_CACHE:
        try:
            _NB_CACHE[path] = json.loads(path.read_text(encoding="utf-8"))["cells"]
        except Exception:
            _NB_CACHE[path] = []
    cells = _NB_CACHE[path]
    for i, c in enumerate(cells):
        if c.get("id") == cell_id:
            q = "".join(cells[i - 1]["source"]) if i else ""
            s = "".join(cells[i + 1]["source"]) if i + 1 < len(cells) else ""
            return q, s
    return "", ""


# ---------------------------------------------------------------------------
# Settings and progress, kept in ~/.pygile (never in the notebook)
# ---------------------------------------------------------------------------
def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, data):
    HOME.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=1), encoding="utf-8")
    if path == CONFIG_FILE:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# The AI tutor (optional)
# ---------------------------------------------------------------------------
def services(cfg):
    """The learner's saved AI services, in the order they are tried."""
    if "provider" in cfg and "services" not in cfg:          # settings from the first version
        cfg["services"] = [{k: cfg[k] for k in ("provider", "key", "model", "url") if k in cfg}]
    return [s for s in cfg.get("services", []) if s.get("provider") in PROVIDERS or s.get("url")]


def service_name(svc):
    return PROVIDERS.get(svc.get("provider"), {}).get("name", svc.get("provider", "AI service"))


def call_service(svc, system, user):
    """One request to one service. Returns (text, problem): problem is None,
    'limit', 'key', 'network' or 'other'."""
    prov = PROVIDERS.get(svc.get("provider"), {})
    url = svc.get("url") or prov.get("url")
    model = svc.get("model") or prov.get("model")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.4,
        "max_tokens": 1200,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if svc.get("key"):
        headers["Authorization"] = f"Bearer {svc['key']}"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode())
        text = (data["choices"][0]["message"].get("content") or "").strip()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return None, "limit"
        if e.code == 402:                                      # no money left (paid services)
            return None, "limit"
        if e.code in (400, 401, 403):
            detail = e.read().decode(errors="replace").lower()
            if e.code != 400 or "key" in detail:
                return None, "key"
        return None, "other"
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, "network"
    except Exception:
        return None, "other"
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    return (text, None) if text else (None, "other")


def ask_ai(cfg, question, solution, code, output, error, verdict, reason):
    """Try each saved service in turn. Returns (text, help_html)."""
    svcs = services(cfg)
    if not svcs:
        return None, None
    user = (
        f"QUESTION:\n{question.strip()[:3000]}\n\n"
        f"COURSE SOLUTION (hidden from the learner):\n{solution.strip()[:3000]}\n\n"
        f"LEARNER'S CODE:\n{code.strip()[:3000]}\n\n"
        f"WHAT IT SHOWED:\n{(output or '(nothing)')[:2000]}\n\n"
        + (f"ERROR:\n{error[:1500]}\n\n" if error else "")
        + f"AUTOMATIC CHECK: {verdict} ({reason})"
    )
    problems = []
    for svc in svcs:
        text, problem = call_service(svc, SYSTEM_PROMPT, user)
        if text:
            return text, None
        problems.append((svc, problem))
    return None, help_for(problems)


def link(text, anchor=""):
    return (f'<a href="{GUIDE_URL}{"#" + anchor if anchor else ""}" target="_blank">'
            f"{text}</a>")


def help_for(problems):
    """Plain, step-by-step help when no service could answer."""
    have = {s.get("provider") for s, _ in problems}
    first_svc, first = problems[0]
    kinds = {p for _, p in problems}
    if kinds == {"network"}:
        return ("Could not connect to the AI service. Check that your internet is working, "
                "then run the cell again. Your mark above works without the internet.")
    lines = []
    for svc, p in problems:
        name = service_name(svc)
        if p == "limit":
            lines.append(f"<b>{name}</b>: today's limit is used up. "
                         + PROVIDERS.get(svc.get("provider"), {}).get("reset", ""))
        elif p == "key":
            lines.append(f"<b>{name}</b> did not accept your key. Type <code>%tutor setup</code> "
                         f"in a new cell, choose {name} again and paste the key again. "
                         + link("Step-by-step help", PROVIDERS.get(svc.get("provider"), {})
                                .get("anchor", "")))
        elif p == "network":
            lines.append(f"<b>{name}</b> could not be reached. Check your internet connection.")
        else:
            lines.append(f"<b>{name}</b> had a problem answering. Try again in a minute.")
    if "limit" in kinds:
        missing = [n for n in ("groq", "gemini", "openrouter") if n not in have]
        tips = ["<b>Wait</b>, and keep practising: your ✅ marks work without the AI."]
        if missing:
            nm = PROVIDERS[missing[0]]["name"]
            tips.append(f"<b>Add a free backup</b>: type <code>%tutor setup</code> in a new cell "
                        f"and choose {nm}. When one service is used up, the tutor moves to "
                        f"the next. " + link(f"How to get a {nm} key",
                                              PROVIDERS[missing[0]]["anchor"]))
        if "deepseek" not in have:
            tips.append("<b>Never run out</b>: DeepSeek costs about US$1 for 1,500 feedback "
                        "messages. " + link("How to set it up", PROVIDERS["deepseek"]["anchor"]))
        lines.append("What you can do:<ul style='margin:4px 0 0 18px;padding:0'>"
                     + "".join(f"<li>{t}</li>" for t in tips) + "</ul>")
    return "<br>".join(lines)


def split_ai_verdict(text):
    first, _, rest = text.partition("\n")
    word = first.strip().strip("*").upper().replace(" ", "_")
    if word in ("CORRECT", "NEARLY", "NOT_YET"):
        return word.lower(), rest.strip()
    return None, text


# ---------------------------------------------------------------------------
# The card shown under an answer
# ---------------------------------------------------------------------------
STYLE = {
    "correct": ("✅", "Correct", "#1a7f37"),
    "nearly": ("🟡", "Nearly there", "#9a6700"),
    "not_yet": ("🔴", "Not yet", "#cf222e"),
    "error": ("🔴", "Not yet: Python found an error", "#cf222e"),
    "ran": ("▶️", "It ran", "#0969da"),
}


def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return s.replace("\n", "<br>")


def card(verdict, title_extra, reason, progress, ai_text=None, ai_note=None, waiting=False):
    icon, label, colour = STYLE[verdict]
    lines = [f"<div style='font-size:1.05em'><b>{icon} {label}</b>"
             f"{' · ' + md_inline(title_extra) if title_extra else ''}</div>"]
    if reason:
        lines.append(f"<div style='margin-top:4px'>{md_inline(reason)}</div>")
    if waiting:
        lines.append("<div style='margin-top:6px;opacity:.7'>🤖 Asking the tutor…</div>")
    if ai_text:
        lines.append(f"<div style='margin-top:6px'>🤖 {md_inline(ai_text)}</div>")
    if ai_note:
        lines.append(f"<div style='margin-top:6px'>🤖 {ai_note}</div>")
    if progress:
        lines.append(f"<div style='margin-top:6px;opacity:.75;font-size:.9em'>{progress}</div>")
    return (f"<div style='border-left:4px solid {colour};padding:8px 12px;margin:6px 0;"
            f"background:color-mix(in srgb, {colour} 9%, transparent);border-radius:4px;"
            f"font-family:var(--jp-ui-font-family, sans-serif);line-height:1.45'>"
            + "".join(lines) + "</div>")


# ---------------------------------------------------------------------------
# The IPython extension
# ---------------------------------------------------------------------------
class _Tee:
    """Copies what a cell prints, while still showing it."""

    def __init__(self, stream):
        self._stream, self.parts = stream, []

    def write(self, s):
        self.parts.append(s)
        return self._stream.write(s)

    def __getattr__(self, name):
        return getattr(self._stream, name)


class Tutor:
    def __init__(self, shell):
        self.shell = shell
        self.enabled = True
        self.tee = None
        self.tip_shown = False

    # hooks ------------------------------------------------------------------
    def pre_run_cell(self, info):
        self.tee = None
        if self.enabled and info.raw_cell.lstrip().startswith(ANSWER_STARTS):
            self.tee = _Tee(sys.stdout)
            sys.stdout = self.tee

    def post_run_cell(self, result):
        tee, self.tee = self.tee, None
        if tee is None:
            return
        sys.stdout = tee._stream
        try:
            self.check(result, "".join(tee.parts))
        except Exception as e:                       # the tutor must never break a lesson
            print(f"(The tutor had a problem: {type(e).__name__}: {e})")

    # marking ------------------------------------------------------------------
    def check(self, result, printed):
        from IPython.display import HTML, display
        info = result.info
        code = info.raw_cell
        body = "\n".join(l for l in code.splitlines() if not l.strip().startswith("#")).strip()
        if not body:
            return                                   # still empty: nothing to mark
        key = answer_key()
        entry = key["answers"].get(getattr(info, "cell_id", None) or "")
        if entry is None:
            return                                   # not a course answer cell we know
        label = entry["label"]

        error = None
        err = result.error_in_exec or result.error_before_exec
        if err is not None:
            error = f"{type(err).__name__}: {err}"

        shown = printed
        if result.result is not None and err is None:
            text = self.shell.display_formatter.format(result.result)[0].get("text/plain", "")
            if not re.search(r" at 0x[0-9a-fA-F]+>", text):    # a map or chart is a picture
                shown = (shown + "\n" + text).strip()

        if error:
            verdict = "error"
            hint = ERROR_HINTS.get(type(err).__name__, "Read the last line of the error first.")
            reason = f"`{error[:200]}`\n{hint} Errors are normal: every programmer sees them every day."
        else:
            ns = self.shell.user_ns
            got_vars = {n: fingerprint(ns[n]) for n in entry.get("vars", {}) if n in ns}
            verdict, reason = mark(entry, {"output": shown, "vars": got_vars})

        # progress
        prog = load_json(PROGRESS_FILE, {})
        solved = set(prog.get(entry["lesson"], []))
        if verdict in ("correct", "ran"):
            solved.add(info.cell_id)
            prog[entry["lesson"]] = sorted(solved)
            save_json(PROGRESS_FILE, prog)
        total = key["lessons"].get(entry["lesson"], 0)
        progress = f"⭐ {len(solved)} of {total} questions done in this lesson" if total else ""
        if verdict == "correct" and total and len(solved) == total:
            progress = f"🎉 All {total} questions in this lesson done. Outstanding work!"

        cheer = {"correct": PRAISE, "nearly": NEARLY, "not_yet": NOT_YET,
                 "error": NOT_YET, "ran": ["Good."]}[verdict]
        reason = f"{random.choice(cheer)} {reason}"

        cfg = load_json(CONFIG_FILE, {})
        has_ai = bool(services(cfg)) and cfg.get("ai", True)
        use_ai = has_ai and (verdict != "correct" or cfg.get("ai_on_correct", False))
        tip = None
        if not services(cfg) and verdict != "correct" and not self.tip_shown:
            self.tip_shown = True                    # once per session, never nagging
            tip = ("Want a personal hint as well? You can add a free AI tutor: type "
                   "<code>%tutor setup</code> in a new cell and follow the steps. "
                   + link("What is this?"))
        handle = display(HTML(card(verdict, label, reason, progress, ai_note=tip,
                                   waiting=bool(use_ai))), display_id=True)
        if not use_ai:
            return
        question, solution = lesson_text(entry["lesson"], info.cell_id)
        ai_text, note = ask_ai(cfg, question, solution, code, printed, error, verdict, reason)
        if ai_text:
            ai_verdict, ai_text = split_ai_verdict(ai_text)
            # The AI marks answers the automatic check cannot (plots, maps), and may raise
            # a mark when an answer is valid but solved another way. It never lowers a
            # mark, and an answer that raised an error stays "Not yet".
            rank = {"not_yet": 0, "nearly": 1, "correct": 2}
            if ai_verdict and (verdict == "ran" or rank.get(ai_verdict, -1) > rank.get(verdict, 9)):
                verdict, reason = ai_verdict, ""      # the AI's words explain the new mark
                if verdict == "correct":
                    solved.add(info.cell_id)
                    prog[entry["lesson"]] = sorted(solved)
                    save_json(PROGRESS_FILE, prog)
                    progress = f"⭐ {len(solved)} of {total} questions done in this lesson"
        handle.update(HTML(card(verdict, label, reason, progress, ai_text, note)))


# ---------------------------------------------------------------------------
# %tutor magic
# ---------------------------------------------------------------------------
BOX = ("<div style='border:1px solid rgba(127,127,127,.35);border-radius:6px;padding:10px 14px;"
       "margin:6px 0;font-family:var(--jp-ui-font-family, sans-serif);line-height:1.5'>{}</div>")


def show(html_text):
    from IPython.display import HTML, display
    display(HTML(BOX.format(html_text)))


def tutor_magic(line):
    args = line.split()
    t = _TUTOR
    cfg = load_json(CONFIG_FILE, {})
    if not args:
        svcs = services(cfg)
        ai = (", then ".join(service_name(s) for s in svcs) if svcs else "not set up")
        paused = " (paused: type <code>%tutor ai on</code>)" if svcs and not cfg.get("ai", True) else ""
        show(f"<b>Marking:</b> {'on' if t.enabled else 'off'}<br>"
             f"<b>AI tutor:</b> {ai}{paused}<br>"
             "<b>Commands</b> (type one in a cell and run it):<br>"
             "<code>%tutor setup</code> add an AI service · <code>%tutor help</code> the guide · "
             "<code>%tutor progress</code> your progress · <code>%tutor ai off</code> pause the AI · "
             "<code>%tutor remove gemini</code> remove a service")
    elif args[0] in ("on", "off"):
        t.enabled = args[0] == "on"
        print(f"Marking is {args[0]}.")
    elif args[:2] in (["ai", "on"], ["ai", "off"]):
        cfg["ai"] = args[1] == "on"
        save_json(CONFIG_FILE, cfg)
        print(f"AI tutor {args[1]}.")
    elif args[0] == "progress":
        prog, key = load_json(PROGRESS_FILE, {}), answer_key()
        rows = [(Path(lesson).stem.replace("_", " "), len(prog.get(lesson, [])), total)
                for lesson, total in key["lessons"].items() if prog.get(lesson)]
        if not rows:
            print("No answers marked yet. Run an answer cell to start.")
        for name, done, total in rows:
            print(f"{name:48s} {'⭐' if done == total else '  '} {done:3d} / {total}")
    elif args[0] == "reset":
        save_json(PROGRESS_FILE, {})
        print("Progress cleared.")
    elif args[0] == "setup":
        setup(cfg)
    elif args[0] == "help":
        show("The full step-by-step guide, with pictures in words: "
             + link("How to use the PyGILE tutor and get a free AI key"))
    elif args[0] == "remove" and len(args) == 2:
        before = services(cfg)
        cfg["services"] = [s for s in before if s.get("provider") != args[1].lower()]
        cfg.pop("provider", None)
        save_json(CONFIG_FILE, cfg)
        print("Removed." if len(cfg["services"]) < len(before) else f"No service called {args[1]}.")
    else:
        print("Unknown command. Type  %tutor  to see the commands.")


def setup(cfg):
    from getpass import getpass
    svcs = services(cfg)
    have = {s.get("provider") for s in svcs}
    names = list(PROVIDERS)
    rows = "".join(
        f"<tr><td style='padding:2px 10px 2px 0'><b>{i}</b></td>"
        f"<td style='padding:2px 10px 2px 0'><b>{PROVIDERS[n]['name']}</b>"
        f"{' ✓ already added' if n in have else ''}</td><td>{PROVIDERS[n]['cost']}</td></tr>"
        for i, n in enumerate(names, 1))
    show("<b>🤖 Add an AI tutor</b><br>"
         "The AI tutor writes a short, personal hint under your answers. "
         "Your ✅ marks work without it.<br><br>"
         f"<table style='border-collapse:collapse'>{rows}</table><br>"
         "<b>New here? Choose 1.</b> You can add more later as backups: when one reaches "
         "its daily limit, the tutor moves to the next.<br><br>"
         "<span style='opacity:.8'>Good to know: Google's Gemini service is for people aged "
         "18 or older. Only the question and your code are sent, never your name, but free "
         "services may let their staff read what is sent. So never type personal "
         "information in an answer cell. " + link("Read the full guide") + "</span>")
    pick = input("Type a number (1 to 4) and press Enter. Press Enter alone to stop: ").strip()
    if not pick.isdigit() or not 1 <= int(pick) <= len(names):
        print("Stopped. Nothing was changed.")
        return
    name = names[int(pick) - 1]
    prov = PROVIDERS[name]
    steps = "".join(f"<li>{st}</li>" for st in prov["steps"])
    show(f"<b>Get your {prov['name']} key</b>"
         f"<ol style='margin:6px 0 6px 20px;padding:0'>{steps}"
         "<li>Come back to this page. Click in the box below, paste the key "
         "(<b>Ctrl+V</b>, or <b>Cmd+V</b> on a Mac) and press <b>Enter</b>. "
         "The key stays hidden while you paste. That is normal: it keeps it safe.</li></ol>"
         "<span style='opacity:.8'>A key is like a password. Do not share it or put it in a "
         "notebook. It is saved only on this computer. "
         + link("Stuck? Step-by-step help", prov["anchor"]) + "</span>")
    key = getpass("Paste your key and press Enter: ").strip().strip('"').strip("'")
    if not key:
        print("Stopped. Nothing was changed.")
        return
    svc = {"provider": name, "key": key, "model": prov["model"]}
    print("Checking the key…")
    text, problem = call_service(svc, "Reply with the single word OK.", "Say OK.")
    if problem == "key":
        show(f"🔴 <b>{prov['name']} did not accept that key.</b> Check that you copied all of it, "
             "with nothing extra. Then type <code>%tutor setup</code> and try again. "
             + link("Step-by-step help", prov["anchor"]))
        return
    cfg["services"] = [s for s in svcs if s.get("provider") != name] + [svc]
    cfg.pop("provider", None)
    cfg.setdefault("ai", True)
    save_json(CONFIG_FILE, cfg)
    if problem is None:
        msg = (f"✅ <b>{prov['name']} is working!</b> Run any answer cell to get your first hint.")
    elif problem == "limit":
        msg = (f"✅ <b>Your key is saved.</b> Today's limit is already used, so hints start "
               f"again later. {prov['reset']}")
    elif problem == "network":
        msg = ("✅ <b>Your key is saved</b>, but it could not be checked, because the internet "
               "could not be reached. Hints will start when you are online.")
    else:
        msg = ("✅ <b>Your key is saved</b>, but the service did not answer the test. "
               "Try an answer cell in a few minutes.")
    if len(cfg["services"]) == 1:
        backup = "groq" if name != "groq" else "gemini"
        msg += (f"<br><br>💡 Tip: add a second free service as a backup, so your hints do not stop "
                f"when one reaches its daily limit. Type <code>%tutor setup</code> again and "
                f"choose {PROVIDERS[backup]['name']}.")
    show(msg)


_TUTOR = None


def load_ipython_extension(shell):
    global _TUTOR
    if _TUTOR is not None:
        return
    _TUTOR = Tutor(shell)
    shell.events.register("pre_run_cell", _TUTOR.pre_run_cell)
    shell.events.register("post_run_cell", _TUTOR.post_run_cell)
    shell.register_magic_function(tutor_magic, "line", "tutor")


def unload_ipython_extension(shell):
    global _TUTOR
    if _TUTOR is None:
        return
    shell.events.unregister("pre_run_cell", _TUTOR.pre_run_cell)
    shell.events.unregister("post_run_cell", _TUTOR.post_run_cell)
    _TUTOR = None
