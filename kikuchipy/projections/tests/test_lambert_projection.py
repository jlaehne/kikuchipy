# -*- coding: utf-8 -*-
# Copyright 2019-2021 The kikuchipy developers
#
# This file is part of kikuchipy.
#
# kikuchipy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kikuchipy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kikuchipy. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from orix.vector import Vector3d
import pytest

from kikuchipy.projections.lambert_projection import (
    LambertProjection,
    _eq_c,
    _vector2xy,
)


class TestLambertProjection:
    def test_vector2xy_vector(self):
        """Works for Vector3d objects with single and multiple vectors"""

        vector_one = Vector3d((0.578, 0.578, 0.578))
        output_a = LambertProjection.vector2xy(vector_one)
        expected_a = np.array((0.81417, 0.81417))

        assert np.allclose(output_a[..., 0, 0], expected_a[0], atol=1e-3)
        assert np.allclose(output_a[..., 0, 1], expected_a[1], atol=1e-3)

        vector_two = Vector3d(
            [[0.578, 0.578, 0.578], [0, 0.707, 0.707], [0.707, 0, 0.707]]
        )
        output_b = LambertProjection.vector2xy(vector_two)

        expected_x = np.array((0.81417, 0, 0.678))
        expected_y = np.array((0.81417, 0.678, 0))

        assert np.allclose(output_b[..., 0, 0], expected_x[0], atol=1e-3)
        assert np.allclose(output_b[..., 0, 1], expected_y[0], atol=1e-3)
        assert np.allclose(output_b[..., 1, 0], expected_x[1], atol=1e-3)
        assert np.allclose(output_b[..., 1, 1], expected_y[1], atol=1e-3)
        assert np.allclose(output_b[..., 2, 0], expected_x[2], atol=1e-3)
        assert np.allclose(output_b[..., 2, 1], expected_y[2], atol=1e-3)

    def test_vector2xy_array(self):
        """Works for numpy arrays."""
        output = LambertProjection.vector2xy(np.array([0.578, 0.578, 0.578]))
        assert np.allclose(output, 0.81480, atol=1e-5)

        xyz = np.array(
            [
                [0, 0, 1],
                [0, 1, 0],
                [2, 0, 0],
                [0, 0, -3],
                [0, 0, -1],
                [0, -1, 0],
                [-2, 0, 0],
                [0, 0, 3],
            ]
        )
        lambert_xy = [
            [0, 0],
            [0, np.sqrt(np.pi / 2)],
            [np.sqrt(np.pi / 2), 0],
            [0, 0],
            [0, 0],
            [0, -np.sqrt(np.pi / 2)],
            [-np.sqrt(np.pi / 2), 0],
            [0, 0],
        ]
        assert np.allclose(LambertProjection.vector2xy(xyz), lambert_xy)
        assert np.allclose(_vector2xy.py_func(xyz), lambert_xy)

    def test_xy2vector(self):
        """Conversion from Lambert to Cartesian coordinates works"""
        lambert_xy = np.array([0.81480, 0.81480])
        v = LambertProjection.xy2vector(lambert_xy)
        assert np.allclose(v.data, 0.578, atol=1e-3)

    def test_eq_c(self):
        """Helper function works"""
        arr_1 = np.array((0.578, 0.578, 0.578))
        value = arr_1[..., 0]
        output_arr = np.array((0.61655, 0.61655, 0.61655))
        expected = output_arr[..., 0]
        output = _eq_c.py_func(value)
        assert output == pytest.approx(expected, rel=1e-5)

    def test_lambert_to_gnomonic(self):
        """Conversion from Lambert to Gnomonic works"""
        vec = np.array((0.81417, 0.81417))  # Should give x,y,z = 1/sqrt(3) (1, 1, 1)
        output = LambertProjection.lambert_to_gnomonic(vec)
        expected = np.array((1, 1))
        assert output[..., 0, 0] == pytest.approx(expected[0], abs=1e-2)

    def test_gnomonic_to_lambert(self):
        """Conversion from Gnomonic to Lambert works"""
        vec = np.array((1, 1))  # Similar to the case above
        output = LambertProjection.gnomonic_to_lambert(vec)
        expected = np.array((0.81417, 0.81417))
        assert output[..., 0, 0] == pytest.approx(expected[0], rel=1e-3)

    def test_shape_respect(self):
        """Check that LambertProjection.project() respects navigation axes"""
        sx = 60
        a = np.arange(1, sx ** 2 + 1).reshape((sx, sx))
        v = Vector3d(np.dstack([a, a, a]))
        assert v.shape == (sx, sx)
        assert v.data.shape == (sx, sx, 3)
        # Forward
        xy_lambert = LambertProjection.vector2xy(v)
        assert xy_lambert.shape == (sx, sx, 2)
        # and back
        xyz_frm_lambert = LambertProjection.xy2vector(xy_lambert)
        assert xyz_frm_lambert.shape == v.shape
        assert xyz_frm_lambert.data.shape == v.data.shape
