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

""" module for testing the MaxColorableSubgraph ConstrainedObjective """

from quark import PolyBinary

from quapps.max_colorable_subgraph.mcs_objective_terms import ONE_COLOR_PER_NODE, COLORED_EDGES
from quapps.max_colorable_subgraph.test_mcs_objective_terms import get_example_instance, \
    get_example_objective_terms_one_hot, EXPECTED_OBJECTIVE_POLY, X


def get_example_constrained_objective():
    """ construct example constrained_objective """
    mcs_instance = get_example_instance()
    return mcs_instance.get_constrained_objective()

def test_constrained_objective_creation():
    """ test constrained_objective creation """
    mcs_constrained_objective = get_example_constrained_objective()
    assert mcs_constrained_objective.objective_poly == EXPECTED_OBJECTIVE_POLY
    assert len(mcs_constrained_objective) == 4

    for node in range(1, 5):
        const_name = ONE_COLOR_PER_NODE + f"_{node}"
        assert mcs_constrained_objective[const_name].upper_bound == 1
        assert mcs_constrained_objective[const_name].lower_bound == 1
        assert mcs_constrained_objective[const_name].polynomial == PolyBinary({((X, node, 0),): 1,
                                                                              ((X, node, 1),): 1,
                                                                              ((X, node, 2),): 1})

def test_objective_terms_creation():
    """ test objective_terms creation via the constrained_objective with combining equally prefixed terms """
    mcs_constrained_objective = get_example_constrained_objective()
    mcs_objective_terms = get_example_objective_terms_one_hot()
    mcs_ots_from_co = mcs_constrained_objective.get_objective_terms()
    assert mcs_ots_from_co == mcs_objective_terms

def test_objective_terms_creation_without_combine():
    """ test objective_terms creation via the constrained_objective without combining equally prefixed terms """
    mcs_constrained_objective = get_example_constrained_objective()
    mcs_objective_terms = get_example_objective_terms_one_hot()
    mcs_ots_from_co = mcs_constrained_objective.get_objective_terms(COLORED_EDGES, combine_prefixes=())
    assert len(mcs_ots_from_co) > len(mcs_objective_terms)
