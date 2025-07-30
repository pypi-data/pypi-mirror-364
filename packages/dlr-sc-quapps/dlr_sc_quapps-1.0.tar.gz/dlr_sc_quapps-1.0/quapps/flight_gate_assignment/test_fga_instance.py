# Copyright 2022 DLR-SC
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
import numpy as np

from quapps.flight_gate_assignment import FGAInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"


def get_example_instance_data():
    """ get full data set for example instance """
    return {"flights": [1, 2, 3],
            "gates": [1, 2],
            "time_buffer": 10,
            "time_arrival": {1: 2, 2: 2.5},
            "time_departure": {1: 3, 2: 2},
            "time_transfer": {(1, 2): 7, (2, 1): 9, (1, 1): 5, (2, 2): 5},
            "time_in": {1: 0, 2: 20, 3: 35},
            "time_out": {1: 16, 2: 30, 3: 50},
            "passengers_in": {1: 50, 3: 100},
            "passengers_out": {1: 10, 2: 25, 3: 65},
            "passengers_transfer": {(1, 1): 10, (1, 3): 20, (2, 1): 20, (2, 2): 10, (3, 1): 20, (3, 3): 10}}

def get_example_instance():
    """ construct example instance """
    return FGAInstance(**get_example_instance_data())


def test_forbidden_pairs():
    """ test calculation of the forbidden pairs """
    fga_instance = get_example_instance()
    expected_forbidden_pairs = [(1, 2), (2, 3)]
    assert fga_instance.forbidden_pairs == expected_forbidden_pairs

def test_consistency():
    """ test consistency of instance data """
    error1 = "There are {} values for flights that do not exist"
    error2 = "There are {} values for flight combinations that do not exist"
    faulty_data = [("passengers_in", {4: 30}, error1),
                   ("passengers_out", {4: 30}, error1),
                   ("passengers_transfer", {(1, 4): 30}, error2),
                   ("time_in", {5: 30}, error2),
                   ("time_out", {5: 30}, error2)]

    for name, data, error in faulty_data:
        with pytest.raises(ValueError, match=error.format(name)):
            data_dict = get_example_instance_data()
            data_dict.update({name : data})
            FGAInstance(**data_dict)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "FGAInstance_flights_003_gates_002"

def test_io():
    """ test read and write of instance """
    fga_instance = get_example_instance()
    fga_instance.save_hdf5(FILENAME_TMP)
    loaded = FGAInstance.load_hdf5(FILENAME_TMP)

    for attr in get_example_instance_data():
        assert np.array_equal(getattr(loaded, attr), getattr(fga_instance, attr))
    assert loaded.forbidden_pairs == fga_instance.forbidden_pairs

    os.remove(FILENAME_TMP)
