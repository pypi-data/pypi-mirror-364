# jupyterlab-stan-highlight

JupyterLab extension to highlight Stan syntax in notebooks and standalone Stan files.

This extension has been updated to work with **JupyterLab 4.0+** and uses CodeMirror 6 for syntax highlighting.

Modeled on the [VSCode grammar](https://github.com/ivan-bocharov/stan-vscode) and uses 
[stan-language-definitions](https://github.com/jrnold/stan-language-definitions)

Use it with [CmdStanJupyter](https://github.com/WardBrian/CmdStanJupyter) to receive
highlighting for your `%%stan` blocks in python notebooks!

## Features

- Syntax highlighting for `.stan` files
- Automatic highlighting for `%%stan` magic cells in Jupyter notebooks
- Support for Stan language constructs including:
  - Data types (int, real, vector, matrix, etc.)
  - Control flow (for, while, if, else)
  - Distributions and functions
  - Comments and preprocessor directives

## Prerequisites

* JupyterLab 4.0 or later

## Installation

### From PyPI (Recommended)

```bash
pip install jupyterlab-stan-highlight
```

### Development Installation

For a development install, clone this repository and run:

```bash
pip install -e .
# Or if you prefer to use conda/mamba
# conda install -c conda-forge jupyterlab nodejs
# mamba install -c conda-forge jupyterlab nodejs

# Install dependencies
jlpm install

# Build the extension
jlpm run build

# Install the extension for development
jupyter labextension develop . --overwrite
```

## Usage

1. **Stan Files**: Open any `.stan` file in JupyterLab and syntax highlighting will be applied automatically.

2. **Notebook Magic Cells**: In a Jupyter notebook, create a code cell that starts with `%%stan` and the rest of the cell content will be highlighted as Stan code:

```python
%%stan
data {
  int<lower=0> N;
  vector[N] y;
}
parameters {
  real mu;
  real<lower=0> sigma;
}
model {
  y ~ normal(mu, sigma);
}
```

## Building

To build the extension:

```bash
jlpm run build
```

To build for production:

```bash
jlpm run build:prod
```

## Changes from Previous Version

This version (0.4.0+) includes major updates for JupyterLab 4 compatibility:

- Migrated from CodeMirror 5 to CodeMirror 6
- Updated to use JupyterLab 4 APIs
- Modernized build system using `@jupyterlab/builder`
- Added TypeScript support
- Improved magic cell detection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
