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

""" module for testing the Ising Objective """

import numpy as np

from quark import PolyIsing

from quapps.arbitrary_ising import IsingInstance


LOCAL_FIELDS = np.array([1, 2, 3])
COUPLINGS = 0.5 * np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]])
EXPECTED_ISING_POLY = PolyIsing({(): 0.0,
                                 (0,): 1.0,
                                 (1,): 2.0,
                                 (2,): 3.0,
                                 (0, 1): 1.0,
                                 (0, 2): 2.0,
                                 (1, 2): 3.0})

def get_example_objective():
    """ construct example objective """
    ising_instance = IsingInstance(LOCAL_FIELDS, COUPLINGS)
    return ising_instance.get_objective()


def test_objective_creation():
    """ test objective creation """
    ising_objective = get_example_objective()
    assert ising_objective.polynomial == EXPECTED_ISING_POLY
    assert ising_objective.name is None
