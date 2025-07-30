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
module for the MaxCut ConstrainedObjective

THIS IMPLEMENTATION ONLY SERVES AS AN EXAMPLE.
To run the MaxCut problem productively, use the MaxCutObjective.
"""

from quark import ConstrainedObjective, PolyBinary, ConstraintBinary


class MaxCutConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the MaxCut problem

    The binary variable x_n is 1 if node n is assigned to the first partition and 0 if to the second partition.
    (currently, ConstrainedObjective does only support PolyBinary objectives and ConstraintBinary)

    this class is only for demonstration purpose, use MaxCutObjective for productive experiments
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        weights = instance.get_weights()

        # 0.5 * (sum_[(n, m) in Edges] w_n_m * ((2x_n - 1) * (2x_m - 1) - 1) )
        return 0.5 * sum(weights.get(edge, 1) * (PolyBinary({edge: 4, edge[:1] : -2, edge[1:] : -2}))
                         for edge in instance.graph.edges())

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        # there are no further constraints
        return {}

    @staticmethod
    def get_cut(raw_solution):
        """ get the cut from the variable assignment of the solution """
        return {tuple(sorted(var for var, value in raw_solution.items() if value == 1)),
                tuple(sorted(var for var, value in raw_solution.items() if value == 0))}


BOTH_0 = "both_0"
BOTH_1 = "both_1"

class MaxCutConstrainedObjectiveLinear(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the MaxCut problem
    with linearized constraints and therefore additional variables

    The binary variable x_n is 1 if node n is assigned to the first partition and 0 if to the second partition.
    The binary variable y_n_m is 1 if edge (n,m) is in the cut and 0 otherwise.

    this class is only for demonstration purpose, use MaxCutObjective for productive experiments
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        weights = instance.get_weights()

        # - (sum_[(n, m) in Edges] w_n_m * y_n_m
        return -1 * PolyBinary({(('y', *edge),): weights.get(edge, 1) for edge in instance.graph.edges()})

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        constraints = {}

        for edge in instance.graph.edges():
            poly = PolyBinary({(('y', *edge),): -1, (('x', edge[0]),): 1, (('x', edge[1]),): 1})
            constraints[BOTH_0 + f"_{edge}"] = ConstraintBinary(poly, 0, 2)

            poly = PolyBinary({(('y', *edge),): 1, (('x', edge[0]),): 1, (('x', edge[1]),): 1})
            constraints[BOTH_1 + f"_{edge}"] = ConstraintBinary(poly, 0, 2)

        return constraints

    @staticmethod
    def get_cut(raw_solution):
        """ get the cut from the variable assignment of the solution """
        return {tuple(sorted(var[1] for var, value in raw_solution.items() if var[0] == "x" and value == 1)),
                tuple(sorted(var[1] for var, value in raw_solution.items() if var[0] == "x" and value == 0))}
