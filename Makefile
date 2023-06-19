.PHONY: build dist redist install install-from-source clean uninstall

build:
	CYTHONIZE=1 ./setup.py build

dist:
	CYTHONIZE=1 ./setup.py sdist bdist_wheel

redist: clean dist

install:
	CYTHONIZE=1 pip3 install .

install-from-source: dist
	pip3 install dist/statica-0.0.1.tar.gz

clean:
	$(RM) -r build dist src/*.egg-info
	$(RM) -r src/statica/file{encoder.c,decoder.c}
	$(RM) -r .pytest_cache
	find . -name __pycache__ -exec rm -r {} +

uninstall:
	pip uninstall statica