format:
	yapf -ir .

lint:
	pylama --skip llvm_lang/parsetab.py .

test:
	pytest


.PHONY: format lint test
