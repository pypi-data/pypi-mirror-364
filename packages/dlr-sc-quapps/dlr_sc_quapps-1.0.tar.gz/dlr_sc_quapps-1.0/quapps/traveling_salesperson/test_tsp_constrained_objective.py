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

""" module for testing the TravelingSalesperson ConstrainedObjective """

from quark import PolyBinary

from quapps.traveling_salesperson.test_tsp_instance import get_example_instance


X = 'x'
EXP_POLY_DICT = {((X, 'b', 1),): 8, ((X, 'b', 3),): 4,
                 ((X, 'c', 1),): 1, ((X, 'c', 3),): 2,
                 ((X, 'd', 1),): 1, ((X, 'd', 3),): 7,
                 ((X, 'b', 1), (X, 'c', 2)): 1, ((X, 'b', 2), (X, 'c', 1)): 4,
                 ((X, 'b', 1), (X, 'd', 2)): 6, ((X, 'b', 2), (X, 'd', 1)): 1,
                 ((X, 'c', 1), (X, 'd', 2)): 9, ((X, 'c', 2), (X, 'd', 1)): 5,
                 ((X, 'b', 2), (X, 'c', 3)): 1, ((X, 'b', 3), (X, 'c', 2)): 4,
                 ((X, 'b', 2), (X, 'd', 3)): 6, ((X, 'b', 3), (X, 'd', 2)): 1,
                 ((X, 'c', 2), (X, 'd', 3)): 9, ((X, 'c', 3), (X, 'd', 2)): 5}
EXPECTED_POLY = PolyBinary(EXP_POLY_DICT)


def get_example_constrained_objective():
    """ construct an example constrained objective """
    tsp_instance = get_example_instance()
    return tsp_instance.get_constrained_objective()


def test_constrained_objective_creation():
    """ test creation of the constrained objective function """
    tsp_constrained_objective = get_example_constrained_objective()

    assert tsp_constrained_objective.objective_poly == EXPECTED_POLY

    # 4-1 nodes to visit + 4-1 positions to fill
    assert len(tsp_constrained_objective) == 6

    for node in ['b', 'c', 'd']:
        const_name = f'visit_node_{node}'
        assert tsp_constrained_objective[const_name].upper_bound == 1
        assert tsp_constrained_objective[const_name].lower_bound == 1
        assert tsp_constrained_objective[const_name].polynomial == PolyBinary({((X, node, 1), ): 1,
                                                                               ((X, node, 2), ): 1,
                                                                               ((X, node, 3), ): 1})
    for i in range(1, 4):
        const_name = f'visit_position_{i}'
        assert tsp_constrained_objective[const_name].upper_bound == 1
        assert tsp_constrained_objective[const_name].lower_bound == 1
        assert tsp_constrained_objective[const_name].polynomial == PolyBinary({((X, 'b', i),): 1,
                                                                               ((X, 'c', i),): 1,
                                                                               ((X, 'd', i),): 1})

def test_get_tour():
    """ test getting the correct tour """
    tsp_constrained_objective = get_example_constrained_objective()
    solution = {('x', 'b', 1): 0, ('x', 'b', 2): 1, ('x', 'b', 3): 0,
                ('x', 'c', 1): 0, ('x', 'c', 2): 0, ('x', 'c', 3): 1,
                ('x', 'd', 1): 1, ('x', 'd', 2): 0, ('x', 'd', 3): 0}
    tour = tsp_constrained_objective.get_tour(solution, start_node="a")
    assert tour == ["a", "d", "b", "c", "a"]
