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

""" module for demonstrating the classical solving of the MaxCut problem """

from quark import ScipModel

from quapps.max_cut import MaxCutObjective
from quapps.max_cut.max_cut_constrained_objective import MaxCutConstrainedObjective, MaxCutConstrainedObjectiveLinear
from quapps.max_cut.max_cut_scip_model import MaxCutScipModel
from quapps.max_cut.test_max_cut_instance import get_example_max_cut_instance, get_example_weighted_max_cut_instance


# always two due to symmetry
POSSIBLE_ISING_SOLUTIONS =          [{"a":  1, "b": -1, "c":  1, "d": -1, "e":  1},
                                     {"a": -1, "b":  1, "c": -1, "d":  1, "e": -1},
                                     {"a": 1, "b": 1, "c": -1, "d": 1, "e": -1},
                                     {"a": -1, "b": -1, "c": 1, "d": -1, "e": 1}]
POSSIBLE_ISING_SOLUTIONS_WEIGHTED = [{"a": -1, "b": -1, "c":  1, "d": -1, "e":  1},
                                     {"a":  1, "b":  1, "c": -1, "d":  1, "e": -1}]
POSSIBLE_SOLUTION_CUTS = [{("a", "c", "e"), ("b", "d")},
                          {("a", "b", "d"), ("c", "e")}]
EXP_NAME = "from_objective"


def test_solution_of_objective():
    """ test if solution of constrained_objective contains expected data """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_objective = MaxCutObjective.get_from_instance(max_cut_instance)
    model = ScipModel.get_from_objective(max_cut_objective)
    solution = model.solve()
    _check_expected_values(solution, -5, POSSIBLE_ISING_SOLUTIONS)

    solution_cut = max_cut_objective.get_cut(solution)
    assert solution_cut in POSSIBLE_SOLUTION_CUTS

def test_solution_of_objective_weighted():
    """ test if solution of objective from objective_terms contains expected data """
    max_cut_instance = get_example_weighted_max_cut_instance()
    max_cut_objective = MaxCutObjective.get_from_instance(max_cut_instance)
    model = ScipModel.get_from_objective(max_cut_objective)
    solution = model.solve()
    _check_expected_values(solution, -8.5, POSSIBLE_ISING_SOLUTIONS_WEIGHTED)

def test_solution_of_objective_weighted_fix_symmetry():
    """ test if solution of objective from objective_terms contains expected data """
    max_cut_instance = get_example_weighted_max_cut_instance()
    max_cut_objective = MaxCutObjective.get_from_instance(max_cut_instance)
    objective_fixed = max_cut_objective.break_symmetry_by_fixing_variable("a", 1)
    model = ScipModel.get_from_objective(objective_fixed)
    solution = model.solve()
    _check_expected_values(solution, -8.5, [{"b": 1, "c": -1, "d": 1, "e": -1}])


def _check_expected_values(solution, obj_value, exp_sols):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == EXP_NAME
    assert solution.solving_success
    assert solution.solving_status == "optimal"
    assert solution.objective_value == obj_value
    assert solution in exp_sols


def test_solution_of_constrained_objective():
    """ test if solution of constrained_objective is correct """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_constrained_objective = MaxCutConstrainedObjective.get_from_instance(max_cut_instance)
    model = ScipModel.get_from_constrained_objective(max_cut_constrained_objective, name=EXP_NAME)
    solution = model.solve()
    assert solution.objective_value == -5
    solution_cut = max_cut_constrained_objective.get_cut(solution)
    assert solution_cut in POSSIBLE_SOLUTION_CUTS

def test_solution_of_constrained_objective_linear():
    """ test if solution of linear constrained_objective is correct """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_constrained_objective_linear = MaxCutConstrainedObjectiveLinear.get_from_instance(max_cut_instance)
    model = ScipModel.get_from_constrained_objective(max_cut_constrained_objective_linear, name=EXP_NAME)
    solution = model.solve()
    assert solution.objective_value == -5
    solution_cut = max_cut_constrained_objective_linear.get_cut(solution)
    assert solution_cut in POSSIBLE_SOLUTION_CUTS

def test_solution_of_scip_model():
    """ test if solution of scip model is correct """
    max_cut_instance = get_example_max_cut_instance()
    model = MaxCutScipModel(max_cut_instance, EXP_NAME)
    solution_binary = model.solve()
    solution_ising = solution_binary.to_ising()
    _check_expected_values(solution_ising, -5, POSSIBLE_ISING_SOLUTIONS)
