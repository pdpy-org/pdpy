
build:
	python3 -m build

activate:
	source ~/.pdpy/bin/activate

deploy:
	python3 -m twine upload --repository testpypi dist/*

local:
	python3 -m pip install ./dist/$(shell ./scripts/get_version.sh ./pyproject.toml -).tar.gz

install:
	python3 -m pip install -i https://test.pypi.org/simple/ $(shell ./scripts/get_version.sh ./pyproject.toml ==)

play:
	make activate && python3

clean:
	rm -rf ./build
	rm -rf ./dist

test:
	tox

version:
	python3 ./scripts/version.py 

all:
	make version
	make build
	make deploy
	make install
	@echo Done with all
