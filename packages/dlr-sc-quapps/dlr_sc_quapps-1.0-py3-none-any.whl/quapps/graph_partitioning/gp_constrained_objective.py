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

""" module for the GraphPartitioning ConstrainedObjective """

from math import isclose

from quark import ConstrainedObjective, ConstraintBinary, PolyBinary


CROSSING_EDGES = "crossing_edges"
ONE_SUBGRAPH_PER_NODE = "one_subgraph_per_node"
CORRECT_NUMBER_OF_SUBGRAPHS = "correct_number_of_subgraphs"
X = "x"


class GPConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective for the GraphPartitioning problem

    The binary variable x_n_s is 1 if node n belongs to subgraph s and 0 otherwise.
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # sum the weights of the edges between the partitions
        return PolyBinary({((X, i, subgraph_1), (X, j, subgraph_2)): instance.edges[(i, j)]
                           for (i, j) in instance.edges.keys()
                           for subgraph_1 in range(instance.number_of_subgraphs)
                           for subgraph_2 in range(instance.number_of_subgraphs)
                           if subgraph_1 != subgraph_2})

    @staticmethod
    def _get_constraints(instance):
        """
        get the constraints from the instance data,
        the first set of constraints restricts the number of assigned subgraphs for each node,
        the second set ensures that the graph is partitioned into the correct number of subgraphs
        """
        constraints = {}
        for node in instance.nodes:
            # every node must be in exactly 1 subgraph
            poly = PolyBinary({((X, node, subgraph), ): 1 for subgraph in range(instance.number_of_subgraphs)})
            constraints[ONE_SUBGRAPH_PER_NODE + f"_{node}"] = ConstraintBinary(poly, 1, 1)

        for subgraph in range(instance.number_of_subgraphs):
            # partition the graph into exactly k subgraphs
            poly = PolyBinary({((X, node, subgraph), ): 1 for node in instance.nodes})
            constraints[CORRECT_NUMBER_OF_SUBGRAPHS + f"_{subgraph}"] = ConstraintBinary(poly, 1, len(instance.nodes))

        return constraints

    def get_objective_terms(self, objective_name=CROSSING_EDGES,
                            combine_prefixes=(ONE_SUBGRAPH_PER_NODE, CORRECT_NUMBER_OF_SUBGRAPHS), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """ overwrite ConstrainedObjective.get_objective_terms to set different default values """
        return super().get_objective_terms(objective_name, combine_prefixes, name, reduction_strategy,
                                           check_special_constraints)

    @staticmethod
    def get_node_partition_assignment(raw_solution):
        """ extract the actual solution from the variable assignment """
        # Get the node-subgraph pairs if the decision variable is assigned to 1
        # (and has length 3, in contrast to slack variables which have length 2).
        return {variable[1]: variable[2] for variable, value in raw_solution.items()
                if isclose(value, 1) and len(variable) == 3}
