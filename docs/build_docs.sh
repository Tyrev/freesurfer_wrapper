# Automation script to build the documentation.
# Please run after every code modification.
# ------------------------------------------
# REQUIREMENTS
# pdoc: pip install pdoc3
# pandoc: apt-get install pandoc
# TeX: apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-recommended
# ------------------------------------------
# USAGE
# bash ./build_docs.sh
# ------------------------------------------
rm -R html markdown pdf
mkdir html markdown pdf
pdoc --force --html ../ --output-dir html 
pdoc --force --pdf ../ > markdown/docs.md
pandoc --metadata=title:"FreeSurfer Multiprocessing Pipeline" \
       --from=markdown+abbreviations+tex_math_single_backslash \
       --pdf-engine=xelatex \
       --variable=mainfont:"DejaVu Sans" \
       --toc \
       --toc-depth=4 \
       --output=pdf/docs.pdf \
    markdown/docs.md