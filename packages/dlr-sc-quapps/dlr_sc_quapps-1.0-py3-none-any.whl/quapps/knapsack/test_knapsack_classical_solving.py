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

""" module for demonstrating the classical solving of the Knapsack problem """

from quark import ScipModel

from quapps.knapsack import KnapsackConstrainedObjective
from quapps.knapsack.knapsack_constrained_objective import KNAPSACK_VALUE, WEIGHT_BELOW_CAPACITY
from quapps.knapsack.test_knapsack_constrained_objective import get_example_constrained_objective

PWS = {KNAPSACK_VALUE: 1, WEIGHT_BELOW_CAPACITY: 1}
EXPECTED_NAME = "knapsack_value1.000000e+00_weight_below_capacity1.000000e+00"


def test_solving_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    knapsack_constrained_objective = get_example_constrained_objective()
    model = ScipModel.get_from_constrained_objective(knapsack_constrained_objective)
    solution = model.solve()
    _check_expected_solution_data(solution, "from_constrained_objective")

    extracted = KnapsackConstrainedObjective.get_items(solution)
    assert extracted == {"A", "B", "E", "F"}  # Check if extracted solution is correct


def test_solving_objective_from_constrained_objective():
    """ test if solution of objective from constrained_objective contains expected data """
    knapsack_constrained_objective = get_example_constrained_objective()
    objective_terms = knapsack_constrained_objective.get_objective_terms()
    objective = objective_terms.get_objective(PWS)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_solution_data(solution)

    extracted = KnapsackConstrainedObjective.get_items(solution)
    assert extracted == {"A", "B", "E", "F"}  # Check if extracted solution is correct


def _check_expected_solution_data(solution, expected_name=EXPECTED_NAME):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == expected_name
    assert solution.solving_success
    assert solution.objective_value == -17
    assert solution.solving_status == "optimal"
