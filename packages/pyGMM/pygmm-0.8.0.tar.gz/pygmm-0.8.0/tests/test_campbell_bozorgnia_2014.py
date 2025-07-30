#!/usr/bin/env python
"""Test calculation of CB14 static methods."""

from numpy.testing import assert_allclose

from pygmm import CampbellBozorgnia2014 as CB14


def test_depth_2_5():
    # Value calculated from NGAW2 spreadsheet
    assert_allclose(CB14.calc_depth_2_5(600, "japan", None), 0.1844427)
    assert_allclose(CB14.calc_depth_2_5(600, "california", None), 0.7952589)
