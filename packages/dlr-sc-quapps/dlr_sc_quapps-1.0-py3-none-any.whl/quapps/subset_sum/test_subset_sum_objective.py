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

""" module for testing the SubsetSum Objective """

from quark import PolyBinary

from quapps.subset_sum.test_subset_sum_instance import get_example_instance


EXPECTED_OBJECTIVE_POLY = PolyBinary({(): 7569,
                                      (('x', 0, 7),): -1169,
                                      (('x', 1, 10),): -1640,
                                      (('x', 2, 13),): -2093,
                                      (('x', 3, 17),): -2669,
                                      (('x', 4, 20),): -3080,
                                      (('x', 5, 25),): -3725,
                                      (('x', 6, 31),): -4433,
                                      (('x', 7, 42),): -5544,
                                      (('x', 0, 7), ('x', 1, 10)): 140,
                                      (('x', 0, 7), ('x', 2, 13)): 182,
                                      (('x', 0, 7), ('x', 3, 17)): 238,
                                      (('x', 0, 7), ('x', 4, 20)): 280,
                                      (('x', 0, 7), ('x', 5, 25)): 350,
                                      (('x', 0, 7), ('x', 6, 31)): 434,
                                      (('x', 0, 7), ('x', 7, 42)): 588,
                                      (('x', 1, 10), ('x', 2, 13)): 260,
                                      (('x', 1, 10), ('x', 3, 17)): 340,
                                      (('x', 1, 10), ('x', 4, 20)): 400,
                                      (('x', 1, 10), ('x', 5, 25)): 500,
                                      (('x', 1, 10), ('x', 6, 31)): 620,
                                      (('x', 1, 10), ('x', 7, 42)): 840,
                                      (('x', 2, 13), ('x', 3, 17)): 442,
                                      (('x', 2, 13), ('x', 4, 20)): 520,
                                      (('x', 2, 13), ('x', 5, 25)): 650,
                                      (('x', 2, 13), ('x', 6, 31)): 806,
                                      (('x', 2, 13), ('x', 7, 42)): 1092,
                                      (('x', 3, 17), ('x', 4, 20)): 680,
                                      (('x', 3, 17), ('x', 5, 25)): 850,
                                      (('x', 3, 17), ('x', 6, 31)): 1054,
                                      (('x', 3, 17), ('x', 7, 42)): 1428,
                                      (('x', 4, 20), ('x', 5, 25)): 1000,
                                      (('x', 4, 20), ('x', 6, 31)): 1240,
                                      (('x', 4, 20), ('x', 7, 42)): 1680,
                                      (('x', 5, 25), ('x', 6, 31)): 1550,
                                      (('x', 5, 25), ('x', 7, 42)): 2100,
                                      (('x', 6, 31), ('x', 7, 42)): 2604})


def get_example_objective():
    """construct example objective"""
    ssp_instance = get_example_instance()
    return ssp_instance.get_objective()

def test_objective_creation():
    """test objective creation"""
    ssp_objective = get_example_objective()
    assert ssp_objective.polynomial == EXPECTED_OBJECTIVE_POLY
    assert ssp_objective.name is None
