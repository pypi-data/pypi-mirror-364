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

"""
module for the SubsetSum ConstrainedObjective

THIS IMPLEMENTATION ONLY SERVES AS AN EXAMPLE.
To run the SubsetSum problem productively, use the SubsetSumObjective.
"""

from quark import ConstrainedObjective, PolyBinary, ConstraintBinary

X = "x"

SUM_VALUE = "sum_value"
SUM_BELOW_TARGET = "sum_below_target"

class SubsetSumConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the SubsetSum problem

    The binary variable x_i is 1 if n_i is included in the set of summed numbers and 0 otherwise.
    """
    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # -sum_[i in 0..N-1] n_i * x_i
        return PolyBinary({((X, i, number),): -number for (i, number) in enumerate(instance.numbers)})

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        # sum_[i in 0..N-1] n_i * x_i
        poly = PolyBinary({((X, i, number),): number for (i, number) in enumerate(instance.numbers)})
        constraints = {SUM_BELOW_TARGET: ConstraintBinary(poly, None, instance.target_sum)}
        return constraints

    def get_objective_terms(self, objective_name=SUM_VALUE, combine_prefixes=(SUM_BELOW_TARGET,), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """ overwrite ConstrainedObjective.get_objective_terms to set different default values """
        return super().get_objective_terms(objective_name, combine_prefixes, name, reduction_strategy,
                                           check_special_constraints)
