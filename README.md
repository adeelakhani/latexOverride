# Resume builder

Three standalone resume versions — edit any one like a normal LaTeX file, then
run `./build.sh` to produce all PDFs. A `sync` command copies selected sections
from one version to the others so you only edit common content once.

## Files

```
swe.tex     ml.tex     agents.tex   # 3 versions, edit these
build.sh    build.py                 # entry point + logic
out/                                 # generated PDFs land here
```

Every version compiles to **two** PDFs:
- `out/<name>.pdf` — Education near the top (as written)
- `out/<name>_e.pdf` — Education moved to the bottom (auto-generated)

So `./build.sh` produces 6 PDFs: `swe.pdf`, `swe_e.pdf`, `ml.pdf`, `ml_e.pdf`, `agents.pdf`, `agents_e.pdf`.

## Commands

**Build all PDFs (no sync):**
```bash
./build.sh
```

**Sync sections from one version to the others, then build:**
```bash
./build.sh sync swe       # copy chosen sections from swe.tex -> ml.tex, agents.tex
./build.sh sync ml        # same but ml.tex as source
./build.sh sync agents
```

Sync prompts you per section:
```
  Education          [y/N]: y
  Technical Skills   [y/N]: y
  Experience         [y/N]: y
  Projects           [y/N]: n
```
Whatever you answer `y` to gets overwritten in the target files.

## Typical workflow

1. Edit `swe.tex` (fix a bullet, add a project, whatever).
2. Run `./build.sh sync swe`.
3. Answer `y` for Experience / Skills (changes you want everywhere), `n` for Projects (since those differ per version).
4. All 6 PDFs regenerate.

## Recovery

Each `.tex` is fully self-contained — no shared imports. If you mess up:
- Open Overleaf, copy the original version, paste it back into the file, run `./build.sh`.

Sync does **not** make automatic backups. If you wipe something via sync and don't notice for a while, recover from Overleaf.
