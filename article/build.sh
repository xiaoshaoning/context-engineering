#!/usr/bin/env bash
# figures: python build.py (svg->pdf, raster fallback) then: bash build.sh
set -e
cd "$(dirname "$0")"
mkdir -p build
python build.py            # cached: only traces slides that are missing (--force to redo)
PAN="/c/Users/xiaos/AppData/Roaming/Python/Python313/site-packages/pypandoc/files/pandoc.exe"
"$PAN" build/build.md -f markdown -t latex --standalone -H header.tex \
  -V documentclass=article -V fontsize=11pt -V lang=en \
  -V title-meta="The State of Context Engineering" -V author-meta="Drew Breunig" \
  -o build/state-of-context-engineering.tex
for i in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=build build/state-of-context-engineering.tex > "build/log$i.txt" || {
    grep -A4 '^! ' "build/log$i.txt" | head -20; exit 1; }
done
cp build/state-of-context-engineering.pdf .
grep -o 'Output written.*' build/log2.txt
