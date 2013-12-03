IMAGES:=$(shell ls *.png)
VIEWS:=$(IMAGES:%.png=%.view)

all: $(VIEWS)

.PHONY:
%.view:%.stl
	meshlab $^ 2> /dev/null

%.stl:%.py
	python $<

%.stl:%.png stlFromImage.py
	python stlFromImage.py $< $@

.PHONY:
clean:
	rm *.stl *.pyc
