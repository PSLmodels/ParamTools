# Contributing

Contributions
------------------------------
Contributions are welcome! Open a PR with your changes (and tests to go along with them!). In this PR describe what your change does and link to any relevant issues.

Feature Requests
----------------------------------
Please open an [issue][1] describing the feature and its potential use cases.

Bug Reports
-----------------------
Please open an [issue][1] describing the bug.

Dev Setup
------------------------
In terminal:

```
cd ParamTools
conda create -n paramtools-dev numpy
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

Testing
-------------------
```
py.test
```


[1]: https://github.com/PSLmodels/ParamTools/issues
