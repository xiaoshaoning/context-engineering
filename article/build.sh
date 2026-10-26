#!/usr/bin/env bash
# figures: python build.py (svg->pdf, raster fallback) then: bash build.sh
set -e
cd "$(dirname "$0")"
mkdir -p build
python build.py            # cached: only traces slides that are missing (--force to redo)
PAN=$(command -v pandoc)
if [ -z "$PAN" ] || ! "$PAN" --version >/dev/null 2>&1; then   # broken shims exist
  PAN=$(python -c "import pypandoc; print(pypandoc.get_pandoc_path())" 2>/dev/null)
fi
"$PAN" --version >/dev/null 2>&1 || {
  echo "pandoc not found: install pandoc, or pip install pypandoc-binary"; exit 1; }
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
