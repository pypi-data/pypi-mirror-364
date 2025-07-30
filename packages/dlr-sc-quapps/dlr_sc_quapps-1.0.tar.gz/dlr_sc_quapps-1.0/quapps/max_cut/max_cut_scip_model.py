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
module for the MaxCut ScipModel

THIS IMPLEMENTATION SERVES AS AN EXAMPLE
how to directly implement a linearized version of the MaxCut problem in SCIP.
"""

from pyscipopt import quicksum

from quark import ScipModel


class MaxCutScipModel(ScipModel):
    """ additional exemplary implementation of the MaxCut problem as mixed-integer linear program in SCIP """

    def __init__(self, instance, name=None):
        """ initialize SCIP model from instance data """
        super().__init__(name or instance.get_name())

        # add variables
        ys = {edge: self.addVar(f"y_{edge[0]}_{edge[1]}", vtype="C", ub=1) for edge in instance.graph.edges()}
        xs = {node: self.addVar(f"x_{node}", vtype="B") for node in instance.graph.nodes()}
        self.data = xs

        # add objective function
        weights = instance.get_weights()
        objective = -1 * quicksum(weights.get(edge, 1) * ys[edge] for edge in instance.graph.edges())
        self.setObjective(objective)
        self.setMinimize()

        # add constraints
        for edge in instance.graph.edges():
            self.addCons(ys[edge] <= xs[edge[0]] + xs[edge[1]])
            self.addCons(ys[edge] <= 2 - xs[edge[0]] - xs[edge[1]])
