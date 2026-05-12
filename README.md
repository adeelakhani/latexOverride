# Resume Builder

Three standalone LaTeX resumes, one build command, optional section-level sync between them.

---

## Quick Start

```bash
./build.sh                        # build all 6 PDFs
./build.sh sync swe               # copy chosen sections from swe.tex into ml + agents
./build.sh sync swe agents        # same but agents.tex only
```

---

## Project Layout

```
.
├── swe.tex          ← edit these like normal LaTeX files
├── ml.tex
├── agents.tex
├── build.sh         ← entry point
├── build.py         ← sync + compile logic
└── out/
    ├── regular/             Education near the top
    │   ├── swe.pdf
    │   ├── ml.pdf
    │   └── agents.pdf
    └── edu-bottom/          Education moved to the bottom (auto-generated)
        ├── swe_e.pdf
        ├── ml_e.pdf
        └── agents_e.pdf
```

LaTeX aux/log files live in `out/.aux/` — ignore unless a build fails.

---

## How Sync Works

Run `./build.sh sync <source>` and you'll be prompted per section:

```
  Education          [y/N]: y
  Technical Skills   [y/N]: y
  Experience         [y/N]: y
  Projects           [y/N]: n
```

What actually gets copied depends on the section:

| Section              | What sync copies                                                          |
| -------------------- | ------------------------------------------------------------------------- |
| **Experience**       | **Bullets only.** Job titles, dates, companies, locations stay untouched. |
| **Projects**         | **Full block.** Project names, tech stacks, dates, bullets — all replaced. |
| **Education**        | Full section.                                                             |
| **Technical Skills** | Full section.                                                             |

So if you fix a Boardy bullet in `swe.tex` and sync Experience, `ml.tex` and `agents.tex` get the new bullet but keep their own job titles (e.g. "AI Engineering Intern" vs "Software Engineering Intern").

---

## Sync Targets

```bash
./build.sh sync swe              # → ml.tex + agents.tex (both, default)
./build.sh sync swe agents       # → agents.tex only
./build.sh sync swe ml           # → ml.tex only
./build.sh sync ml               # → swe.tex + agents.tex
./build.sh sync agents           # → swe.tex + ml.tex
```

---

## Typical Workflow

1. Edit `swe.tex` — fix bullets, retitle a job, add a project, whatever.
2. Run `./build.sh sync swe`.
3. Answer `y` for sections to propagate, `n` for ones that should stay version-specific.
4. All 6 PDFs regenerate.

---

## Recovery

Each `.tex` is fully self-contained — no shared imports, no dependencies between files.

If you mess something up:

1. Open the original in Overleaf.
2. Paste it back into the affected `.tex` file.
3. Run `./build.sh`.

> **Note:** `sync` does **not** make automatic backups. If you sync the wrong section and don't notice for a while, the old content in the target file is gone — recover from Overleaf.
