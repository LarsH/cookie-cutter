
all: julgran.view

.PHONY:
%.view:%.stl
	meshlab $^ 2> /dev/null

%.stl:%.py
	python $<

.PHONY:
clean:
	rm *.stl *.pyc
