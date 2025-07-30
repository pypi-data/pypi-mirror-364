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

""" module for the PrimeFactorization ConstrainedObjective """

import math
from abc import ABC

from quark import ConstrainedObjective, PolyBinary, ConstraintBinary
from quark.polynomial import is_constant

from .utils_table_str import get_table_str

PRIME1 = "prime1"
PRIME2 = "prime2"
PRODUCT = "product"
COLUMN_PRODUCT = "column_product_{}"
CARRY = "carry"


class _PFConstrainedObjectiveBase(ConstrainedObjective, ABC):
    """
    base implementation of the objective and the constraints for the PrimeFactorization problem
    """
    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
        # there is no actual objective
        return PolyBinary()

    @staticmethod
    def get_prime_factors(raw_solution):
        """ extract the actual solution from the variable assignment  """
        # assert raw_solution.objective_value == 0
        # decode the binary encoding of the prime factors
        prime1 = sum(value * 2 ** var[1] for var, value in raw_solution.items() if var[0] == PRIME1) + 1
        prime2 = sum(value * 2 ** var[1] for var, value in raw_solution.items() if var[0] == PRIME2) + 1
        return {PRIME1: prime1, PRIME2: prime2}


class PFConstrainedObjectiveSimple(_PFConstrainedObjectiveBase):
    """
    implementation of the objective and the constraints for the PrimeFactorization problem
    using simple multiplication

    the factors are simply in binary encoding and multiplied to give a single constraint (with N =! x*y)
    """

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        # the product of the primes should be equal to the product
        poly_prime1 = get_binary_polynomial(instance.bit_length1, PRIME1)
        poly_prime2 = get_binary_polynomial(instance.bit_length2, PRIME2)
        constraint = ConstraintBinary(poly_prime1 * poly_prime2, instance.product, instance.product)
        return {PRODUCT : constraint}


class PFConstrainedObjectiveTable(_PFConstrainedObjectiveBase):
    """
    implementation of the objective and the constraints for the PrimeFactorization problem
    using the multiplication table
    """

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        column_polys = {column : -bit for column, bit in enumerate(instance.product_bits) if column > 0}
        for column in range(1, instance.bit_length_product):
            column_polys[column] += get_column_sum(column, instance.bit_length1, instance.bit_length2)
            _add_carry(column_polys, column, instance.product_bits)

        return {get_column_name(column, instance.bit_length_product): ConstraintBinary(poly, 0, 0)
                for column, poly in column_polys.items()}

    def preprocess(self, new_name=None):
        """ set variables in advance for which the values are given by the constraint structure """
        # due to the structure of the problem, the preprocessing can be done here straightforwardly
        preprocessable = get_all_preprocessable_variables(self)
        if not preprocessable:
            return self, {}

        constraints = {name: constraint.copy() for name, constraint in self.items()}
        preprocessed = {}
        while preprocessable:
            for constraint in constraints.values():
                evaluated = constraint.polynomial.evaluate(preprocessable, keep_poly=True)
                constraint.polynomial = PolyBinary(evaluated).remove_zero_coefficients()
            preprocessed.update(preprocessable)
            constraints = {name: constraint for name, constraint in constraints.items()
                           if not is_constant(constraint.polynomial)}
            preprocessable = get_all_preprocessable_variables(constraints)

        return self.__class__(self.objective_poly, constraints, new_name or self.name), preprocessed

    def get_table_str(self):
        """ get the table representation of the constraints as a string """
        variables = self.get_all_variables()
        bit_length1 = max(var[1] for var in variables if var[0] == PRIME1)
        bit_length2 = max(var[1] for var in variables if var[0] == PRIME2)
        return get_table_str(bit_length1, bit_length2, self.values())


def get_binary_polynomial(bit_length, variable_name):
    """ get a polynomial representing the binary representation of a number with the given bit length """
    return PolyBinary({((variable_name, i),): 2 ** i for i in range(1, bit_length)}) + 1

def get_column_sum(column, bit_length1, bit_length2):
    """ get the sum of all monomials in a column of the multiplication table """
    rows = range(max(column - bit_length1 + 1, 0), min(bit_length2, column + 1))
    return PolyBinary({get_multiplication_table_variables_at(column, row): 1 for row in rows})

def get_multiplication_table_variables_at(column, row):
    """ get the variables of the monomial at the specific row and column of the multiplication table """
    bit_prime1, bit_prime2 = column - row, row
    if bit_prime2 == 0:
        return ((PRIME1, bit_prime1),)
    if bit_prime1 == 0:
        return ((PRIME2, bit_prime2),)
    return (PRIME1, bit_prime1), (PRIME2, bit_prime2)

def _add_carry(column_polys, column, product_bits):
    """
    according to the number of already collected summands we might need to introduce carry variables
    those catch if the sum might exceed 2, resp. higher powers of 2, and thus need to be added in later columns
    """
    number_summands = len(column_polys[column]) - 1 - product_bits[column]
    if number_summands > 0:
        lg = int(math.floor(math.log(number_summands, 2)))
        for i_carry in range(lg):
            if column + i_carry + 1 < len(product_bits):
                column_polys[column] -= PolyBinary({((CARRY, column, i_carry),): 2 ** (i_carry + 1)})
                column_polys[column + i_carry + 1] += PolyBinary({((CARRY, column, i_carry),): 1})

def get_all_preprocessable_variables(constraints):
    """ get the variables of all constraints that can be preprocessed """
    preprocessable = {}
    for constraint in constraints.values():
        preprocessable.update(constraint.get_preprocessable_variables())
    return preprocessable

def get_column_name(column, total_len):
    """ get the name of the column """
    str_format = f"0{len(str(total_len))}d"
    column_index_str = f"{column:{str_format}}"
    return COLUMN_PRODUCT.format(column_index_str)
