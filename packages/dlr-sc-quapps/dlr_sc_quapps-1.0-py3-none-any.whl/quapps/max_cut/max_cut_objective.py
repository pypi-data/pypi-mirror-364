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

""" module for the MaxCut Objective """

from quark import Objective, PolyIsing


class MaxCutObjective(Objective):
    """
    implementation of the objective for the MaxCut problem

    use this class for productive experiments
    """

    @staticmethod
    def _get_polynomial(instance):
        weights = instance.get_weights()

        # 0.5 * (sum_[(n, m) in Edges] w_n_m * (s_n * s_m - 1))
        objective_poly = PolyIsing({edge: weights.get(edge, 1) for edge in instance.graph.edges()})
        objective_poly -= sum(weights.values()) if weights else len(instance.graph.edges())
        return objective_poly * 0.5

    @staticmethod
    def get_cut(raw_solution):
        """ get the cut from the variable assignment of the solution """
        return {tuple(sorted(var for var, value in raw_solution.items() if value == 1)),
                tuple(sorted(var for var, value in raw_solution.items() if value == -1))}
