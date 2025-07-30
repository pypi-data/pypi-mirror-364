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

""" module for testing the Knapsack ConstrainedObjective """

from quark import PolyBinary, ConstraintBinary
from quark.constrained_objective import ConstrainedObjective

from quapps.knapsack.test_knapsack_instance import get_example_instance

X = "x"
WEIGHT_BELOW_CAPACITY = "weight_below_capacity"

EXPECTED_OBJECTIVE_POLY = PolyBinary({((X, "A"),): -3, ((X, "B"),): -4, ((X, "C"),): -5,
                                      ((X, "D"),): -2, ((X, "E"),): -5, ((X, "F"),): -5})


def get_example_constrained_objective():
    """ construct example constrained_objective """
    knapsack_instance = get_example_instance()
    return knapsack_instance.get_constrained_objective()


def test_constrained_objective_creation():
    """ test constrained_objective creation """
    knapsack_constrained_objective = get_example_constrained_objective()

    constraint_poly = PolyBinary({((X, "A"),): 1, ((X, "B"),): 1, ((X, "C"),): 9,
                                 ((X, "D"),): 6, ((X, "E"),): 3, ((X, "F"),): 5})
    constraints = {WEIGHT_BELOW_CAPACITY: ConstraintBinary(constraint_poly, 0, 11)}
    expected_constrained_objective = ConstrainedObjective(EXPECTED_OBJECTIVE_POLY, constraints)

    assert knapsack_constrained_objective == expected_constrained_objective
