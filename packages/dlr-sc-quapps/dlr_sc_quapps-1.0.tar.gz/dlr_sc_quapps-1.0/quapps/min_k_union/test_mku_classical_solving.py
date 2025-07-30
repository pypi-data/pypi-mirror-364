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

""" module for demonstrating the classical solving of the FlightGateAssignment problem """

from math import isclose

from quark import ScipModel

from quapps.min_k_union import MKUConstrainedObjective
from quapps.min_k_union.mku_objective_terms import MKUObjectiveTerms
from quapps.min_k_union.mku_constrained_objective import COUNT_ELEMENTS, ELEMENT_IN_SUBSET, USE_K_SUBSETS
from quapps.min_k_union.test_mku_constrained_objective import get_example_instance, get_example_constrained_objective


def test_solving_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    mku_instance = get_example_instance()
    mku_constrained_objective = MKUConstrainedObjective.get_from_instance(mku_instance)
    model = ScipModel.get_from_constrained_objective(mku_constrained_objective, name="mku_constrained_objective")
    solution = model.solve()

    exp_solution = {('e', 1): 0,
                    ('e', 2): 1,
                    ('e', 3): 0,
                    ('e', 4): 1,
                    ('s', '(1, 2)'): 0,
                    ('s', '(1, 2, 4)'): 0,
                    ('s', '(1,)'): 0,
                    ('s', '(2, 3, 4)'): 0,
                    ('s', '(2, 4)'): 1,
                    ('s', '(2,)'): 1,
                    ('s', '(3,)'): 0,
                    ('s', '(4,)'): 1}
    assert solution.name == "mku_constrained_objective"
    assert solution.solving_success
    assert solution.solving_status == "optimal"
    assert solution.objective_value == 2
    assert solution == exp_solution
    assert MKUConstrainedObjective.get_subsets(solution) == {(2,), (2, 4), (4,)}

def test_solving_objective():
    """ test if solution of objective from constrained_objective contains expected data """
    pws = {COUNT_ELEMENTS: 1, USE_K_SUBSETS: 10, ELEMENT_IN_SUBSET: 10}
    fga_constrained_objective = get_example_constrained_objective()
    objective_terms = fga_constrained_objective.get_objective_terms()
    objective = objective_terms.get_objective(pws)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()

    expected_name = "count_elements1.000000e+00_use_k_subsets1.000000e+01_element_in_subset1.000000e+01"
    assert solution.name == expected_name
    assert solution.solving_success
    assert solution.solving_status == "optimal"
    assert solution.objective_value == 2
    assert MKUConstrainedObjective.get_subsets(solution) == {(1,), (1, 2), (2,)}  # other solution with same value

def test_solving_objective_terms():
    """ test if solution of constrained_objective contains expected data """
    mku_instance = get_example_instance()
    mku_objective_terms = MKUObjectiveTerms.get_from_instance(mku_instance)
    terms_weights = mku_objective_terms.get_default_terms_weights()
    mku_objective = mku_objective_terms.get_objective(terms_weights)
    model = ScipModel.get_from_objective(mku_objective)
    solution = model.solve()

    exp_solution = {('e', 1): 1,
                    ('e', 2): 1,
                    ('e', 3): 0,
                    ('e', 4): 0,
                    ('s', '(1, 2)'): 1,
                    ('s', '(1, 2, 4)'): 0,
                    ('s', '(1,)'): 1,
                    ('s', '(2, 3, 4)'): 0,
                    ('s', '(2, 4)'): 0,
                    ('s', '(2,)'): 1,
                    ('s', '(3,)'): 0,
                    ('s', '(4,)'): 0}
    assert solution.name == "count_elements1.000000e+00_use_k_subsets1.000000e+00_element_in_subset1.000000e+00"
    assert solution.solving_success
    assert solution.solving_status == "optimal"
    assert isclose(solution.objective_value, 2)
    assert solution == exp_solution
    assert MKUConstrainedObjective.get_subsets(solution) == {(1,), (1, 2), (2,)}
