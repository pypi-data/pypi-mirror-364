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

""" module for testing the SubsetSum ConstrainedObjective """

from quark import PolyBinary, ConstraintBinary

from quapps.subset_sum.test_subset_sum_instance import get_example_instance
from quapps.subset_sum.subset_sum_constrained_objective import SubsetSumConstrainedObjective


X = "x"
EXPECTED_OBJECTIVE_POLY = PolyBinary({(("x", 0, 7),): -7,
                                      (("x", 1, 10),): -10,
                                      (("x", 2, 13),): -13,
                                      (("x", 3, 17),): -17,
                                      (("x", 4, 20),): -20,
                                      (("x", 5, 25),): -25,
                                      (("x", 6, 31),): -31,
                                      (("x", 7, 42),): -42})
EXPECTED_CONSTRAINT_POLY = PolyBinary({(("x", 0, 7),): 7,
                                       (("x", 1, 10),): 10,
                                       (("x", 2, 13),): 13,
                                       (("x", 3, 17),): 17,
                                       (("x", 4, 20),): 20,
                                       (("x", 5, 25),): 25,
                                       (("x", 6, 31),): 31,
                                       (("x", 7, 42),): 42})

def get_example_constrained_objective():
    """ construct example constrained_objective """
    return SubsetSumConstrainedObjective.get_from_instance(get_example_instance())


def test_constrained_objective_creation():
    """ test constrained_objective creation """
    ssp_constrained_objective = get_example_constrained_objective()
    exp_constraint = ConstraintBinary(EXPECTED_CONSTRAINT_POLY, 0, 87)
    exp_constraints = {"sum_below_target": exp_constraint}
    assert dict(ssp_constrained_objective) == exp_constraints
    assert ssp_constrained_objective.objective_poly == EXPECTED_OBJECTIVE_POLY
