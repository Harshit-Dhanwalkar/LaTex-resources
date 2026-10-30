LUALATEX = $(RUN) lualatex -interaction=nonstopmode -halt-on-error
SEEDS   ?= 1 2 3 4 5 6
# RUN=tools/in-docker builds inside the florilegium-tex image (see tools/Dockerfile)
RUN     ?=
LUA      = ink.lua flora.lua florilegium.lua initial.lua

all: florilegium.pdf florilegium-grow.pdf showcase.pdf

# authored composition (authored.lua), one pass, about a second a page
florilegium.pdf: florilegium.tex florilegium.sty authored.lua grow.lua $(LUA) text-methods.tex text-sharing.tex
	$(LUALATEX) florilegium.tex

# grown composition (grow.lua), one pass: the end of the text is measured with \pagetotal
florilegium-grow.pdf: florilegium-grow.tex florilegium.sty grow.lua $(LUA) text-methods.tex text-growth.tex text-sharing.tex
	$(LUALATEX) florilegium-grow.tex

# initials, flowers at the headings, visitors and the seasons; two passes, because
# the option aging reads the page count of the first one
showcase.pdf: showcase.tex florilegium.sty grow.lua $(LUA)
	$(LUALATEX) showcase.tex
	$(LUALATEX) showcase.tex

# one of every primitive, drawn with \florilegiumdraw
specimen.pdf: specimen.tex florilegium.sty $(LUA)
	$(LUALATEX) specimen.tex

# one page for one seed:  make seed-7  ->  build/seed-7.pdf
seed-%: gallery.tex florilegium.sty grow.lua $(LUA)
	mkdir -p build
	$(LUALATEX) -jobname=build/seed-$* "\def\florilegiumseed{$*}\input{gallery.tex}"

# contact sheets: seeds (+ gif), one seed in six inks, one seed through the seasons
# (needs python3 + Pillow + pdftoppm)
gallery: gallery.tex florilegium.sty grow.lua $(LUA) tools/gallery.py
	python3 tools/gallery.py --seeds $(SEEDS) --run "$(RUN)"
	python3 tools/gallery.py --seed 6 --inks 2456C4 5B2A1F 2F6B4F 8E1B3A 4B3B8F 1D6E7A --run "$(RUN)"
	python3 tools/gallery.py --seed 6 --ages 0 0.33 0.67 1 --run "$(RUN)"

# the growth of one seed:  make grow-7  ->  build/grow-7.gif and .mp4 (MP4 needs ffmpeg);
# EXPLAIN=1 also marks the free disc each branch grows to  ->  build/grow-7-explain.*
grow-%: animation.tex florilegium.sty grow.lua $(LUA) tools/animate.py
	python3 tools/animate.py --seed $* --run "$(RUN)" $(if $(EXPLAIN),--explain)

# the README's animations (seed 6: all four visitors)
animation:
	$(MAKE) grow-6 RUN="$(RUN)"
	$(MAKE) grow-6 RUN="$(RUN)" EXPLAIN=1
	cp build/grow-6.gif gallery/growth.gif
	cp build/grow-6-explain.gif gallery/growth-explain.gif

preview: florilegium.pdf florilegium-grow.pdf showcase.pdf
	mkdir -p gallery
	pdftoppm -png -r 60 -f 1 -l 1 -singlefile florilegium.pdf gallery/preview-authored
	pdftoppm -png -r 60 -f 1 -l 1 -singlefile florilegium-grow.pdf gallery/preview-grown
	pdftoppm -png -r 45 showcase.pdf build/showcase
	python3 -c "from PIL import Image; import glob; \
	  ims = [Image.open(f).convert('RGB') for f in sorted(glob.glob('build/showcase-*.png'))]; w, h = ims[0].size; \
	  s = Image.new('RGB', (len(ims) * (w + 8) + 8, h + 16), (235, 235, 240)); \
	  [s.paste(im, (8 + i * (w + 8), 8)) for i, im in enumerate(ims)]; s.save('gallery/preview-showcase.png')"

clean:
	rm -rf build *.aux *.log *.out *.synctex.gz

.PHONY: all gallery animation preview clean
