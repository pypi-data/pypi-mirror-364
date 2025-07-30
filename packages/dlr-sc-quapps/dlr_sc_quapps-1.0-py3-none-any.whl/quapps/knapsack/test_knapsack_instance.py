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

""" module for testing the Knapsack Instance """

import os
import pytest

from quapps.knapsack import KnapsackInstance

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"


def get_example_instance():
    """ construct example instance """
    items = {"A": (3, 1), "B": (4, 1), "C": (5, 9), "D": (2, 6), "E": (5, 3), "F": (5, 5)}
    capacity = 11
    return KnapsackInstance(items, capacity)


def test_init():
    """ test initialization of instance """
    kns_instance = get_example_instance()
    assert kns_instance.items == {"A": (3, 1), "B": (4, 1), "C": (5, 9), "D": (2, 6), "E": (5, 3), "F": (5, 5)}
    assert kns_instance.capacity == 11

def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="No items given"):
        KnapsackInstance({}, 3)
    with pytest.raises(ValueError, match="Capacity is not a positive integer"):
        KnapsackInstance( {"A": (1, 2), "B": (2, 3)}, 3.5)
    with pytest.raises(TypeError, match="At least one value is not a float or integer"):
        KnapsackInstance({"A": (1.1, 2), "B": ("b", 3)}, 6)
    with pytest.raises(TypeError, match="At least one weight is not an integer"):
        KnapsackInstance({"A": (1.1, 2), "B": (2, 3.3)}, 5)
    with pytest.raises(ValueError, match="Capacity is not a positive integer"):
        KnapsackInstance({"A": (1, 2), "B": (2, 3)}, -3)
    with pytest.raises(ValueError, match="An item is missing a value or a weight"):
        KnapsackInstance({"A": (1,), "B": ()}, 5)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "KnapsackInstance_items_006_capacity_011_max_value_005_max_weight_009"

def test_io():
    """ test read and write of instance """
    knapsack_instance = get_example_instance()
    knapsack_instance.save_hdf5(FILENAME_TMP)
    loaded = KnapsackInstance.load_hdf5(FILENAME_TMP)

    assert loaded.items == knapsack_instance.items
    assert loaded.capacity == knapsack_instance.capacity

    os.remove(FILENAME_TMP)

def test_get_random():
    """ test generation of random knapsack instance """
    random_knapsack_instance = KnapsackInstance.get_random(15, 60, 14, 15)

    assert len(random_knapsack_instance.items) == 15
    assert random_knapsack_instance.capacity <= 16

    for name, (value, weight) in random_knapsack_instance.items.items():
        assert value <= 60
        assert weight <= 14
        assert name < 15    # items in this instance are numbered from 0 to 14
