#!/usr/bin/env --split-string=python -m pytest --verbose

"""Implement the tests"""

import pytest
import random
import time
import os
import textwrap

class TestCase_Ncrvi:

    POWER_ON_WAIT = float(os.environ['POWER_ON_WAIT'])
    INITIAL_WAIT = float(os.environ['INITIAL_WAIT'])
    POWER_OFF_WAIT = float(os.environ['POWER_OFF_WAIT'])
    SETTLING_DELAY = float(os.environ['SETTLING_DELAY'])
    EXPECTED_COMPONENTS = int(os.environ['EXPECTED_COMPONENTS'])
    HOW_OFTEN = int(os.environ['HOW_OFTEN'])

    class NumberOfComponentsError(ArithmeticError): pass

    def test_initial_wait(self):

        try:
            assert self.INITIAL_WAIT
            print('Power on')
            time.sleep(self.INITIAL_WAIT)
        except AssertionError:
            pytest.skip('Not requested')

    @pytest.fixture
    def total_components(self) -> int:

        time.sleep(self.POWER_OFF_WAIT)
        print('Power off')
        time.sleep(self.POWER_ON_WAIT)
        print('Power on')
        time.sleep(self.SETTLING_DELAY)
        print('Work')
        time.sleep(self.POWER_OFF_WAIT)
        print('Power off')

        yield random.choice(range(self.EXPECTED_COMPONENTS))

    @pytest.mark.parametrize('how_often', range(HOW_OFTEN))
    def test_it(self, total_components, how_often):

        try:
            assert total_components == self.EXPECTED_COMPONENTS - 1
        except AssertionError as exc:
            raise self.NumberOfComponentsError(textwrap.dedent(f'''
                missing components: only {total_components!r} out of {(self.EXPECTED_COMPONENTS - 1)!r}
            ''').strip()) from exc
