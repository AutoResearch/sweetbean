# User Guide

This guide provides an overview over SweetBean.

## Features

- **Declarative Specification**: SweetBean is a domain-specific programming language in Python built for the declarative
  specification of stimuli sequences that can be synthesized into JavaScript or HTML files ready to be served as online
  or run with Large Language Models or Vision Models as synthetic participants.
- SweetBean experiments can be exported to multiple formats:
    - **HTML**: SweetBean can export experiments to HTML files that can be served as online experiments.
    - **JavaScript**: SweetBean can export experiments to JavaScript files that can be run in the browser.
    - **AutoRA**: SweetBean can be used to run automated Experiments with [AutoRA](https://autoresearch.github.io/autora/).
    - **LLM**: SweetBean can be used to run experiments with Large Language Models.
    - **Stimulus Sequence**: SweetBean can automatically generate an image of the stimulus sequence often used to document
      the experiment in papers.
    - Coming soon: **Vision Models**: SweetBean will be able to run experiments with Vision Models.

## Installation

To install and use SweetBean you need:

- `Python` (version ">=3.8,<4") and
- the `sweetbean` package, including required dependencies specified in the [`pyproject.toml` file](https://github.com/AutoResearch/sweetbean/blob/main/pyproject.toml).

### Step 1: Install `python`

You can install `python`:

- Using the instructions at [python.org](https://www.python.org), or
- Using a package manager, e.g.
  [homebrew](https://docs.brew.sh/Homebrew-and-Python), 
  [pyenv](https://github.com/pyenv/pyenv),
  [asdf](https://github.com/asdf-community/asdf-python), 
  [rtx](https://github.com/jdxcode/rtx/blob/main/docs/python.md),
  [winget](https://winstall.app/apps/Python.Python.3.8).

If successful, you should be able to run python in your terminal emulator like this:
```shell
python
```

...and see some output like this:
```
Python 3.11.3 (main, Apr  7 2023, 20:13:31) [Clang 14.0.0 (clang-1400.0.29.202)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
```

### Step 2: Install `sweetbean`

!!! success
    We recommend setting up your development environment using a manager like `venv`, which creates isolated python 
    environments. Other environment managers, like 
    [virtualenv](https://virtualenv.pypa.io/en/latest/),
    [pipenv](https://pipenv.pypa.io/en/latest/),
    [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/), 
    [hatch](https://hatch.pypa.io/latest/), 
    [poetry](https://python-poetry.org), 
    are available and will likely work, but will have different syntax to the syntax shown here.

In the `<project directory>`, run the following command to create a new virtual environment in the `.venv` directory

```shell
python3 -m "venv" ".venv" 
```

!!! hint
    If you have multiple Python versions installed on your system, it may be necessary to specify the Python version when creating a virtual environment. For example, run the following command to specify Python 3.8 for the virtual environment. 
    ```shell
    python3.8 -m "venv" ".venv" 
    ```

Activate it by running
```shell
source ".venv/bin/activate"
```

```shell
pip install "autora"
```

Check your installation by running:
```shell
python -c "from sweetbean.variable import TimelineVariable"
```

You can now start using SweetBean!
