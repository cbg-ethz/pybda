# Copyright (C) 2018 Simon Dirmeier
#
# This file is part of koios.
#
# koios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# koios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with koios. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import os
import unittest


class TestConfig(unittest.TestCase):
    """
    Tests the control parsing module.

    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._file = os.path.join(
          os.path.dirname(__file__), "..", "data", "config.yml")
        self._c = Config(self._file)

    def test_plate_id_file(self):
        assert self._c.plate_id_file == "experiment_meta_file.tsv"

    def test_layout_file(self):
        assert self._c.layout_file == "layout.tsv"

    def test_plate_folder(self):
        assert self._c.plate_folder == "./"

    def test_output_path(self):
        assert self._c.output_path == "./out/"

    def test_plate_regex(self):
        assert self._c.plate_regex == ".*\/\w+\-\w[P|U]\-[G|K]\d+(-\w+)*\/.*"
