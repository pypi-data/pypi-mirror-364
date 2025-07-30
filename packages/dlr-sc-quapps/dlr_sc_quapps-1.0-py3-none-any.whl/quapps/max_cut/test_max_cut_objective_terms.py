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

""" module for testing the MaxCut ObjectiveTerms """

from quapps.max_cut.max_cut_objective_terms import MaxCutObjectiveTerms, NUM_CUTS
from quapps.max_cut.test_max_cut_instance import get_example_max_cut_instance, get_example_weighted_max_cut_instance
from quapps.max_cut.test_max_cut_objective import EXPECTED_OBJECTIVE_POLY, EXPECTED_OBJECTIVE_POLY_WEIGHTED


def test_objective_terms_init():
    """ test objective_terms creation """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_objective_terms = MaxCutObjectiveTerms.get_from_instance(max_cut_instance)
    assert len(max_cut_objective_terms) == 1
    assert max_cut_objective_terms[NUM_CUTS] == EXPECTED_OBJECTIVE_POLY

def test_objective_terms_init_weighted():
    """ test objective_terms creation with weights"""
    max_cut_instance = get_example_weighted_max_cut_instance()
    max_cut_objective_terms = MaxCutObjectiveTerms.get_from_instance(max_cut_instance)
    assert len(max_cut_objective_terms) == 1
    assert max_cut_objective_terms[NUM_CUTS] == EXPECTED_OBJECTIVE_POLY_WEIGHTED
