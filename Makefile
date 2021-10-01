SHELL = /bin/bash

.PHONY: generate-acknowledgements
generate-acknowledgements:
	echo -e "# Open Source Acknowledgements\n\nSpice.ai would like to acknowledge the following open source projects for making this project possible:\n\nPython Packages\n" > ACKNOWLEDGEMENTS.md
	python -m venv venv-acknowledgments
	source venv-acknowledgments/bin/activate
	venv-acknowledgments/bin/pip install -r gardener/requirements.txt
	venv-acknowledgments/bin/pip install pip-licenses
	venv-acknowledgments/bin/pip-licenses -f csv --with-authors --with-urls 2>/dev/null >> ACKNOWLEDGEMENTS.md
	rm -rf venv-acknowledgments

	sed -i 's/\"//g' ACKNOWLEDGEMENTS.md
	sed -i 's/,/, /g' ACKNOWLEDGEMENTS.md
	sed -i 's/,  /, /g' ACKNOWLEDGEMENTS.md