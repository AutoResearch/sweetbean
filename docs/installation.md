# Installation & Compatibility

## Installation

The package is available on PyPI and can be installed via pip:

```bash
pip install sweetbean
```

For HTML→PNG export (`Block.to_image`), also install the **image** extra (adds pyppeteer and Pillow):

```bash
pip install "sweetbean[image]"
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
- `pydantic`

**Optional:** `pyppeteer` and `pillow` (install `sweetbean[image]`) are required only for `Block.to_image()` and related rasterization helpers.

### jsPsych Plugins

SweetBean **does not support all jsPsych plugins**, but new plugins are added regularly.  
If you need support for a specific jsPsych plugin, please open an issue **[here](https://github.com/AutoResearch/sweetbean/issues).**
