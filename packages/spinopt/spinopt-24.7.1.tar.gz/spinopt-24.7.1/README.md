# SpiNopt: a Scipy optimization interface to NLOPT

For optimization, everyone starts out with the [Scipy optimization library](https://docs.scipy.org/doc/scipy/tutorial/optimize.html), but, at some point, you might want to try something else.
[NLOPT](https://nlopt.readthedocs.io/en/latest/) is a great library, but can be quite a hassle rewrite your code to use it.

This package provides a Scipy interface to the NLOPT optimization library. It's aim is not to provide a complete ecosystem which different solvers are available, but merely a way to quickly connect the NLOPT solvers, once you already have something set up with Scipy, or are familiar with how to set something up with Scipy.

## Basic example

```python
import numpy as np
from spinopt import NLOptimizer

dim = 3

# Define objective in this way
def my_easy_func(x, grad):
    if grad.size > 0:
        grad[:] = 2 * (x - np.arange(len(x)))
    x = x - np.arange(len(x))
    return x.dot(x)

# Define constraints Scipy style
A = np.ones((1, dim))
b = np.ones((1, 1))
constraints = [{"type": "eq", "jac": lambda w: A, "fun": lambda w: A.dot(w) - b.squeeze()}]

# Initialize optimizer
x0=np.zeros(dim)
opt = NLOptimizer(my_easy_func, x0, constraints=constraints)

# Optimize
res = opt.minimize()
assert res.success
assert np.allclose(res.x, np.arange(dim), atol=1e-5)
```

## Installation

To install from PyPI:

```bash
pip install spinopt
```

To install the latest development version from github:

```bash
pip install git+https://github.com/mvds314/spinopt.git
```

## Development

For development purposes, clone the repo:

```bash
git clone https://github.com/mvds314/spinopt.git
```

Then navigate to the folder containing `setup.py` and run

```bash
pip install -e .
```

to install the package in edit mode.

Run unittests with `pytest`.

## Related software

- [Scipy optimize](https://docs.scipy.org/doc/scipy/tutorial/optimize.html)
- [NLOPT](https://nlopt.readthedocs.io/en/latest/)
