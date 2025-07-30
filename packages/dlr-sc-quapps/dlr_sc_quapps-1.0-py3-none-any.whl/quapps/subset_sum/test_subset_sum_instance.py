# Copyright 2024 DLR-SC
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

""" module for testing the SubsetSum Instance """

import os
import pytest

from quapps.subset_sum import SubsetSumInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"

NUMBERS = [7, 10, 13, 17, 20, 25, 31, 42]
TARGET_SUM = 87

def get_example_instance():
    """ construct example instance """
    return SubsetSumInstance(NUMBERS, TARGET_SUM)


def test_init():
    """ test initialization of instance """
    ssp_instance = get_example_instance()
    assert ssp_instance.numbers == NUMBERS
    assert ssp_instance.target_sum == TARGET_SUM

def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="No numbers given"):
        SubsetSumInstance([], 3)
    with pytest.warns(UserWarning, match="Only the keys of the dictionary will be used"):
        SubsetSumInstance({0: 0, 1:1, 2:2}, 3)
    with pytest.raises(TypeError, match="numbers is not a collection of integers"):
        SubsetSumInstance([1, 2, 3.5], 3)
    with pytest.raises(TypeError, match="target_sum is not an integer"):
        SubsetSumInstance([1, 2, 3], 1.5)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "SubsetSumInstance_numbers_8_min_7_max_42_target_sum_87"

def test_io():
    """ test read and write of instance """
    ssp_instance = get_example_instance()
    ssp_instance.save_hdf5(FILENAME_TMP)
    loaded = SubsetSumInstance.load_hdf5(FILENAME_TMP)

    assert loaded.numbers == ssp_instance.numbers
    assert loaded.target_sum == ssp_instance.target_sum

    os.remove(FILENAME_TMP)

def test_get_random():
    """ test generation of random SubsetSum instance """
    random_ssp_instance = SubsetSumInstance.get_random(15, 50, 160)
    assert len(random_ssp_instance.numbers) == 15
    assert 0 <= random_ssp_instance.target_sum <= 160
    for number in random_ssp_instance.numbers:
        assert 0 <= number <= 50
