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

"""
module for the MinKUnion ConstrainedObjective

THIS IMPLEMENTATION ONLY SERVES AS AN EXAMPLE.
To run the MinKUnion problem productively, use the MKUConstrainedObjective.
"""

from quark import PolyBinary, ConstraintBinary, ObjectiveTerms


E, S = "e", "s"
COUNT_ELEMENTS = "count_elements"
USE_K_SUBSETS = "use_k_subsets"
ELEMENT_IN_SUBSET = "element_in_subset"


class MKUObjectiveTerms(ObjectiveTerms):
    """
    implementation of the objective terms for the MinKUnion problem

    The binary variable x_e is 1 if element e is in a subset that is used, 0 otherwise,
    the binary variable y_s is 1 if the subset s is a subset that is used, 0 otherwise

    nicer implementation of inequality constraints with use of logical table

    if 0 <= x_e - y_s [<= 1] is fulfilled:

        | value x_e | value y_s | fulfilled |
        |-------|-------|-------|
        |   0   |   0   |   1   |
        |   0   |   1   |   0   |
        |   1   |   0   |   1   |
        |   1   |   1   |   1   |

    reversely need penalty for ((NOT x_e) AND y_s)

    => penalty function p(x_e, y_s) = (1 - x_e) * y_s
    """

    @staticmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names
        """
        return [USE_K_SUBSETS, ELEMENT_IN_SUBSET]

    @staticmethod
    def _get_objective_terms(instance):
        """ get the objective terms from the instance data """
        # actual objective function
        objective_terms = {COUNT_ELEMENTS: PolyBinary({((E, element),): 1 for element in instance.all_elements})}

        # use k subsets
        poly = PolyBinary({((S, str(subset)),): 1 for subset in instance.subsets})
        constraint = ConstraintBinary(poly, instance.k, instance.k)
        objective_terms.update(constraint.get_penalty_terms(USE_K_SUBSETS))

        # element in subset
        objective_terms[ELEMENT_IN_SUBSET] = PolyBinary()
        for subset in instance.subsets:
            for element in subset:
                # penalty term (1 - x_e) * y_s
                poly = PolyBinary({((S, str(subset)),): 1, ((S, str(subset)),(E, element)): -1})
                objective_terms[ELEMENT_IN_SUBSET] += poly

        return objective_terms
