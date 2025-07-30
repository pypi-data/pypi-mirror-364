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

""" module for testing the MaxColorableSubgraph ObjectiveTerms """

from quark import PolyBinary, PolyIsing

from quapps.max_colorable_subgraph import MCSObjectiveTermsDWE
from quapps.max_colorable_subgraph.mcs_objective_terms import MCSObjectiveTerms
from quapps.max_colorable_subgraph.mcs_objective_terms import COLORED_EDGES, ONE_COLOR_PER_NODE, X, S
from quapps.max_colorable_subgraph.test_mcs_instance import get_example_instance


EXPECTED_OBJECTIVE_POLY = PolyBinary({((X, 1, 0), (X, 2, 0)): 1,
                                      ((X, 1, 1), (X, 2, 1)): 1,
                                      ((X, 1, 2), (X, 2, 2)): 1,
                                      ((X, 2, 0), (X, 3, 0)): 1,
                                      ((X, 2, 0), (X, 4, 0)): 1,
                                      ((X, 2, 1), (X, 3, 1)): 1,
                                      ((X, 2, 1), (X, 4, 1)): 1,
                                      ((X, 2, 2), (X, 3, 2)): 1,
                                      ((X, 2, 2), (X, 4, 2)): 1,
                                      ((X, 3, 0), (X, 4, 0)): 1,
                                      ((X, 3, 1), (X, 4, 1)): 1,
                                      ((X, 3, 2), (X, 4, 2)): 1})

def get_example_objective_terms_one_hot():
    """ construct example_objective terms using one hot encoding """
    mcs_instance = get_example_instance()
    return MCSObjectiveTerms.get_from_instance(mcs_instance)

def get_example_objective_terms_domain_wall():
    """ construct example objective_terms using domain wall encoding """
    mcs_instance = get_example_instance()
    return MCSObjectiveTermsDWE.get_from_instance(mcs_instance)


def test_objective_terms_one_hot_creation():
    """ test objective_terms creation """
    mcs_objective_terms = get_example_objective_terms_one_hot()
    assert len(mcs_objective_terms) == 2
    assert mcs_objective_terms[COLORED_EDGES] == EXPECTED_OBJECTIVE_POLY

    expected_one_color_per_node = PolyBinary({(): 4,
                                              ((X, 1, 0),): -1,
                                              ((X, 1, 1),): -1,
                                              ((X, 1, 2),): -1,
                                              ((X, 2, 0),): -1,
                                              ((X, 2, 1),): -1,
                                              ((X, 2, 2),): -1,
                                              ((X, 3, 0),): -1,
                                              ((X, 3, 1),): -1,
                                              ((X, 3, 2),): -1,
                                              ((X, 4, 0),): -1,
                                              ((X, 4, 1),): -1,
                                              ((X, 4, 2),): -1,
                                              ((X, 1, 0), (X, 1, 1)): 2,
                                              ((X, 1, 0), (X, 1, 2)): 2,
                                              ((X, 1, 1), (X, 1, 2)): 2,
                                              ((X, 2, 0), (X, 2, 1)): 2,
                                              ((X, 2, 0), (X, 2, 2)): 2,
                                              ((X, 2, 1), (X, 2, 2)): 2,
                                              ((X, 3, 0), (X, 3, 1)): 2,
                                              ((X, 3, 0), (X, 3, 2)): 2,
                                              ((X, 3, 1), (X, 3, 2)): 2,
                                              ((X, 4, 0), (X, 4, 1)): 2,
                                              ((X, 4, 0), (X, 4, 2)): 2,
                                              ((X, 4, 1), (X, 4, 2)): 2})
    assert mcs_objective_terms[ONE_COLOR_PER_NODE] == expected_one_color_per_node

def test_objective_terms_domain_wall_creation():
    """ test objective_terms creation """
    mcs_objective_terms = get_example_objective_terms_domain_wall()
    assert len(mcs_objective_terms) == 2

    expected_colored_edges = PolyIsing({(): 2.0,
                                        ((S, 1, 0),): 0.25,
                                        ((S, 1, 1),): -0.25,
                                        ((S, 2, 0),): 0.75,
                                        ((S, 2, 1),): -0.75,
                                        ((S, 3, 0),): 0.5,
                                        ((S, 3, 1),): -0.5,
                                        ((S, 4, 0),): 0.5,
                                        ((S, 4, 1),): -0.5,
                                        ((S, 1, 0), (S, 2, 0)): 0.5,
                                        ((S, 1, 0), (S, 2, 1)): -0.25,
                                        ((S, 1, 1), (S, 2, 0)): -0.25,
                                        ((S, 1, 1), (S, 2, 1)): 0.5,
                                        ((S, 2, 0), (S, 3, 0)): 0.5,
                                        ((S, 2, 0), (S, 3, 1)): -0.25,
                                        ((S, 2, 0), (S, 4, 0)): 0.5,
                                        ((S, 2, 0), (S, 4, 1)): -0.25,
                                        ((S, 2, 1), (S, 3, 0)): -0.25,
                                        ((S, 2, 1), (S, 3, 1)): 0.5,
                                        ((S, 2, 1), (S, 4, 0)): -0.25,
                                        ((S, 2, 1), (S, 4, 1)): 0.5,
                                        ((S, 3, 0), (S, 4, 0)): 0.5,
                                        ((S, 3, 0), (S, 4, 1)): -0.25,
                                        ((S, 3, 1), (S, 4, 0)): -0.25,
                                        ((S, 3, 1), (S, 4, 1)): 0.5})
    assert mcs_objective_terms[COLORED_EDGES] == expected_colored_edges

    expected_one_color_per_node = PolyIsing({(): 4,
                                             ((S, 1, 0),): 1,
                                             ((S, 1, 1),): -1,
                                             ((S, 2, 0),): 1,
                                             ((S, 2, 1),): -1,
                                             ((S, 3, 0),): 1,
                                             ((S, 3, 1),): -1,
                                             ((S, 4, 0),): 1,
                                             ((S, 4, 1),): -1,
                                             ((S, 1, 0), (S, 1, 1)): -1,
                                             ((S, 2, 0), (S, 2, 1)): -1,
                                             ((S, 3, 0), (S, 3, 1)): -1,
                                             ((S, 4, 0), (S, 4, 1)): -1})
    assert mcs_objective_terms[ONE_COLOR_PER_NODE] == expected_one_color_per_node

def test_objective_terms_domain_wall_solution():
    """ test solution extraction """
    mcs_objective_terms = get_example_objective_terms_domain_wall()
    raw_solution = {(S, 1, 0): 1,
                    (S, 1, 1): 1,
                    (S, 2, 0): -1,
                    (S, 2, 1): 1,
                    (S, 3, 0): -1,
                    (S, 3, 1): -1,
                    (S, 4, 0): 1,
                    (S, 4, 1): -1}
    extracted_solution = mcs_objective_terms.get_node_color_index_assignment(raw_solution)
    expected_extracted_solution = {1: 0, 2: 1, 3: 2, 4: 0}
    assert extracted_solution == expected_extracted_solution
