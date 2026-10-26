#!/usr/bin/env bash
# figures: python build.py (svg->pdf, raster fallback) then: bash build.sh
set -e
cd "$(dirname "$0")"
[ "$1" = "figs" ] && python build.py
PAN="/c/Users/xiaos/AppData/Roaming/Python/Python313/site-packages/pypandoc/files/pandoc.exe"
"$PAN" build.md -f markdown -t latex --standalone -H header.tex \
  -V documentclass=article -V fontsize=11pt -V lang=en \
  -V title-meta="The State of Context Engineering" -V author-meta="Drew Breunig" \
  -o state-of-context-engineering.tex
for i in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error state-of-context-engineering.tex > "log$i.txt" || {
    grep -A4 '^! ' "log$i.txt" | head -20; exit 1; }
done
grep -o 'Output written.*' log2.txt
