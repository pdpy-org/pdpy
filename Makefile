
local:
	python setup.py build

help:
	@echo "Help file here"

doc:
	cd docs && make html


build:
	python -m build

activate:
	source ~/.pdpy/bin/activate

deploy:
	python -m twine upload --repository testpypi dist/*

install:
	python -m pip install -i https://test.pypi.org/simple/ $(shell ./scripts/get_version.sh ./pyproject.toml ==)

dist:
	python setup.py sdist

publish:
	python -m twine upload dist/* --verbose

clean:
	rm -rf ./build
	rm -rf ./dist
	rm -rf *.egg-info

test:
	tox

version:
	cd scripts && python touch_version.py
	./scripts/make_setup.sh > setup.py
	git add pyproject.toml && git commit -m 'bump version number'
	cd ../doc && git add version.txt && git commit -m 'bump version number'

all:
	make clean
	make version
	make build
	make deploy
	echo "waiting 10 seconds for pypi to update"
	sleep 10
	make install
	echo "Done with all"

