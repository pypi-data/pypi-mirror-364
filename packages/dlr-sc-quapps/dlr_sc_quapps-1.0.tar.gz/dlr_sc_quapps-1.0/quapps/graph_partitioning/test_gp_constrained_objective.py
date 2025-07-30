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

""" module for testing the GraphPartitioning ConstrainedObjective """

from quark import PolyBinary, ConstraintBinary

from quapps.graph_partitioning.gp_constrained_objective import X, ONE_SUBGRAPH_PER_NODE, CORRECT_NUMBER_OF_SUBGRAPHS
from quapps.graph_partitioning.test_gp_instance import get_example_instance


EXPECTED_OBJECTIVE_POLY = PolyBinary({((X, 1, 0), (X, 2, 1)): 5,  # Edge (1,2), weight 5
                                      ((X, 1, 0), (X, 2, 2)): 5,
                                      ((X, 1, 1), (X, 2, 0)): 5,
                                      ((X, 1, 1), (X, 2, 2)): 5,
                                      ((X, 1, 2), (X, 2, 0)): 5,
                                      ((X, 1, 2), (X, 2, 1)): 5,

                                      ((X, 2, 0), (X, 3, 1)): 4,  # Edge (2,3), weight 4
                                      ((X, 2, 0), (X, 3, 2)): 4,
                                      ((X, 2, 1), (X, 3, 0)): 4,
                                      ((X, 2, 1), (X, 3, 2)): 4,
                                      ((X, 2, 2), (X, 3, 0)): 4,
                                      ((X, 2, 2), (X, 3, 1)): 4,

                                      ((X, 2, 0), (X, 4, 1)): 5,  # Edge (2,4), weight 5
                                      ((X, 2, 0), (X, 4, 2)): 5,
                                      ((X, 2, 1), (X, 4, 0)): 5,
                                      ((X, 2, 1), (X, 4, 2)): 5,
                                      ((X, 2, 2), (X, 4, 0)): 5,
                                      ((X, 2, 2), (X, 4, 1)): 5,

                                      ((X, 1, 0), (X, 5, 1)): 4,  # Edge (1,5), weight 4
                                      ((X, 1, 0), (X, 5, 2)): 4,
                                      ((X, 1, 1), (X, 5, 0)): 4,
                                      ((X, 1, 1), (X, 5, 2)): 4,
                                      ((X, 1, 2), (X, 5, 0)): 4,
                                      ((X, 1, 2), (X, 5, 1)): 4,

                                      ((X, 5, 0), (X, 6, 1)): 2,  # Edge (5,6), weight 2
                                      ((X, 5, 0), (X, 6, 2)): 2,
                                      ((X, 5, 1), (X, 6, 0)): 2,
                                      ((X, 5, 1), (X, 6, 2)): 2,
                                      ((X, 5, 2), (X, 6, 0)): 2,
                                      ((X, 5, 2), (X, 6, 1)): 2,

                                      ((X, 5, 0), (X, 7, 1)): 3,  # Edge (5,7), weight 3
                                      ((X, 5, 0), (X, 7, 2)): 3,
                                      ((X, 5, 1), (X, 7, 0)): 3,
                                      ((X, 5, 1), (X, 7, 2)): 3,
                                      ((X, 5, 2), (X, 7, 0)): 3,
                                      ((X, 5, 2), (X, 7, 1)): 3})


def get_example_constrained_objective():
    """ construct example constrained_objective """
    gp_instance = get_example_instance()
    return gp_instance.get_constrained_objective()


def test_constrained_objective_creation():
    """ test constrained_objective creation """
    gp_constrained_objective = get_example_constrained_objective()
    assert gp_constrained_objective.objective_poly == EXPECTED_OBJECTIVE_POLY

    # The graph has 7 nodes each with 1 validity constraint, and we check for each subgraph 1,2,3
    # whether it has been assigned a node, so we have a total of 10 constraints.
    assert len(gp_constrained_objective) == 10

    for node in range(1, 7+1):
        constraint_name = ONE_SUBGRAPH_PER_NODE + f"_{node}"
        constraint = ConstraintBinary(PolyBinary({((X, node, 0),): 1, ((X, node, 1),): 1, ((X, node, 2),): 1}), 1, 1)
        assert gp_constrained_objective[constraint_name] == constraint

    for subgraph in range(3):
        constraint_name = CORRECT_NUMBER_OF_SUBGRAPHS + f"_{subgraph}"
        poly = PolyBinary({((X, 1, subgraph),): 1, ((X, 2, subgraph),): 1, ((X, 3, subgraph),): 1,
                           ((X, 4, subgraph),): 1, ((X, 5, subgraph),): 1, ((X, 6, subgraph),): 1,
                           ((X, 7, subgraph),): 1})
        constraint = ConstraintBinary(poly, 1, 7)
        assert gp_constrained_objective[constraint_name] == constraint
