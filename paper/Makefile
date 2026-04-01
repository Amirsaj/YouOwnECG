TEX = pdflatex
BIB = bibtex
MAIN = main

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib
	$(TEX) $(MAIN)
	$(BIB) $(MAIN)
	$(TEX) $(MAIN)
	$(TEX) $(MAIN)

figures:
	python3 generate_figures.py

clean:
	rm -f $(MAIN).{aux,bbl,blg,log,out,pdf,toc,lof,lot}

.PHONY: all figures clean
