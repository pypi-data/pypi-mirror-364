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

""" module for demonstrating the classical solving of the SubsetSum problem """

from quark import ScipModel

from quapps.subset_sum import SubsetSumObjective
from quapps.subset_sum.subset_sum_constrained_objective import (SUM_VALUE, SUM_BELOW_TARGET)
from quapps.subset_sum.test_subset_sum_constrained_objective import get_example_constrained_objective
from quapps.subset_sum.test_subset_sum_objective import get_example_objective


PWS = {SUM_VALUE: 1, SUM_BELOW_TARGET: 10}
EXPECTED_NAME = 'sum_value1.000000e+00_sum_below_target1.000000e+01'


def test_solving_objective():
    """ test if solution of objective contains expected data """
    ssp_objective = get_example_objective()
    model = ScipModel.get_from_objective(ssp_objective)
    solution = model.solve()
    _check_expected_solution_data(solution, 0, "from_objective")

    extracted = SubsetSumObjective.get_numbers(solution)
    _check_expected_extracted_solution(extracted)

def test_solving_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    ssp_constrained_objective = get_example_constrained_objective()
    model = ScipModel.get_from_constrained_objective(ssp_constrained_objective)
    solution = model.solve()
    _check_expected_solution_data(solution, -87, "from_constrained_objective")

    extracted = SubsetSumObjective.get_numbers(solution)
    _check_expected_extracted_solution(extracted)

def test_solving_objective_from_constrained_objective():
    """ test if solution of objective from constrained_objective contains expected data """
    ssp_constrained_objective = get_example_constrained_objective()
    objective_terms = ssp_constrained_objective.get_objective_terms()
    objective = objective_terms.get_objective(PWS)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_solution_data(solution, -87)

    extracted = SubsetSumObjective.get_numbers(solution)
    _check_expected_extracted_solution(extracted)

def _check_expected_solution_data(solution, expected_value, expected_name=EXPECTED_NAME):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == expected_name
    assert solution.solving_success
    assert solution.objective_value == expected_value
    assert solution.solving_status == "optimal"

def _check_expected_extracted_solution(extracted):
    """ check if the extracted solution contains the expected data """
    assert extracted == (20, 25, 42)
    assert sum(extracted) == 87
