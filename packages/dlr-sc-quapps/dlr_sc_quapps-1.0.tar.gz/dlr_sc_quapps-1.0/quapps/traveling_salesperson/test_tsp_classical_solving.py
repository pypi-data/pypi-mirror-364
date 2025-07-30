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

""" module for demonstrating the classical solving of the TravelingSalesperson problem """

from quark import ScipModel

from quapps.traveling_salesperson.test_tsp_constrained_objective import get_example_constrained_objective


EXPECTED_SOLUTION = {('x', 'b', 1): 0, ('x', 'b', 2): 1, ('x', 'b', 3): 0,
                     ('x', 'c', 1): 0, ('x', 'c', 2): 0, ('x', 'c', 3): 1,
                     ('x', 'd', 1): 1, ('x', 'd', 2): 0, ('x', 'd', 3): 0}
EXPECTED_NAME = "total_weight1.000000e+00_visit_node1.000000e+01_visit_position1.000000e+01"


def test_solving_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    tsp_constrained_objective = get_example_constrained_objective()
    model = ScipModel.get_from_constrained_objective(tsp_constrained_objective)
    solution = model.solve()
    _check_expected_values(solution, 'from_constrained_objective')

def test_solving_objective_from_constrained_objective():
    """ test if solution of 4 node test graph is correct """
    tsp_constrained_objective = get_example_constrained_objective()
    objective_terms = tsp_constrained_objective.get_objective_terms()
    terms_weights = objective_terms.get_default_terms_weights(penalty_scale=10)
    objective = objective_terms.get_objective(terms_weights)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_values(solution, EXPECTED_NAME)

def _check_expected_values(solution, exp_name):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == exp_name
    assert solution.solving_success
    assert solution.solving_status == 'optimal'
    assert solution.objective_value == 5
    assert solution == EXPECTED_SOLUTION
