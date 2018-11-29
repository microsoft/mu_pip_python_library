# Developing Project Mu Pip Python Library

## Pre-Requisites

1. Get the code

``` cmd
git clone https://github.com/Microsoft/mu_pip_python_library.git
```

2. Install development dependencies

``` cmd
pip install --upgrade -r requirements.txt
```

3. Uninstall any copy of mu_python_library

``` cmd
pip uninstall mu_python_library
```

4. Install from local source (run command from root of repo)

``` cmd
pip install -e .
```

## Testing

1. Run a Basic Syntax/Lint Check (using flake8) and resolve any issues

``` cmd
flake8 MuPythonLibrary
```

!!! info
    Newer editors are very helpful in resolving source formatting errors (whitespace, indentation, etc). 
    In VSCode open the py file and use ++alt+shift+f++ to auto format.  

2. Run pytest with coverage data collected

``` cmd
pytest -v --junitxml=test.junit.xml --html=pytest_MuPythonLibrary_report.html --self-contained-html --cov=MuPythonLibrary --cov-report html:cov_html --cov-report xml:cov.xml --cov-config .coveragerc
```

3. Look at the reports

* pytest_MuPythonLibrary_report.html
* cov_html/index.html
