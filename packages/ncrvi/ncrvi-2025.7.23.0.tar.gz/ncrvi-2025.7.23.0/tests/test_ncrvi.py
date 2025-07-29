#!/usr/bin/env --split-string=python -m pytest --verbose

"""Implement the tests"""

import pytest
import random
import time
import os

@pytest.fixture
def total_comonents() -> int:

    time.sleep(float(os.environ['poffw']))
    print('Power off')
    time.sleep(float(os.environ['ponw']))
    print('Power on')
    time.sleep(float(os.environ['settle']))
    print('Work')
    time.sleep(float(os.environ['poffw']))
    print('Power off')

    yield random.choice(range(int(os.environ['expected'])))

class TestCase_Ncrvi_01:

    @pytest.mark.parametrize('how_often', range(int(os.environ['how_often'])))
    def test_it(self, total_comonents, how_often):

        assert total_comonents == int(os.environ['expected']) - 1
