
all: julgran.view

.PHONY:
%.view:%.stl
	meshlab $^

%.stl:%.py
	python $<

.PHONY:
clean:
	rm *.stl *.pyc
