SOURCE = 3d-gaussian-distribution
TARGET = $(SOURCE).pdf
DELAY = 80
DENSITY = 300
WIDTH = 512

.PHONY: all clean gif png transparentGif svg

all: $(TARGET)

$(TARGET): $(SOURCE).tex
	pdflatex -interaction=nonstopmode -halt-on-error $<

clean:
	rm -rf $(TARGET) *.log *.aux *.svg *.png *.gif *.crop.pdf

gif: $(TARGET)
	pdfcrop $(TARGET)
	convert -verbose -delay $(DELAY) -loop 0 -density $(DENSITY) $(SOURCE)-crop.pdf $(SOURCE).gif
	make clean

png: $(TARGET)
	pdfcrop $(TARGET)
	inkscape $(SOURCE)-crop.pdf -w $(WIDTH) --export-png=$(SOURCE).png
	make clean

transparentGif: $(TARGET)
	pdfcrop $(TARGET)
	convert $(SOURCE)-crop.pdf -transparent white $(SOURCE).gif
	make clean

svg: $(TARGET)
	pdfcrop $(TARGET)
	pdf2svg $(SOURCE)-crop.pdf $(SOURCE).svg
