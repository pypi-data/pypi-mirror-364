#!/usr/bin/env --split-string=python -m pytest --verbose

"""Implement the tests"""

import pytest

class TestCase_Ncrvi_01:

    def test_it(self):

        try:
            assert True is not False
        except AssertionError as exc:
            raise RuntimeError('You are in trouble...')
