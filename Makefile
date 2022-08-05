
build:
	python3 -m build

activate:
	source ~/.pdpy/bin/activate

deploy:
	python3 -m twine upload --repository testpypi dist/*

install:
	make activate && python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps pdpy-0.0.2

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