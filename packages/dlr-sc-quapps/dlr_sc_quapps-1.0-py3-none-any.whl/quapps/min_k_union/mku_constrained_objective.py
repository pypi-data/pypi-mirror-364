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

""" module for the MinKUnion ConstrainedObjective """

from ast import literal_eval

from quark import PolyBinary, ConstraintBinary, ConstrainedObjective


E = "e"
S = "s"
COUNT_ELEMENTS = "count_elements"
USE_K_SUBSETS = "use_k_subsets"
ELEMENT_IN_SUBSET = "element_in_subset"


class MKUConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the MinKUnion problem

    The binary variable x_e is 1 if element e is in a subset that is used, 0 otherwise,
    the binary variable y_s is 1 if the subset s is a subset that is used, 0 otherwise
    """

    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        return PolyBinary({((E, element),): 1 for element in instance.all_elements})

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        constraints = {}

        poly = PolyBinary({((S, str(subset)),): 1 for subset in instance.subsets})
        constraints[USE_K_SUBSETS] = ConstraintBinary(poly, instance.k, instance.k)

        for subset in instance.subsets:
            for element in subset:
                poly = PolyBinary({((E, element),): 1, ((S, str(subset)),): -1})
                constraints[ELEMENT_IN_SUBSET + f"_{element}_{subset}"] = ConstraintBinary(poly, 0, 1)

        return constraints

    def get_objective_terms(self, objective_name=COUNT_ELEMENTS, combine_prefixes=(ELEMENT_IN_SUBSET,), name=None,
                            reduction_strategy=None, check_special_constraints=True):
        """ overwrite ConstrainedObjective.get_objective_terms to set different default values """
        return super().get_objective_terms(objective_name, combine_prefixes, name, reduction_strategy,
                                           check_special_constraints)

    @staticmethod
    def get_subsets(raw_solution):
        """ extract the actual solution from the variable assignment """
        return {literal_eval(variable[1])
                for variable, value in raw_solution.items() if value == 1 and variable[0] == S}
