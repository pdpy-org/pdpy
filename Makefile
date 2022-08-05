
build:
	python3 -m build

deploy:
	python3 -m twine upload --repository testpypi dist/*

install:
	source ~/.pdpy/bin/activate && python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps pdpy-0.0.1

play:
	source ~/.pdpy/bin/activate && python3

clean:
	rm -rf ./build
	rm -rf ./dist

test:
	tox
