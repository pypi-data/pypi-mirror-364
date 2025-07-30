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

""" module for demonstrating the classical solving of the FlightGateAssignment problem """

import pytest
from quark import ScipModel

from quapps.flight_gate_assignment import FGAConstrainedObjective
from quapps.flight_gate_assignment.fga_objective_terms import TRANSIT, ONE_GATE_PER_FLIGHT, FLIGHTS_TIME_OVERLAP
from quapps.flight_gate_assignment.test_fga_constrained_objective import get_example_instance, \
    get_example_constrained_objective, get_example_objective_terms
from quapps.flight_gate_assignment.fga_utils_classical_solving import get_valid_solution, get_min_gate_num


def test_get_min_gate_num():
    """ test lower bound on number of gates """
    fga_instance = get_example_instance()
    assert get_min_gate_num(fga_instance) == 2

def test_get_valid_solution():
    """ test construction of a valid solution """
    fga_instance = get_example_instance()
    solution = get_valid_solution(fga_instance)
    assert solution.solving_success
    assert solution == {(1, 1): 1, (1, 2): 0, (2, 1): 0, (2, 2): 1, (3, 1): 1, (3, 2): 0}

    fga_constrained_objective = get_example_constrained_objective(fga_instance)
    assert fga_constrained_objective.check_validity(solution)

    unsolvable = get_example_instance()
    unsolvable.time_buffer = 100
    solution = get_valid_solution(unsolvable)
    assert not solution.solving_success

def test_solution_of_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    fga_constrained_objective = get_example_constrained_objective()
    model = ScipModel.get_from_constrained_objective(fga_constrained_objective, name="fga_constrained_objective")
    solution = model.solve()
    _check_expected_values(solution, "fga_constrained_objective")

def test_solution_of_objective_from_constrained_objective():
    """ test if solution of objective from constrained_objective contains expected data """
    pws = {ONE_GATE_PER_FLIGHT: 650, FLIGHTS_TIME_OVERLAP: 135, TRANSIT: 1}
    fga_constrained_objective = get_example_constrained_objective()

    with pytest.warns(UserWarning, match="The two variables"):
        objective_terms = fga_constrained_objective.get_objective_terms(TRANSIT, ONE_GATE_PER_FLIGHT)

    objective = objective_terms.get_objective(pws)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()

    expected_name = "one_gate_per_flight6.500000e+02_flights_time_overlap1.350000e+02_transit1.000000e+00"
    _check_expected_values(solution, expected_name)

def test_solution_of_objective_from_objective_terms():
    """ test if solution of objective from objective_terms contains expected data """
    # here the factors are already included in the objective terms creation
    pws = {ONE_GATE_PER_FLIGHT: 1, FLIGHTS_TIME_OVERLAP: 1, TRANSIT: 1}
    fga_objective_terms = get_example_objective_terms()
    objective = fga_objective_terms.get_objective(pws)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()

    expected_name = "one_gate_per_flight1.000000e+00_flights_time_overlap1.000000e+00_transit1.000000e+00"
    _check_expected_values(solution, expected_name)


def _check_expected_values(solution, expected_name):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == expected_name
    assert solution.solving_success
    assert solution.solving_status == "optimal"
    assert solution.objective_value == 1090
    assert solution == {(1, 1): 0, (1, 2): 1,
                        (2, 1): 1, (2, 2): 0,
                        (3, 1): 0, (3, 2): 1}
    assert FGAConstrainedObjective.get_flight_gate_assignment(solution) == {1 : 2, 2 : 1, 3 : 2}
