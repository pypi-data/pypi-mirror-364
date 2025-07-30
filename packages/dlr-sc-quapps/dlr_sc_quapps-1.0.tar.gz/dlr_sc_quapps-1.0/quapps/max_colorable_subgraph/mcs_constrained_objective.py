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

""" module for the MaxColorableSubgraph ConstrainedObjective """

from math import isclose

from quark import ConstrainedObjective, ConstraintBinary, PolyBinary


ONE_COLOR_PER_NODE = "one_color_per_node"
COLORED_EDGES = "colored_edges"
X = "x"


class MCSConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the MaxColorableSubgraph problem

    The binary variable x_n_c is 1 if node n is colored with color c and 0 otherwise.
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # counting the number of wrongly colored edges:
        # sum_[c in Colors] sum_[(n, m) in Edges] (1 * x_n_c * x_m_c)
        return PolyBinary({((X, node1, color), (X, node2, color)): 1 for node1, node2 in instance.edges
                                                                     for color in instance.colors})

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        constraints = {}

        # every node should get exactly one color:
        # for all n in Nodes: sum_[c in Colors] x_n_c == 1
        for node in instance.nodes:
            poly = PolyBinary({((X, node, color),): 1 for color in instance.colors})
            constraints[ONE_COLOR_PER_NODE + f"_{node}"] = ConstraintBinary(poly, 1, 1)

        return constraints

    def get_objective_terms(self, objective_name=COLORED_EDGES, combine_prefixes=(ONE_COLOR_PER_NODE,), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """ overwrite ConstrainedObjective.get_objective_terms to set different default values """
        return super().get_objective_terms(objective_name, combine_prefixes, name, reduction_strategy,
                                           check_special_constraints)

    @staticmethod
    def get_node_color_assignment(raw_solution):
        """ extract the actual solution from the variable assignment """
        return {node : color for (_, node, color), value in raw_solution.items() if isclose(value, 1)}
