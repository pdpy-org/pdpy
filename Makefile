
# used in github actions - do not edit
local:
	make clean
	make build
	make install-local
	echo "Done with all"

# used in github actions - do not edit
doc:
	cd docs && make html

build:
	python -m build

activate:
	source ~/.pdpy/bin/activate

deploy:
	python -m twine upload --repository testpypi dist/*

install-local:
	python -m pip install ./dist/*.tar.gz

install:
	python -m pip install -i https://test.pypi.org/simple/ $(shell ./scripts/get_version.sh ./pyproject.toml ==)

clean:
	rm -rf ./build
	rm -rf ./dist

test:
	tox

version:
	python ./scripts/version.py 

all:
	make clean
	make version
	make build
	make deploy
	echo "waiting 10 seconds for pypi to update"
	sleep 10
	make install
	echo "Done with all"

