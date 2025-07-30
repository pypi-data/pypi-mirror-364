# CLFits: Command-Line FITS Header Editor

[![PyPI Version](https://img.shields.io/pypi/v/clfits.svg)](https://pypi.org/project/clfits)
[![CI Status](https://github.com/AmberLee2427/CLFits/actions/workflows/ci.yml/badge.svg)](https://github.com/AmberLee2427/CLFits/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/AmberLee2427/CLFits/graph/badge.svg?token=C9FTGOCJ4M)](https://codecov.io/github/AmberLee2427/CLFits)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, robust command-line tool for viewing and editing FITS file headers.

## 🚀 Installation

Install `CLFits` directly from PyPI:

```bash
pip install clfits
```

## ✨ Quick Start

`CLFits` provides a straightforward, command-based interface for header manipulation.

**View the entire header:**

```bash
clfits view my_image.fits
```

**Get the value of a specific keyword:**

```bash
clfits get my_image.fits OBJECT
```

**Set a keyword's value and comment:**

```bash
clfits set my_image.fits OBJECT "NGC 4993" --comment "Corrected object name"
```

**Delete a keyword:**

```bash
clfits del my_image.fits HISTORY
```

**Export the header to JSON:**

```bash
clfits export my_image.fits --format json
```

**Export the header to a YAML file (format is inferred from filename):**

```bash
clfits export my_image.fits --output header.yml
```

For more detailed instructions, see the [full documentation](https://clfits.readthedocs.io/). 