![PyPI](https://img.shields.io/pypi/v/sweetbean)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/autoresearch/sweetbean/test-pytest.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/sweetbean)
![Link to docs](https://img.shields.io/badge/Docs-autoresearch.github.io/sweetbean-purple)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.07703/status.svg)](https://doi.org/10.21105/joss.07703)


# SweetBean

A declarative programming language built in Python, designed for the synthesis of behavioral experiments. It allows researchers to specify experiments once and seamlessly compile them into a [jsPsych](https://www.jspsych.org/) experiment for conducting studies with human participants or text-based simulations with synthetic participants using large-language models. 

## Features

- **Declarative language**: Specify experiments once and compile them into a jsPsych experiment for conducting studies with **human participants** or text-based simulations with **synthetic participants** using large-language models.
- **Python-based**: SweetBean is built in Python, making it accessible and easy to use for researchers and educators.

## Integrate with other packages

This package seamlessly integrates with other packages aimed at running online behavioral experiments:

- [AutoRA](https://autoresearch.github.io/autora/): For closed loop research, automatic experiment deployment, participant recruitment, and data collection.
- [SweetPea](http://sweetpea.ai/): For experimental design.

But it can also be used as a standalone product.

## Installation

The package is available on PyPI and can be installed via pip:

```bash
pip install sweetbean
```

## Compatibility

SweetBean is compatible with the following version of jsPsych:

- **jsPsych**: `7.x`  

### Dependencies

Sweetbean has the following dependencies that need to be installed on your system:

- **Python**: `>=3.9, <4.0`  
- **java**

Other versions may work but are not officially supported. If you experience issues, please report them!

### Python Dependencies
The following Python packages are required and will be installed automatically via `pip`:

- `jinja2`
- `transcrypt`
- `pyppeteer`
- `pillow`

### jsPsych Plugins
SweetBean **does not support all jsPsych plugins**, but new plugins are added regularly.  
If you need support for a specific jsPsych plugin, please open an issue **[here](https://github.com/AutoResearch/sweetbean/issues).**

## Documentation

You can find examples and documentation here: https://autoresearch.github.io/sweetbean/

## Issues

Please report any issues with this software or its documentation [here](https://github.com/AutoResearch/sweetbean/issues/new/choose).

## Contributing

We are open to contributions to SweetBean. More information can be found [here](https://autoresearch.github.io/sweetbean/CONTRIBUTING/).

## Collaborating

We are always interested in collaborating! If you like our work but need some tailoring for your specific use case, please contact [ystrittmatter@princeton.edu](mailto:ystrittmatter@princeton.edu).

## Citation

If you would like to reference SweetBean in a publication, you can use the following BibTeX entry referencing the associated [publication in the Journal of Open Source Software](https://joss.theoj.org/papers/10.21105/joss.07703):

```bibtex
@article{Strittmatter2025, doi = {10.21105/joss.07703},
author = {Younes Strittmatter and Sebastian Musslick},
title = {SweetBean: A declarative language for behavioral experiments with human and artificial participants},
url = {https://doi.org/10.21105/joss.07703}, 
year = {2025}, 
publisher = {The Open Journal}, 
volume = {10}, 
number = {107}, 
pages = {7703}, 
journal = {Journal of Open Source Software},
doi = {10.21105/joss.07703}
}
```

## About

This project is in active development by
the [Autonomous Empirical Research Group](https://musslick.github.io/AER_website/Research.html), Lead
Designer [Younes Strittmatter](https://younesstrittmatter.github.io/), led
by [Sebastian Musslick](https://smusslick.com).

This research program was supported by Schmidt Science Fellows, in partnership with the Rhodes Trust, as well as the
Carney BRAINSTORM program at Brown University.
