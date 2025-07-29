# matrix-count

[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]
[![codecov][codecov-badge]][codecov-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/maxjerdee/matrix-count/workflows/CI/badge.svg
[actions-link]:             https://github.com/maxjerdee/matrix-count/actions
[codecov-badge]:            https://codecov.io/github/maxjerdee/matrix-count/coverage.svg?token=1GSB7GLW7K
[codecov-link]:             https://codecov.io/github/maxjerdee/matrix-count
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[pypi-link]:                https://pypi.org/project/matrix-count/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/matrix-count
[pypi-version]:             https://img.shields.io/pypi/v/matrix-count
[rtd-badge]:                https://readthedocs.org/projects/matrix-count/badge/?version=stable
[rtd-link]:                 https://matrix-count.readthedocs.io/en/stable

<!-- prettier-ignore-end -->

### Estimating integer matrix counting problems

##### Maximilian Jerdee

We provide analytic estimates and sampling-based algorithms for a variety of
counting problems defined over integer matrices.

For example, we may count the number of non-negative symmetric integer matrices
with even diagonal entries and a given row sum. This is the number of
(multi-)graphs with a given degree sequence. We can also estimate the number of
such matrices under combinations of the further conditions:

- Binary matrices (only simple graphs).
- Fixed total sum of diagonal entries (number of self edges).
- Fixed sum of entries in blocks of matrix. (number of edges between prescribed
  groups) [Not yet implemented]

We also include methods for estimating the number of non-negative integer
matrices with a given row sum and column sum as described in
[Jerdee, Kirkley, Newman (2022)](https://arxiv.org/abs/2209.14869). [Not
yet implemented]

These problems can also be generalized as sums over matrices $A$ weighted by a
Dirichlet-multinomial factor on their entries

$$w(A) = \prod_{i < j}\binom{A_{ij} + \alpha - 1}{\alpha - 1} \prod_i \binom{A_{ii}/2 + \alpha - 1}{\alpha - 1}.$$

Note that $\alpha = 1$ corresponds to the uniform count. This more general
estimate acts as the partition function of a generalized random multigraph
model.

## Installation

`matrix-count` may be installed through pip:

```bash
pip install matrix-count
```

or be built locally by cloning this repository and running

```bash
pip install .
```

in the base directory.

## Typical usage

Once installed, the package can be imported as

```python
import matrix_count
```

Note that this is not `import matrix-count`.

The package can then be used to evaluate rapid analytic estimates of these
counting problems, to sample from the space of such matrices, and to converge to
the exact number of these matrices.

```python
# Margin of a 8x8 symmetric non-negative integer matrix with even diagonal entries
margin = [10, 9, 8, 7, 6, 5, 4, 3]

# Estimate the logarithm of the number of symmetric matrices with given margin sum
# (number of multigraphs with given degree sequence)
estimate = matrix_count.estimate_log_symmetric_matrices(margin, alpha=1)
print("Estimated log count of symmetric matrices:", estimate)

# Count the number of such matrices
count, count_err = matrix_count.count_log_symmetric_matrices(margin, alpha=1)
print("Log count of symmetric matrices:", count, "+/-", count_err)

# Sample from the space of such matrices
num_samples = 3
for _t in range(num_samples):
    sample, entropy = matrix_count.sample_symmetric_matrix(margin)
    print("Sampled matrix:")
    print(sample)
    print("Minus log probability of sampled matrix:", entropy)
```

Further usage examples can be found in the `examples` directory of the
repository and the [package documentation][rtd-link].
