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
module for the MaxCut ObjectiveTerms

THIS IMPLEMENTATION ONLY SERVES AS AN EXAMPLE.
To run the MaxCut problem productively, use the MaxCutObjective.
"""

from quark import ObjectiveTerms, PolyIsing


NUM_CUTS = "num_cuts"


class MaxCutObjectiveTerms(ObjectiveTerms):
    """
    implementation of the objective terms for the MaxCut problem

    this class is only for demonstration purpose, use MaxCutObjective for productive experiments
    """

    @staticmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names
        """
        # here there are no further constraints
        return []

    @staticmethod
    def _get_objective_terms(instance):
        """ get the objective terms from the instance data """
        weights = instance.get_weights()
        objective_terms = {NUM_CUTS: 0}

        # 0.5 * (sum_[(n, m) in Edges] w_n_m * (s_n * s_m - 1) )
        objective_terms[NUM_CUTS] += PolyIsing({edge: weights.get(edge, 1) for edge in instance.graph.edges()})
        objective_terms[NUM_CUTS] -= sum(weights.values()) if weights else len(instance.graph.edges())
        objective_terms[NUM_CUTS] *= 0.5
        return objective_terms
