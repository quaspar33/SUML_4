# Instructions
## Virtual environment creation and preparation
### Windows
In order to create a virtual environment and install all packages associated with this project, run the following:  
py -3.13 -m venv .venv; .venv/Scripts/activate; pip install poetry>=2.2.1; poetry install

### Mac
If you're using Mac, use:  
python -3.13 -m venv .venv; source .venv/bin/activate; pip install poetry>=2.2.1; poetry install


If you already have a virtual environment set up, just run this:
poetry install