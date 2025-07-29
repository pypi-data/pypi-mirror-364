from __future__ import annotations

import importlib.metadata

import matrix_count as m


def test_version():
    assert importlib.metadata.version("matrix_count") == m.__version__
