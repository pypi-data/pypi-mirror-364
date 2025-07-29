# pysfsymbols

[![PyPI - Version](https://img.shields.io/pypi/v/pysfsymbols.svg)](https://pypi.org/project/pysfsymbols)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysfsymbols.svg)](https://pypi.org/project/pysfsymbols)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

You can install the library using pip:
```bash
pip install pysfsymbols
```

## Usage[^1]

This library was designed to be used in combination with Qt for Python, specifically tested with PySide6.

Due to how the *Unicode Private Use Area (PUA)* works, this library can only work if the application is set to use an Apple San Francisco Font, e.g.:

```python
app = QApplication()

font_id = QFontDatabase.addApplicationFont(":/resources/fonts/sf_pro_rounded/SF-Pro-Rounded-Regular.otf"),
font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

font = QFont(font_family, 12, QFont.Weight.Normal)

app.setFont(font)
app.exec()
```

To use an SF Symbol within a QPushButton:

```python
import pysfsymbols

button = QPushButton(sf_symbols.fetch_symbol('symbol.name'))
```

[^1]: sorry this documentation isn't very useful rn, if you have any issues email me at thom-cummings@outlook.com and i can possibly help better.

## License

`pysfsymbols` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
