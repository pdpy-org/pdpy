

override filename
examples := $(wildcard *.py)
override pd=/Applications/Pd-0.52-2.app/Contents/Resources/bin/pd

single:
	python $(filename).py 2>&1 > log.txt && $(pd) $(filename).pd

all: $(examples)
	@for example in $(examples); do \
		. ~/.pdpy/bin/activate; \
		echo BEGIN $$example example; \
		python $$example; \
		echo END; \
	done

clean:
	rm *.pd
	rm *.json