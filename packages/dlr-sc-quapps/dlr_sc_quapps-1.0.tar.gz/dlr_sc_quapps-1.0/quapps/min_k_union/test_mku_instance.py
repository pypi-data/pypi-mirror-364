# Copyright 2023 DLR-SC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" module for testing the FlightGateAssignment Instance """

import os
import pytest

from quapps.min_k_union import MKUInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"


def get_example_instance():
    """ construct example instance """
    return MKUInstance(subsets=[{1}, {2}, {3}, {4}, {1, 2}, {2, 4}, {1, 2, 4}, {2, 3, 4}], k=3)


def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="There are not enough subsets"):
        MKUInstance([{1, 2, 4}, {2, 3, 4}], k = 3)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    exp_name = "MKUInstance_subsets_008_elements_004_k_003_max_subset_size_003"
    assert instance.get_name() == exp_name

def test_get_random():
    """ test random generator"""
    elements = 20
    # Should always succeed to cover 20 elements since it generates 20 subsets with sizes at least 1
    random_instance = MKUInstance.get_random(elements, 20, 10, 8, 10)
    assert len(random_instance.subsets) == 20
    assert all(len(subset) >= 1 for subset in random_instance.subsets)
    assert all(len(subset) <= 8 for subset in random_instance.subsets)

    covered_elements = set().union(*random_instance.subsets)
    assert len(covered_elements) == 20

    with pytest.raises(ValueError, match="Cannot generate desired subsets"):
        # Should always fail to generate since num_subsets * biggest_subset_size < len(elements)
        MKUInstance.get_random(elements, 6, 5, 3, 10)

def test_io():
    """ test read and write of instance """
    mku_instance = get_example_instance()
    mku_instance.save_hdf5(FILENAME_TMP)
    loaded = MKUInstance.load_hdf5(FILENAME_TMP)

    assert loaded.subsets == mku_instance.subsets
    assert loaded.k == mku_instance.k

    os.remove(FILENAME_TMP)
