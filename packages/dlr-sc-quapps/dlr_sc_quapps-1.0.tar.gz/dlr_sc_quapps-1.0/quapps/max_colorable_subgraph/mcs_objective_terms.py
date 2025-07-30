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

"""
module for the MaxColorableSubgraph ObjectiveTerms

THE IMPLEMENTATION OF MCSObjectiveTerms ONLY SERVES AS AN EXAMPLE.
To run the MCS problem productively, use the MCSConstrainedObjective.

The implementation of MCSObjectiveTermsDWE uses a different encoding than MCSConstrainedObjective
and its corresponding objective terms, whose advantage is however unclear.
"""

from math import isclose

from quark import ObjectiveTerms, PolyBinary, PolyIsing


ONE_COLOR_PER_NODE = "one_color_per_node"
COLORED_EDGES = "colored_edges"
X, S = "x", "s"


class MCSObjectiveTerms(ObjectiveTerms):
    """
    implementation of the objective terms for the MaxColorableSubgraph problem
    using one hot encoding for coloring
    """

    @staticmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names
        """
        return [ONE_COLOR_PER_NODE]

    @staticmethod
    def _get_objective_terms(instance):
        """ get the objective terms from the instance data using one hot encoding """
        objective_terms = {COLORED_EDGES: PolyBinary(),
                           ONE_COLOR_PER_NODE : PolyBinary()}

        # actual objective
        # counting the number of wrongly colored edges:
        # sum_[c in Colors] sum_[(n, m) in Edges] (1 * x_n_c * x_m_c)
        for color in instance.colors:
            objective_terms[COLORED_EDGES] += PolyBinary({((X, node1, color), (X, node2, color)): 1
                                                          for node1, node2 in instance.edges})

        # objective terms from the constraint
        # every node should get exactly one color:
        # sum_[n in Nodes] (sum_[c in Colors] x_n_c - 1)^2
        for node in instance.nodes:
            poly = PolyBinary({((X, node, color),): 1 for color in instance.colors}) - 1
            objective_terms[ONE_COLOR_PER_NODE] += poly * poly

        return objective_terms


class MCSObjectiveTermsDWE(ObjectiveTerms):
    """
    implementation of the objective terms for the MaxColorableSubgraph problem
    using domain wall encoding for coloring
    """

    @staticmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names
        """
        return [ONE_COLOR_PER_NODE]

    @staticmethod
    def _get_objective_terms(instance):
        """ get the objective terms from the instance data using domain wall encoding """
        objective_terms = {COLORED_EDGES: PolyIsing(),
                           ONE_COLOR_PER_NODE: PolyIsing()}

        num_colors = len(instance.colors)

        def dw_spin(node, color_index):
            """ abbreviation of the function call """
            return get_domain_wall_spin(color_index, num_colors, (S, node, color_index))

        # actual objective
        # counting the number of wrongly colored edges
        for color_index in range(num_colors):
            for node1, node2 in instance.edges:
                objective_terms[COLORED_EDGES] += (dw_spin(node1, color_index) - dw_spin(node1, color_index - 1)) \
                                                  * (dw_spin(node2, color_index) - dw_spin(node2, color_index - 1))
        objective_terms[COLORED_EDGES] *= 0.25

        # objective terms from the constraint
        # every node should get exactly one color
        # penalty term which vanishes iff there is a single domain wall per node
        objective_terms[ONE_COLOR_PER_NODE] += (num_colors - 2) * len(instance.nodes)
        for node in instance.nodes:
            for color_index in range(num_colors):
                objective_terms[ONE_COLOR_PER_NODE] -= dw_spin(node, color_index) * dw_spin(node, color_index - 1)

        return objective_terms

    @staticmethod
    def get_node_color_index_assignment(raw_solution):
        """ extract the actual solution from the variable assignment """
        color_indices = {}
        num_colors = max(color_index for (_, _, color_index) in raw_solution.keys()) + 2
        for node in set(node for (_, node, _) in raw_solution.keys()):
            chain = [-1] + [raw_solution[(S, node, index)] for index in range(num_colors - 1)] + [1]
            wall = [isclose(chain[index] * chain[index + 1], -1) for index in range(num_colors)]
            color_indices[node] = wall.index(True)
        return color_indices


def get_domain_wall_spin(index, number_of_encoded_values, variable):
    """
    generic function that returns the ising monomial for the given index in the domain wall encoding,
    where the first index (-1) is fixed to the constant term -1
    and the last index (number_of_encoded_values - 1) is fixed to the constant term +1

    :param (int) index: the index corresponding to a domain wall
    :param (int) number_of_encoded_values: the total number of spins representing the possible options
    :param (tuple) variable: tuple representing the variable of the polynomial corresponding to this domain wall
    """
    if index == -1:
        return PolyIsing({(): -1})
    if index == number_of_encoded_values - 1:
        return PolyIsing({(): 1})
    return PolyIsing({(variable,): 1})
