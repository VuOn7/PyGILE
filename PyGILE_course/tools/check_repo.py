"""Fast consistency checks for the PyGILE repository (no lessons are run).

1. Every lesson is saved without outputs (STYLE_GUIDE.md).
2. The navigation bars are up to date (add_nav.py --check).
3. The three step-by-step installers install exactly the packages in
   environment.yml, with the same versions.
4. The question counts in the READMEs match the lessons.
5. The tutor's answer key (tools/answer_key.json) has every answer cell.

Usage, from anywhere:  python PyGILE_course/tools/check_repo.py
Exit code 1 if anything fails. Needs only nbformat and PyYAML.
"""
import re
import shlex
import sys
from pathlib import Path

import nbformat
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_nav  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "PyGILE_course"
problems = []


def fail(msg):
    problems.append(msg)
    print(f"FAIL {msg}")


lessons = add_nav.lessons()

# 1. No outputs ------------------------------------------------------------
for path in lessons:
    nb = nbformat.read(path, as_version=4)
    dirty = [i for i, c in enumerate(nb.cells)
             if c.cell_type == "code" and (c.outputs or c.execution_count)]
    if dirty:
        fail(f"{path.relative_to(ROOT)}: saved with outputs in cells {dirty[:5]}. "
             "Clear all outputs before saving.")

# 2. Navigation bars --------------------------------------------------------
if not add_nav.main(check=True):
    fail("navigation bars are out of date (see above)")

# 3. Installers match environment.yml ---------------------------------------
env = yaml.safe_load((ROOT / "environment.yml").read_text(encoding="utf-8"))
wanted = {re.sub(r"\s+", "", d) for d in env["dependencies"] if isinstance(d, str)}


def bash_packages(path):
    text = path.read_text(encoding="utf-8").replace("\\\n", " ")
    found = set()
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("install_group "):
            found |= set(shlex.split(line)[3:])          # skip name, step, description
        if line.startswith("if ! $INSTALLER create "):
            found |= {a for a in shlex.split(line) if a.startswith("python=")}
    return found


def bat_packages(path):
    found = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("call :install_group "):
            found |= set(shlex.split(line)[4:])          # skip call, label, step, description
        if " create -n pygile " in line:
            found |= {a for a in shlex.split(line) if a.startswith("python=")}
    return found


installers = {
    "environments/linux/install_pygile_linux.sh": bash_packages,
    "environments/mac/install_pygile_macos.sh": bash_packages,
    "environments/windows/install_pygile_windows.bat": bat_packages,
}
for rel, reader in installers.items():
    got = reader(ROOT / rel)
    if got != wanted:
        missing, extra = sorted(wanted - got), sorted(got - wanted)
        fail(f"{rel} does not match environment.yml. Missing: {missing}. Extra: {extra}")

# 4. Question counts in the READMEs ---------------------------------------
def n_questions(path):
    nb = nbformat.read(path, as_version=4)
    return sum(1 for c in nb.cells if c.cell_type == "code"
               and (c.source.startswith("# Q") or c.source.startswith("# Your answer")))


counts = {p.relative_to(COURSE).as_posix(): n_questions(p) for p in lessons}
course_readme = (COURSE / "README.md").read_text(encoding="utf-8")
listed = dict(re.findall(r"\]\(([A-E]_\w+/[A-E]\d\d_\w+\.ipynb)\)\s*\|[^|]*\|\s*(\d+)\s*\|",
                         course_readme))
for rel, n in counts.items():
    if rel not in listed:
        fail(f"PyGILE_course/README.md has no table row for {rel}")
    elif int(listed[rel]) != n:
        fail(f"PyGILE_course/README.md says {rel} has {listed[rel]} questions; it has {n}")

for part, total in re.findall(r"\*\*Part ([A-E]) total: ([\d,]+) questions", course_readme):
    real = sum(n for rel, n in counts.items() if rel.startswith(part + "_"))
    if int(total.replace(",", "")) != real:
        fail(f"PyGILE_course/README.md says Part {part} has {total} questions; it has {real}")

grand = sum(counts.values())
for readme in (ROOT / "README.md", COURSE / "README.md"):
    text = readme.read_text(encoding="utf-8")
    claims = re.findall(r"(\d{1,3}(?:,\d{3})+|\d{4,}) (?:practice )?questions", text)
    for claim in claims:
        if int(claim.replace(",", "")) != grand:
            fail(f"{readme.relative_to(ROOT)} says {claim} questions in total; there are {grand:,}")
    for claim in re.findall(r"(\d+) lessons", text):
        if int(claim) > 20 and int(claim) != len(lessons):       # skip per-part counts
            fail(f"{readme.relative_to(ROOT)} says {claim} lessons; there are {len(lessons)}")
    for part, claim in re.findall(r"Part ([A-E]) · [^(\n]*\((\d+) lessons\)", text):
        real = sum(1 for rel in counts if rel.startswith(part + "_"))
        if int(claim) != real:
            fail(f"{readme.relative_to(ROOT)} says Part {part} has {claim} lessons; it has {real}")

# 5. Tutor answer key ------------------------------------------------------
import json  # noqa: E402

key_file = COURSE / "tools" / "answer_key.json"
key = json.loads(key_file.read_text(encoding="utf-8"))["answers"] if key_file.exists() else {}
for path in lessons:
    rel = path.relative_to(COURSE).as_posix()
    nb = nbformat.read(path, as_version=4)
    ids = {c.id for c in nb.cells if c.cell_type == "code"
           and (c.source.startswith("# Q") or c.source.startswith("# Your answer"))}
    keyed = {i for i, v in key.items() if v["lesson"] == rel}
    if ids != keyed:
        fail(f"{rel}: the tutor's answer key is out of date ({len(ids - keyed)} answer cells missing, "
             f"{len(keyed - ids)} extra). Run: python PyGILE_course/tools/build_answer_key.py {rel}")

print(f"{'PASS' if not problems else 'FAIL'}: {len(lessons)} lessons, {grand:,} questions, "
      f"{len(installers)} installers checked, {len(problems)} problems")
sys.exit(1 if problems else 0)
