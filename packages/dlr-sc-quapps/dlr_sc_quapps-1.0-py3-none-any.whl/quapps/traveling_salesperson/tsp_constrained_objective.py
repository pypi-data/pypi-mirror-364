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

""" module for the TravelingSalesperson ConstrainedObjective """

from math import isclose

from quark import ConstrainedObjective, PolyBinary, ConstraintBinary


VISIT_NODE = "visit_node"
VISIT_POSITION = "visit_position"
TOTAL_WEIGHT = "total_weight"
X = 'x'


class TSPConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the TravelingSalesperson problem

    The binary variable x_n_i is 1 if node n is visited as i-th position and 0 otherwise.
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # sum the weight of all edges without the start node for all positions
        # sum_{i = 1,...,|Nodes|-2} sum_{(n, m) in Edges, n,m != start} w_n_m x_n_i x_m_(i+1)
        obj_poly = PolyBinary({((X, edge[0], i), (X, edge[1], i+1)): instance.weights.get(edge)
                               for edge in instance.graph.edges if instance.start_node not in edge
                               for i in range(1, instance.num_nodes-1)})

        # add the weight of the edges of the start node to the second node (position 1)
        # sum_{(start_node, n) in Edges} w_start_n x_n_1
        for edge in instance.graph.out_edges(instance.start_node):
            obj_poly += PolyBinary({((X, edge[1], 1),): instance.weights.get(edge)})

        # add the weight of the edges of second last node to the last node (the start node again)
        # sum_{(n, start) in Edges} w_n_start x_n_(|Nodes|-1)
        for edge in instance.graph.in_edges(instance.start_node):
            obj_poly += PolyBinary({((X, edge[0], instance.num_nodes-1),): instance.weights.get(edge)})

        return obj_poly

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        constraints = {}

        all_but_start_node = list(instance.graph.nodes)
        all_but_start_node.remove(instance.start_node)

        # every position has to be used exactly once by one of the nodes except the start node
        # for all i = 1,...,|Nodes|-1: sum_{n in Nodes, n != start} x_n_i == 1
        for i in range(1, instance.num_nodes):
            poly = PolyBinary({((X, node, i),): 1 for node in all_but_start_node})
            constraints[VISIT_POSITION + f"_{i}"] = ConstraintBinary(poly, 1, 1)

        # every node has to get exactly one position
        # for all n in Nodes, n != start: sum_{i = 1,...,|Nodes|-1} x_n_i == 1
        for node in all_but_start_node:
            poly = PolyBinary({((X, node, i),): 1 for i in range(1, instance.num_nodes)})
            constraints[VISIT_NODE + f"_{node}"] = ConstraintBinary(poly, 1, 1)

        return constraints

    def get_objective_terms(self, objective_name=TOTAL_WEIGHT, combine_prefixes=(VISIT_NODE, VISIT_POSITION), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """ overwrite ConstrainedObjective.get_objective_terms to set different default values """
        return super().get_objective_terms(objective_name, combine_prefixes, name, reduction_strategy,
                                           check_special_constraints)

    @staticmethod
    def get_tour(raw_solution, start_node=0):
        """ get the tour over the nodes """
        pos_2_node = {position: node for (_, node, position), value in raw_solution.items() if isclose(value, 1)}
        return [start_node] + [pos_2_node[pos] for pos in range(1, len(pos_2_node) + 1)] + [start_node]
