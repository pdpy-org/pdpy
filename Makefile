
build:
	python -m build

activate:
	source ~/.pdpy/bin/activate

deploy:
	python -m twine upload --repository testpypi dist/*

local:
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

doc:
	cd docs && make html && open build/html/index.html

all-local:
	make clean
	make build
	make local
	make doc
	echo "Done with all"
