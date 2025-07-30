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

""" module for testing the FlightGateAssignment ConstrainedObjective """

from quark import PolyBinary

from quapps.min_k_union.mku_constrained_objective import USE_K_SUBSETS, ELEMENT_IN_SUBSET
from quapps.min_k_union.test_mku_instance import get_example_instance


EXPECTED_OBJECTIVE_POLY = PolyBinary({(('e', 1),): 1, (('e', 2),): 1, (('e', 3),): 1, (('e', 4),): 1})

def get_example_constrained_objective(mku_instance=None):
    """ construct example constrained_objective """
    if not mku_instance:
        mku_instance = get_example_instance()
    return mku_instance.get_constrained_objective()


def test_constrained_objective_creation():
    """ test constrained_objective creation """
    mku_constrained_objective = get_example_constrained_objective()
    assert mku_constrained_objective.objective_poly == EXPECTED_OBJECTIVE_POLY
    assert len(mku_constrained_objective) == 15

    expected_poly = PolyBinary({(('s', '(1, 2)'),):    1,
                                (('s', '(1, 2, 4)'),): 1,
                                (('s', '(1,)'),):      1,
                                (('s', '(2, 3, 4)'),): 1,
                                (('s', '(2, 4)'),):    1,
                                (('s', '(2,)'),):      1,
                                (('s', '(3,)'),):      1,
                                (('s', '(4,)'),):      1})
    assert mku_constrained_objective[USE_K_SUBSETS].polynomial == expected_poly
    assert mku_constrained_objective[USE_K_SUBSETS].upper_bound == 3
    assert mku_constrained_objective[USE_K_SUBSETS].lower_bound == 3

    const_name = ELEMENT_IN_SUBSET + "_2_(1, 2, 4)"
    expected_poly = PolyBinary({(('e', 2),): 1,
                                (('s', '(1, 2, 4)'),): -1})
    assert mku_constrained_objective[const_name].polynomial == expected_poly
    assert mku_constrained_objective[const_name].upper_bound == 1
    assert mku_constrained_objective[const_name].lower_bound == 0
