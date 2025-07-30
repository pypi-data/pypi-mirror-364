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

from quapps.min_k_union.mku_objective_terms import MKUObjectiveTerms
from quapps.min_k_union.mku_constrained_objective import USE_K_SUBSETS, ELEMENT_IN_SUBSET, COUNT_ELEMENTS
from quapps.min_k_union.test_mku_instance import get_example_instance


EXPECTED_OBJECTIVE_POLY = PolyBinary({(('e', 1),): 1, (('e', 2),): 1, (('e', 3),): 1, (('e', 4),): 1})

def get_example_objective_terms(mku_instance=None):
    """ construct example constrained_objective """
    if not mku_instance:
        mku_instance = get_example_instance()
    print(mku_instance.subsets)
    return MKUObjectiveTerms.get_from_instance(mku_instance)


def test_objective_terms_creation():
    """ test constrained_objective creation """
    mku_objective_terms = get_example_objective_terms()
    assert len(mku_objective_terms) == 3

    assert mku_objective_terms[COUNT_ELEMENTS] == EXPECTED_OBJECTIVE_POLY

    expected_poly = PolyBinary({(('s', '(1,)'     ),): 1,
                                (('s', '(1, 2)'   ),): 1,
                                (('s', '(1, 2, 4)'),): 1,
                                (('s', '(2,)'     ),): 1,
                                (('s', '(2, 3, 4)'),): 1,
                                (('s', '(2, 4)'   ),): 1,
                                (('s', '(3,)'     ),): 1,
                                (('s', '(4,)'     ),): 1,
                                ():                   -3})
    assert mku_objective_terms[USE_K_SUBSETS] == expected_poly * expected_poly

    expected_poly = PolyBinary({(('s', '(1, 2)'),):    2,
                                (('s', '(1, 2, 4)'),): 3,
                                (('s', '(1,)'),):      1,
                                (('s', '(2, 3, 4)'),): 3,
                                (('s', '(2, 4)'),):    2,
                                (('s', '(2,)'),):      1,
                                (('s', '(3,)'),):      1,
                                (('s', '(4,)'),):      1,
                                (('e', 1), ('s', '(1, 2)')):    -1,
                                (('e', 1), ('s', '(1, 2, 4)')): -1,
                                (('e', 1), ('s', '(1,)')):      -1,
                                (('e', 2), ('s', '(1, 2)')):    -1,
                                (('e', 2), ('s', '(1, 2, 4)')): -1,
                                (('e', 2), ('s', '(2, 3, 4)')): -1,
                                (('e', 2), ('s', '(2, 4)')):    -1,
                                (('e', 2), ('s', '(2,)')):      -1,
                                (('e', 3), ('s', '(2, 3, 4)')): -1,
                                (('e', 3), ('s', '(3,)')):      -1,
                                (('e', 4), ('s', '(1, 2, 4)')): -1,
                                (('e', 4), ('s', '(2, 3, 4)')): -1,
                                (('e', 4), ('s', '(2, 4)')):    -1,
                                (('e', 4), ('s', '(4,)')):      -1})
    assert mku_objective_terms[ELEMENT_IN_SUBSET] == expected_poly
