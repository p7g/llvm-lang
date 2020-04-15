format:
	yapf -ir .

lint:
	pylama --skip llvm_lang/parsetab.py .
	mypy --package llvm_lang

test:
	pytest


.PHONY: format lint test
