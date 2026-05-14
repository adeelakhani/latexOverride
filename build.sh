#!/bin/bash
# Thin wrapper around build.py. See build.py for full usage.
#
#   ./build.sh                  build 7 PDFs (3 resumes x 2 layouts + out/coverletter.pdf)
#   ./build.sh sync swe         interactively sync sections from swe.tex
#                                 into ml.tex and agents.tex, then build

set -e
cd "$(dirname "$0")"

# Ensure /Library/TeX/texbin is on PATH (BasicTeX install location)
if [ -d /Library/TeX/texbin ] && [[ ":$PATH:" != *":/Library/TeX/texbin:"* ]]; then
    export PATH="/Library/TeX/texbin:$PATH"
fi

# Point TeX at the project-local package tree — nothing leaks to ~/Library
export TEXMFHOME="$(pwd)/texmf"
export TEXMFVAR="$(pwd)/texmf-var"
export TEXMFCONFIG="$(pwd)/texmf-config"

exec python3 build.py "$@"
