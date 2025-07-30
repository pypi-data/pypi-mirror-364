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

""" module for testing the PrimeFactorization ConstrainedObjective """

import pytest

from quark import PolyBinary, ConstraintBinary, Polynomial

from quapps.prime_factorization import PFInstance, PFConstrainedObjectiveSimple
from quapps.prime_factorization.pf_constrained_objective import PRODUCT, COLUMN_PRODUCT, PRIME1, PRIME2, CARRY
from quapps.prime_factorization.test_pf_instance import get_example_instance


REDUCTION = "reduction"

def get_example_constrained_objective_simple():
    """ construct example constrained objective """
    pf_instance = get_example_instance()
    return PFConstrainedObjectiveSimple.get_from_instance(pf_instance)

def get_example_constrained_objective_table():
    """ construct example constrained objective """
    pf_instance = get_example_instance()
    return pf_instance.get_constrained_objective()


EXPECTED_POLY_SIMPLE = PolyBinary({(): 1,
                                   ((PRIME1, 1),): 2,
                                   ((PRIME1, 2),): 4,
                                   ((PRIME1, 3),): 8,
                                   ((PRIME2, 1),): 2,
                                   ((PRIME2, 2),): 4,
                                   ((PRIME2, 3),): 8,
                                   ((PRIME1, 1), (PRIME2, 1)): 4,
                                   ((PRIME1, 1), (PRIME2, 2)): 8,
                                   ((PRIME1, 1), (PRIME2, 3)): 16,
                                   ((PRIME1, 2), (PRIME2, 1)): 8,
                                   ((PRIME1, 2), (PRIME2, 2)): 16,
                                   ((PRIME1, 2), (PRIME2, 3)): 32,
                                   ((PRIME1, 3), (PRIME2, 1)): 16,
                                   ((PRIME1, 3), (PRIME2, 2)): 32,
                                   ((PRIME1, 3), (PRIME2, 3)): 64})

def test_constrained_objective_creation_simple():
    """ test constrained objective creation """
    pf_constrained_objective = get_example_constrained_objective_simple()
    assert len(pf_constrained_objective) == 1
    assert pf_constrained_objective[PRODUCT] == ConstraintBinary(EXPECTED_POLY_SIMPLE, 121, 121)
    assert pf_constrained_objective.objective_poly == PolyBinary()


EXPECTED_POLYS_TABLE = [PolyBinary({(): 0,
                                    ((CARRY, 1, 0),): -2,
                                    ((PRIME1, 1),): 1,
                                    ((PRIME2, 1),): 1}),
                        PolyBinary({(): 0,
                                    ((CARRY, 1, 0),): 1,
                                    ((CARRY, 2, 0),): -2,
                                    ((CARRY, 2, 1),): -4,
                                    ((PRIME1, 2),): 1,
                                    ((PRIME2, 2),): 1,
                                    ((PRIME1, 1), (PRIME2, 1)): 1}),
                        PolyBinary({(): -1,
                                    ((CARRY, 2, 0),): 1,
                                    ((CARRY, 3, 0),): -2,
                                    ((CARRY, 3, 1),): -4,
                                    ((PRIME1, 3),): 1,
                                    ((PRIME2, 3),): 1,
                                    ((PRIME1, 1), (PRIME2, 2)): 1,
                                    ((PRIME1, 2), (PRIME2, 1)): 1}),
                        PolyBinary({(): -1,
                                    ((CARRY, 2, 1),): 1,
                                    ((CARRY, 3, 0),): 1,
                                    ((CARRY, 4, 0),): -2,
                                    ((CARRY, 4, 1),): -4,
                                    ((PRIME1, 1), (PRIME2, 3)): 1,
                                    ((PRIME1, 2), (PRIME2, 2)): 1,
                                    ((PRIME1, 3), (PRIME2, 1)): 1}),
                        PolyBinary({(): -1,
                                    ((CARRY, 3, 1),): 1,
                                    ((CARRY, 4, 0),): 1,
                                    ((CARRY, 5, 0),): -2,
                                    ((PRIME1, 2), (PRIME2, 3)): 1,
                                    ((PRIME1, 3), (PRIME2, 2)): 1}),
                        PolyBinary({(): -1,
                                    ((CARRY, 4, 1),): 1,
                                    ((CARRY, 5, 0),): 1,
                                    ((PRIME1, 3), (PRIME2, 3)): 1})]

def test_constrained_objective_creation_table():
    """ test constrained objective creation """
    pf_constrained_objective = get_example_constrained_objective_table()
    assert len(pf_constrained_objective) == 6
    for column in range(6):
        name = COLUMN_PRODUCT.format(column + 1)
        assert pf_constrained_objective[name] == ConstraintBinary(EXPECTED_POLYS_TABLE[column], 0, 0)
    assert pf_constrained_objective.objective_poly == PolyBinary()


EXPECTED_POLYS_OBJ_TERMS = {PRODUCT : PolyBinary({(): 64,
                                                  ((PRIME1, 1),): -28,
                                                  ((PRIME2, 1),): -28,
                                                  ((REDUCTION, PRIME1, 1, PRIME2, 1),): -48,
                                                  ((PRIME1, 1), (PRIME2, 1)): 8,
                                                  ((PRIME1, 1), (REDUCTION, PRIME1, 1, PRIME2, 1)): 16,
                                                  ((PRIME2, 1), (REDUCTION, PRIME1, 1, PRIME2, 1)): 16}),
                            REDUCTION : PolyBinary({((REDUCTION, PRIME1, 1, PRIME2, 1),): 3,
                                                    ((PRIME1, 1), (PRIME2, 1)): 1,
                                                    ((PRIME1, 1), (REDUCTION, PRIME1, 1, PRIME2, 1)): -2,
                                                    ((PRIME2, 1), (REDUCTION, PRIME1, 1, PRIME2, 1)): -2})}

def test_objective_terms_creation():
    """ test objective_terms creation via the constrained_objective """
    pf_instance = PFInstance(3, 3)
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: "
                                         r"\{\('prime1', 1\): 1, \('prime2', 1\): 1\}"):
        pf_constrained_objective = PFConstrainedObjectiveSimple.get_from_instance(pf_instance)
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('prime1', 1\): 1, \('prime2', 1\): 1,"
                                         r" \('reduction', 'prime1', 1, 'prime2', 1\): 1\}"):
        pf_objective_terms = pf_constrained_objective.get_objective_terms()
    assert dict(pf_objective_terms) == EXPECTED_POLYS_OBJ_TERMS

def test_preprocess():
    """ test the preprocessing of the constrained objective """
    pf_instance = PFInstance(3, 7)
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('carry', 3, 0\): 1\}"):
        pf_constrained_objective = pf_instance.get_constrained_objective()
    with pytest.warns(UserWarning, match="There is nothing in this ConstrainedObjective"):
        new_pf_constrained_objective, preprocessed = pf_constrained_objective.preprocess()
    assert not new_pf_constrained_objective
    assert preprocessed == {(CARRY, 3, 0): 1, (CARRY, 2, 0): 1, (PRIME1, 1): 1, (PRIME2, 2): 1,
                             (CARRY, 1, 0): 1, (PRIME2, 1): 1}
    assert pf_constrained_objective.get_prime_factors(preprocessed) == {PRIME1: 3, PRIME2: 7}

    # preprocessing with variable replacement
    pf_instance = PFInstance(11, 13)
    with pytest.warns(UserWarning, match="The two variables"):
        pf_constrained_objective = pf_instance.get_constrained_objective()
    new_pf_constrained_objective, preprocessed = pf_constrained_objective.preprocess()
    assert preprocessed == {(CARRY, 6, 0): Polynomial({(): 1, ((CARRY, 5, 1),): -1}),
                            (PRIME2, 1): Polynomial({(): 1, ((PRIME1, 1),): -1})}

    poly_dicts = [{(): -1, ((CARRY, 2, 0),): -2, ((PRIME1, 2),): 1, ((PRIME2, 2),): 1},
                  {(): -1, ((CARRY, 2, 0),): 1, ((CARRY, 3, 0),): -2, ((CARRY, 3, 1),): -4, ((PRIME1, 2),): 1,
                   ((PRIME1, 3),): 1, ((PRIME2, 3),): 1, ((PRIME1, 1), (PRIME1, 2)): -1, ((PRIME1, 1), (PRIME2, 2)): 1},
                  {((CARRY, 3, 0),): 1, ((CARRY, 4, 0),): -2, ((CARRY, 4, 1),): -4, ((PRIME1, 3),): 1,
                   ((PRIME1, 1), (PRIME1, 3)): -1, ((PRIME1, 1), (PRIME2, 3)): 1, ((PRIME1, 2), (PRIME2, 2)): 1},
                  {((CARRY, 3, 1),): 1, ((CARRY, 4, 0),): 1, ((CARRY, 5, 0),): -2, ((CARRY, 5, 1),): -4,
                   ((PRIME1, 2), (PRIME2, 3)): 1, ((PRIME1, 3), (PRIME2, 2)): 1},
                  {(): -2, ((CARRY, 4, 1),): 1, ((CARRY, 5, 0),): 1, ((CARRY, 5, 1),): 2,((PRIME1, 3), (PRIME2, 3)): 1}]
    exp_constraints = {f'column_product_{i+2}': ConstraintBinary(PolyBinary(poly_dicts[i]), 0, 0) for i in range(5)}
    assert dict(new_pf_constrained_objective) == exp_constraints

    # nothing to preprocess
    pf_instance = PFInstance(11, 11)
    pf_constrained_objective = pf_instance.get_constrained_objective()
    new_pf_constrained_objective, preprocessed = pf_constrained_objective.preprocess()
    assert not preprocessed
    assert new_pf_constrained_objective == pf_constrained_objective

def test_get_table_str():
    """ test the table string representation """
    pf_instance = PFInstance(3, 7)
    with pytest.warns(UserWarning, match=r"Variables could be set in advance: \{\('carry', 3, 0\): 1\}"):
        pf_constrained_objective = pf_instance.get_constrained_objective()
    exp_str = "       p_1|         1|*      q_2|       q_1|         1\n" \
              "==========|==========|==========|==========|==========\n" \
              "          |          |    +1 q_2|    +1 q_1|        +1\n" \
              "          |+1 p_1 q_2|+1 p_1 q_1|    +1 p_1|          \n" \
              "----------|----------|----------|----------|----------\n" \
              "  +1 c_3_0|  +1 c_2_0|  +1 c_1_0|          |          \n" \
              "----------|----------|----------|----------|----------\n" \
              "          |  -2 c_3_0|  -2 c_2_0|  -2 c_1_0|          \n" \
              "----------|----------|----------|----------|----------\n" \
              "        -1|         0|        -1|         0|        -1"
    assert pf_constrained_objective.get_table_str() == exp_str
