# PyCodeBox

[![Python Tests](https://github.com/zwallen/PyCodeBox/actions/workflows/python-tests.yml/badge.svg)](https://github.com/zwallen/PyCodeBox/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/zwallen/PyCodeBox/branch/master/graph/badge.svg)](https://codecov.io/gh/zwallen/PyCodeBox)


A personal collection of Python convenience functions for styling data displays and outputs, transforming and organizing data, performing statistical analyses, and other commonly performed actions in data science projects.

The package can be installed from PyPI:

```bash
pip install pycodebox
```

or GitHub:

```bash
pip install git+https://github.com/zwallen/PyCodeBox.git
```

And imported in your Python scripts as follows:

```python
from pycodebox import export_styled_xlsx_w_2_headers, fisher_exact_by_strata
```

## Important Disclaimer

As these are only personal convenience functions wrapping existing functions and packages:

* **Compatibility:** They may or may not work for your purposes as they were designed in response to specific workflows and analyses. They are not meant to be designed for general audience use.
* **Support:** Limited support is provided - use at your own risk and test thoroughly with your data.
* **Citation:** Citation of the package is not necessary if you decide to use any of the functions written here (but glad if they were able to help!).

## Issues and Contributing

This is primarily a personal package, but if you encounter bugs or have suggestions:
* Open an issue on GitHub for bug reports
* Pull requests are welcome for bug fixes
* For questions, contact: zachary.d.wallen@gmail.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

Version 0.1.1 (current)
* Updated package name to `pycodebox` to avoid conflicts with existing packages on PyPI
* Successful upload to PyPI, so package can now be installed via `pip install pycodebox`

Version 0.1.0
* Initial release
* Basic data styling, transformation, statistical analysis, and plotting functions

---
**Note:** This package represents a personal toolkit developed for specific analytical needs. While shared publicly, it prioritizes the author's workflows over general usability.
