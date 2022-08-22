
help:
	@echo "Help file here"

local:
	python setup.py build

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

clean:
	rm -rf ./build
	rm -rf ./dist
	rm -rf pdpy.egg-info

test:
	tox

version:
	cd scripts && python touch_version.py

all:
	make clean
	make version
	make build
	make deploy
	echo "waiting 10 seconds for pypi to update"
	sleep 10
	make install
	echo "Done with all"

