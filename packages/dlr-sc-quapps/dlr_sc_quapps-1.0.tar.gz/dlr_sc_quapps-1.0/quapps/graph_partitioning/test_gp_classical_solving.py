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

""" module for demonstrating the classical solving of the GraphPartitioning problem """

from quark import ScipModel

from quapps.graph_partitioning import GPConstrainedObjective
from quapps.graph_partitioning.gp_constrained_objective import (ONE_SUBGRAPH_PER_NODE, CROSSING_EDGES,
                                                                CORRECT_NUMBER_OF_SUBGRAPHS)
from quapps.graph_partitioning.test_gp_constrained_objective import get_example_constrained_objective


PWS = {CROSSING_EDGES: 1, ONE_SUBGRAPH_PER_NODE: 7, CORRECT_NUMBER_OF_SUBGRAPHS: 3}
EXPECTED_NAME = "crossing_edges1.000000e+00_one_subgraph_per_node7.000000e+00_correct_number_of_subgraphs3.000000e+00"


def test_solving_constrained_objective():
    """ test if solution of constrained_objective contains expected data """
    gp_constrained_objective = get_example_constrained_objective()
    model = ScipModel.get_from_constrained_objective(gp_constrained_objective)
    solution = model.solve()
    _check_expected_solution_data(solution, "from_constrained_objective")

    extracted = GPConstrainedObjective.get_node_partition_assignment(solution)
    _check_expected_extracted_solution(extracted)

def test_solving_objective_from_constrained_objective():
    """ test if solution of objective from constrained_objective contains expected data """
    gp_constrained_objective = get_example_constrained_objective()
    objective_terms = gp_constrained_objective.get_objective_terms()
    objective = objective_terms.get_objective(PWS)
    model = ScipModel.get_from_objective(objective)
    solution = model.solve()
    _check_expected_solution_data(solution)

    extracted = GPConstrainedObjective.get_node_partition_assignment(solution)
    _check_expected_extracted_solution(extracted)


def _check_expected_solution_data(solution, expected_name=EXPECTED_NAME):
    """ check if the solution object contains the expected data and a valid variable assignment """
    assert solution.name == expected_name
    assert solution.solving_success
    assert solution.objective_value == 5  # Optimal value. See below for derivation.
    assert solution.solving_status == "optimal"

def _check_expected_extracted_solution(extracted):
    """ check if the calculated (extracted) solution is indeed the optimal solution for this instance """
    # Since a partition into 3 subgraphs must have at least 2 crossing edges and since the
    # lowest weights in this graph are 2 and 3, the optimal solution has a value of at least 5.
    # This value is attained by partitioning the graph into the following node partitions: {1, 2, 3, 4, 5} u {6} u {7}.
    # Changing any of these sets changes the set of crossing edges and, since every other
    # edge has weight > 3, thus increases the value of our solution. Therefore, this solution
    # is unique up to permutation of the subgraph assignments.
    all_permutations_of_optimal_solution = [{1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 2},
                                            {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 2, 7: 1},
                                            {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0, 7: 2},
                                            {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 0},
                                            {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 0, 7: 1},
                                            {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 1, 7: 0}]
    assert extracted in all_permutations_of_optimal_solution
