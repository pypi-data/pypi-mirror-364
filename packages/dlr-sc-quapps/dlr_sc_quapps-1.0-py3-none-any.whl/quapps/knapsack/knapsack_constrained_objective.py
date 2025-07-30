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

""" module for the Knapsack ConstrainedObjective """

from math import isclose

from quark import ConstrainedObjective, PolyBinary, ConstraintBinary

X = "x"

KNAPSACK_VALUE = "knapsack_value"
WEIGHT_BELOW_CAPACITY = "weight_below_capacity"


class KnapsackConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the Knapsack problem

    The binary variable x_n is 1 if item n is included in the knapsack and 0 otherwise.
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # -sum_[n in names] v_n * x_n
        return PolyBinary({((X, name),): -value for name, (value, _) in instance.items.items()})

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        # sum_[n in names] w_n * x_n
        poly = PolyBinary({((X, name),): weight for name, (value, weight) in instance.items.items()})
        constraints = {WEIGHT_BELOW_CAPACITY: ConstraintBinary(poly, 0, instance.capacity)}

        return constraints

    def get_objective_terms(self, objective_name=KNAPSACK_VALUE, combine_prefixes=(), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """ overwrite ConstrainedObjective.get_objective_terms to set different default values """
        return super().get_objective_terms(objective_name, combine_prefixes, name, reduction_strategy,
                                           check_special_constraints)

    @staticmethod
    def get_items(raw_solution):
        """ extract the actual solution from the variable assignment """
        return {name for ((variable, name), value) in raw_solution.items() if isclose(value, 1) and variable == "x"}
