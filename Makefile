IMAGES:=$(shell ls *.jpg)
VIEWS:=$(IMAGES:%.jpg=%.view)

all: $(VIEWS)

.PHONY:
%.view:%.stl
	meshlab $^ 2> /dev/null

%.stl:%.py
	python $<

%.stl:%.jpg stlFromImage.py
	python stlFromImage.py $< $@

.PHONY:
clean:
	rm *.stl *.pyc
