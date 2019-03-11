# Contributing

Contributions
------------------------------
Contributions are welcome! Open a [PR][2] with your changes (and tests to go along with them!). In this PR describe what your change does and link to any relevant issues.

Feature Requests
----------------------------------
Please open an [issue][1] describing the feature and its potential use cases.

Bug Reports
-----------------------
Please open an [issue][1] describing the bug.

Dev Setup
------------------------

Fork the repo and clone it so that you have a copy of the source code. Next, run the following commands in the terminal:

```
cd ParamTools
conda env create
conda activate paramtools-dev
pip install -e .
pre-commit install
```

Testing
-------------------
```
py.test -v
```


[1]: https://github.com/PSLmodels/ParamTools/issues
[2]: https://github.com/PSLmodels/ParamTools/pulls
