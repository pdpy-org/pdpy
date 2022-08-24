# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #

override pd := /Applications/Pd-0.52-2.app/Contents/Resources/bin/pd
override filename := ""

examples := $(wildcard *.py)
output := $(wildcard *.pd)

all: $(examples)
	@for e in $(examples); do \
		. ~/.pdpy/bin/activate; \
		echo "==> BEGIN $$e <==================================="; \
		python $$e; \
		echo "==> END $$e <==================================="; \
	done

check: $(output)
	@for f in $(output); do \
		$(pd) -open $$f; \
	done

clean:
	rm *.pd
	rm *.json

single:
	python $(filename).py 2>&1 > log.txt && $(pd) $(filename).pd