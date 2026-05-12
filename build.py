#!/usr/bin/env python3
"""
Build resume PDFs from swe.tex / ml.tex / agents.tex.

Each version compiles to TWO PDFs:
  out/regular/<name>.pdf       - Education near the top (as written in the .tex)
  out/edu-bottom/<name>_e.pdf  - Education moved to the bottom (auto-generated)

Sync mode lets you push selected sections from one version to the others
before compiling.

Usage:
    ./build.sh                  # compile every version (no sync)
    ./build.sh sync swe         # ask which sections to copy from swe.tex
                                #   into ml.tex and agents.tex, then compile
    ./build.sh sync ml          # same but ml.tex as the source
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
AUX_DIR = OUT_DIR / ".aux"
REGULAR_DIR = OUT_DIR / "regular"
EDU_BOTTOM_DIR = OUT_DIR / "edu-bottom"
TMP_DIR = ROOT / ".build"

VERSIONS = ["swe", "ml", "agents"]
SYNCABLE_SECTIONS = ["Education", "Technical Skills", "Experience", "Projects"]


# ---------- section-level surgery ----------------------------------------

def _section_re(name: str) -> re.Pattern:
    return re.compile(rf"\\section\{{{re.escape(name)}\}}")


def find_section_bounds(content: str, name: str) -> tuple[int, int] | None:
    m = _section_re(name).search(content)
    if not m:
        return None
    after = content[m.end():]
    next_m = re.search(r"\\section\{|\\end\{document\}", after)
    end = m.end() + next_m.start() if next_m else len(content)
    return (m.start(), end)


def get_section(content: str, name: str) -> str | None:
    bounds = find_section_bounds(content, name)
    return content[bounds[0]:bounds[1]] if bounds else None


def replace_section(content: str, name: str, new_block: str) -> str:
    bounds = find_section_bounds(content, name)
    if bounds is None:
        return content
    return content[:bounds[0]] + new_block + content[bounds[1]:]


def move_education_to_bottom(content: str) -> str:
    """Return content with the Education section moved before \\end{document}."""
    edu = get_section(content, "Education")
    if edu is None:
        return content
    without_edu = replace_section(content, "Education", "")
    without_edu = re.sub(r"\n{3,}", "\n\n", without_edu)
    return without_edu.replace(
        r"\end{document}",
        edu.rstrip() + "\n\n\\end{document}",
        1,
    )


# ---------- sync mode ----------------------------------------------------

def confirm(label: str) -> bool:
    resp = input(f"  {label:<18} [y/N]: ").strip().lower()
    return resp in ("y", "yes")


def sync_mode(source: str) -> None:
    if source not in VERSIONS:
        sys.exit(f"error: source must be one of {VERSIONS}, got '{source}'")
    src_path = ROOT / f"{source}.tex"
    if not src_path.exists():
        sys.exit(f"error: {src_path.name} not found")

    targets = [v for v in VERSIONS if v != source]
    print(f"sync source: {source}.tex")
    print(f"targets:     {', '.join(t + '.tex' for t in targets)}\n")
    print("which sections should overwrite the targets?")

    chosen = [s for s in SYNCABLE_SECTIONS if confirm(s)]
    if not chosen:
        print("\nnothing selected, skipping sync.\n")
        return

    src_content = src_path.read_text()
    print()
    for t in targets:
        tpath = ROOT / f"{t}.tex"
        tcontent = tpath.read_text()
        for sec in chosen:
            block = get_section(src_content, sec)
            if block is not None:
                tcontent = replace_section(tcontent, sec, block)
        tpath.write_text(tcontent)
        print(f"  updated {t}.tex  ({', '.join(chosen)})")
    print()


# ---------- compile ------------------------------------------------------

def compile_tex(tex_path: Path, dest_dir: Path) -> bool:
    """Compile tex_path, drop the .pdf into dest_dir, keep aux/log in OUT_DIR/.aux."""
    AUX_DIR.mkdir(parents=True, exist_ok=True)
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"==> {tex_path.relative_to(ROOT)}")
    cmd = [
        "pdflatex",
        "-output-directory", str(AUX_DIR),
        "-interaction=nonstopmode",
        str(tex_path),
    ]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

    aux_pdf = AUX_DIR / (tex_path.stem + ".pdf")
    dest_pdf = dest_dir / (tex_path.stem + ".pdf")

    if result.returncode != 0 or not aux_pdf.exists():
        print(f"    FAILED — see out/.aux/{tex_path.stem}.log")
        return False

    shutil.move(str(aux_pdf), str(dest_pdf))

    log = AUX_DIR / (tex_path.stem + ".log")
    pages = "?"
    if log.exists():
        flat = log.read_text(errors="ignore").replace("\n", "")
        m = re.search(r"Output written on [^(]+\((\d+) pages?", flat)
        if m:
            pages = m.group(1)
    print(f"    -> {dest_pdf.relative_to(ROOT)} ({pages} page{'s' if pages != '1' else ''})")
    return True


def build_all() -> None:
    TMP_DIR.mkdir(exist_ok=True)
    for v in VERSIONS:
        src = ROOT / f"{v}.tex"
        if not src.exists():
            print(f"skip: {v}.tex not found")
            continue
        compile_tex(src, REGULAR_DIR)
        e_tex = TMP_DIR / f"{v}_e.tex"
        e_tex.write_text(move_education_to_bottom(src.read_text()))
        compile_tex(e_tex, EDU_BOTTOM_DIR)


# ---------- entry --------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "sync":
        if len(args) < 2:
            sys.exit("usage: ./build.sh sync {swe|ml|agents}")
        sync_mode(args[1])
    build_all()


if __name__ == "__main__":
    main()
