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

""" module for demonstrating the classical solving of the MaxColorableSubgraph problem """

from quark import ScipModel

from quapps.max_colorable_subgraph import MCSConstrainedObjective, MCSObjectiveTermsDWE
from quapps.max_colorable_subgraph.mcs_objective_terms import ONE_COLOR_PER_NODE, COLORED_EDGES
from quapps.max_colorable_subgraph.test_mcs_constrained_objective import get_example_constrained_objective
from quapps.max_colorable_subgraph.test_mcs_objective_terms import get_example_objective_terms_one_hot, \
    get_example_objective_terms_domain_wall


PWS = {ONE_COLOR_PER_NODE: 1,
       COLORED_EDGES     : 1}
EXPECTED_NAME = "one_color_per_node1.000000e+00_colored_edges1.000000e+00"


def test_solving_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    mcs_constrained_objective = get_example_constrained_objective()
    model = ScipModel.get_from_constrained_objective(mcs_constrained_objective)
    solution = model.solve()
    _check_expected_solution_data(solution, "from_constrained_objective")

    extracted = MCSConstrainedObjective.get_node_color_assignment(solution)
    _check_expected_extracted_solution(extracted)

def test_solving_objective_from_constrained_objective():
    """ test if solution of objective from constrained_objective contains expected data """
    mcs_constrained_objective = get_example_constrained_objective()
    objective_terms = mcs_constrained_objective.get_objective_terms(COLORED_EDGES, ONE_COLOR_PER_NODE)
    objective = objective_terms.get_objective(PWS)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_solution_data(solution)

    extracted = MCSConstrainedObjective.get_node_color_assignment(solution)
    _check_expected_extracted_solution(extracted)

def test_solving_objective_from_objective_terms_one_hot():
    """ test if solution of objective from objective_terms using one hot encoding contains expected data """
    mcs_objective_terms = get_example_objective_terms_one_hot()
    objective = mcs_objective_terms.get_objective(PWS)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_solution_data(solution)

    extracted = MCSConstrainedObjective.get_node_color_assignment(solution)
    _check_expected_extracted_solution(extracted)

def test_solving_objective_from_objective_terms_domain_wall():
    """ test if solution of objective from objective_terms using domain wall encoding contains expected data """
    mcs_objective_terms = get_example_objective_terms_domain_wall()
    objective = mcs_objective_terms.get_objective(PWS)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_solution_data(solution)

    extracted = MCSObjectiveTermsDWE.get_node_color_index_assignment(solution)
    _check_expected_extracted_solution(extracted)

def _check_expected_solution_data(solution, expected_name=EXPECTED_NAME):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == expected_name
    assert solution.solving_success
    assert solution.objective_value == 0
    assert solution.solving_status == "optimal"

def _check_expected_extracted_solution(extracted):
    assert extracted[1] in [extracted[3], extracted[4]]
    assert extracted[1] != extracted[2]
    assert extracted[2] != extracted[3]
    assert extracted[2] != extracted[4]
    assert extracted[3] != extracted[4]
