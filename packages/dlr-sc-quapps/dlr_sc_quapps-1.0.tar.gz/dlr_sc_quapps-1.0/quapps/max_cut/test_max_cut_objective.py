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

""" module for testing the MaxCut Objective """

from quark import PolyIsing

from quapps.max_cut import MaxCutObjective
from quapps.max_cut.test_max_cut_instance import get_example_max_cut_instance, get_example_weighted_max_cut_instance


EXPECTED_OBJECTIVE_POLY = PolyIsing({(): -3.0,
                                     ("a", "b"): 0.5,
                                     ("a", "e"): 0.5,
                                     ("b", "c"): 0.5,
                                     ("b", "e"): 0.5,
                                     ("c", "d"): 0.5,
                                     ("d", "e"): 0.5})

EXPECTED_OBJECTIVE_POLY_WEIGHTED = PolyIsing({(): -4.5,
                                              ("a", "b"): 0.25,
                                              ("a", "e"): 1.5,
                                              ("b", "c"): 0.5,
                                              ("b", "e"): 0.5,
                                              ("c", "d"): 1.0,
                                              ("d", "e"): 0.75})

def test_objective_init():
    """ test objective initialization """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_objective = max_cut_instance.get_objective()
    assert max_cut_objective.polynomial == EXPECTED_OBJECTIVE_POLY

def test_objective_init_weighted():
    """ test objective initialization """
    max_cut_instance = get_example_weighted_max_cut_instance()
    max_cut_objective = max_cut_instance.get_objective()
    assert max_cut_objective.polynomial == EXPECTED_OBJECTIVE_POLY_WEIGHTED

def test_extract_cut():
    """ test extraction of final solution cut """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_objective = MaxCutObjective.get_from_instance(max_cut_instance)  # different initialization also possible
    solution = {"a": -1, "b":  1, "c": -1, "d":  1, "e": -1}
    cut = max_cut_objective.get_cut(solution)
    assert cut == {("a", "c", "e"), ("b", "d")}
