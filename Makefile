format:
	yapf -ir .

lint:
	pylama --skip llvm_lang/parsetab.py .


.PHONY: format lint
