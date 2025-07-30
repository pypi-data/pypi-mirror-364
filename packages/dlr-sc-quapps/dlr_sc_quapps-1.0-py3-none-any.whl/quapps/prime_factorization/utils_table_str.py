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

""" module for the PrimeFactorization ConstrainedObjective table representation utils """

import numpy as np

from quark import PolyBinary


PRODUCT   = "product"
POS_CARRY = "pos_carry"
NEG_CARRY = "neg_carry"
CONSTANT  = "constant"
STR       = "str"
CARRY     = "carry"
PRIME1    = "prime1"
PRIME2    = "prime2"
C         = "c"
P         = "p"
Q         = "q"


def get_table_str(bit_length1, bit_length2, constraints):
    """
    get the table representation of the constraints as a string

    :param bit_length1: the bit length of the first prime factor
    :param bit_length2: the bit length of the second prime factor
    :param constraints: the constraints to be represented
    :return: a nice str representation of the constraints as a table
    """
    cols_parts = _get_table_cols_parts(constraints, bit_length1, bit_length2)
    max_lengths = _get_max_lengths(cols_parts, bit_length1)
    cols = _combine_to_table_cols(cols_parts, bit_length1, bit_length2, max_lengths)
    full_str = _combine_to_full_table_str(cols, bit_length2, max_lengths)
    return full_str

def _get_table_cols_parts(constraints, bit_length1, bit_length2):
    # due to restriction to primes larger than 2 we could set the 0th bit of both primes to one
    # and therefore the last column is trivial
    last_col = {PRODUCT: ["+1"], POS_CARRY: [], NEG_CARRY: [], CONSTANT: ["-1"]}
    # to fill up the table we might need empty columns
    empty_col = {PRODUCT: [], POS_CARRY: [], NEG_CARRY: [], CONSTANT: []}
    # get the column parts for all constraints
    cols = [last_col, *(_get_table_col_parts(constraint) for constraint in constraints)]
    # add the empty ones according to the length of the headline
    cols += [empty_col] * (bit_length1 + bit_length2 + 2 - len(cols))
    return cols

def _get_table_col_parts(constraint):
    # extract the separate monomial strings
    col = [str(PolyBinary({var_tuple: value})) for var_tuple, value in constraint.polynomial.items()]
    # replace the long variable names with shorter ones
    col = [monomial.replace(CARRY, C).replace(PRIME2, Q).replace(PRIME1, P) for monomial in col[::-1]]
    # divide the monomials into the different parts
    return {PRODUCT:   [monomial for monomial in col if P in monomial or Q in monomial],
            POS_CARRY: [monomial for monomial in col if C in monomial and '+' in monomial],
            NEG_CARRY: [monomial for monomial in col if C in monomial and '-' in monomial],
            CONSTANT:  [monomial for monomial in col if not any(x in monomial for x in [C, P, Q])] or ['0']}

def _get_max_lengths(cols, bit_length1):
    # we need several lengths to have a nice looking table
    max_lengths = {STR: 0, PRODUCT: bit_length1 + 1, POS_CARRY: 0, NEG_CARRY: 0, CONSTANT: 0}
    for col_parts in cols:
        for name, part in col_parts.items():
            # for each single part we have a separate section
            max_lengths[name] = max(max_lengths[name], len(part))
            # and we need the length of the longest entry for column width
            max_lengths[STR] = max(max_lengths[STR], 0, *(len(s) for s in part))
    return max_lengths

def _combine_to_table_cols(cols_parts, bit_length1, bit_length2, max_lens):
    # the product of the bits in the headline
    head = [*(f"{P}_{i}" for i in range(bit_length1, 0, -1)), "1",
            *(f"{Q}_{i}" for i in range(bit_length2, 0, -1)), "1"]
    cols = []
    for i, col_parts in enumerate(cols_parts[::-1]):
        # add the corresponding part of the headline to the column
        col = [head[i], '=' * max_lens[STR]]
        for name, part in col_parts.items():
            # fill up each part with empty entries
            empty_rows = [""] * (max_lens[name] - len(part))
            # in the main part we switch whether we put the empty entries above or below for the diagonal structure
            new_part = (empty_rows + part) if name == PRODUCT and i <= bit_length1 else (part + empty_rows)
            col += new_part + ['-' * max_lens[STR]]
        cols.append(col)
    return cols

def _combine_to_full_table_str(cols, bit_length2, max_lens):
    # extend each entry to the full maximal length
    cols = [[" " * (max_lens[STR] - len(x)) + x for x in col] for i, col in enumerate(cols)]
    # add the multiplication sign in the headline
    cols[len(cols) - bit_length2 - 1][0] = '*' + cols[len(cols) - bit_length2 - 1][0][1:]
    # combine the entries to a full string with the corresponding separation symbols
    full_str = '\n'.join('|'.join(row) for row in np.array(cols).transpose()[:-1])
    return full_str
