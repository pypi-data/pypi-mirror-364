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

""" module for demonstrating the classical solving of the PrimeFactorization problem """

import pytest

from quark import ScipModel

from quapps.prime_factorization import PFInstance, PFConstrainedObjectiveTable
from quapps.prime_factorization.test_pf_constrained_objective import get_example_constrained_objective_simple, \
    get_example_constrained_objective_table, PRIME1, PRIME2


@pytest.mark.parametrize("get_example_func", [get_example_constrained_objective_simple,
                                              get_example_constrained_objective_table])
def test_solution_of_constrained_objective(get_example_func):
    """ test if solution of objective_constrained is correct """
    pf_constrained_objective = get_example_func()
    model = ScipModel.get_from_constrained_objective(pf_constrained_objective)
    solution = model.solve()

    assert set(solution.items()) >= set({(PRIME1, 1): 1, (PRIME1, 2): 0, (PRIME1, 3): 1,
                                         (PRIME2, 1): 1, (PRIME2, 2): 0, (PRIME2, 3): 1}.items())

    extracted_solution = pf_constrained_objective.get_prime_factors(solution)
    assert extracted_solution == {PRIME1 : 11, PRIME2: 11}

def test_big():
    """ test a bigger instance """
    pf_instance = PFInstance(product=48567227, bit_length1=14)

    with pytest.warns(UserWarning, match=r"The two variables '\('prime1', 1\)' and '\('prime2', 1\)' are set to "
                                         r"be negations of each other, consider replacing one with '1 - other'"):
        pf_constrained_objective = PFConstrainedObjectiveTable.get_from_instance(pf_instance)

    model = ScipModel.get_from_constrained_objective(pf_constrained_objective)
    solution = model.solve()
    assert pf_constrained_objective.get_prime_factors(solution) == {PRIME1: 6133, PRIME2: 7919}
