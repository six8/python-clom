#!/usr/bin/env python
import pytest
import sys
from os import path

test_dir = path.dirname(path.abspath(__file__))

sys.path.insert(0, path.dirname(test_dir))

if __name__ == '__main__':
    raise SystemExit(pytest.main())
