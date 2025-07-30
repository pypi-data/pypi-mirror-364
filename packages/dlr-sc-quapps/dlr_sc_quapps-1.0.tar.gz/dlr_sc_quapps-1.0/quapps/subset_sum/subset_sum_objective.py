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

""" module for the SubsetSum Objective """

from math import isclose

from quark import Objective, PolyBinary

X = "x"


class SubsetSumObjective(Objective):
    """ implementation of the objective for the SubsetSum problem """

    @staticmethod
    def _get_polynomial(instance):
        """ get the polynomial from the instance data """
        poly = PolyBinary({((X, i, number),): number for (i, number) in enumerate(instance.numbers)})
        poly -= instance.target_sum  # difference to target sum
        poly = poly * poly  # square the difference to get penalty term
        return poly

    @staticmethod
    def get_numbers(raw_solution):
        """ extract the actual solution from the variable assignment """
        indices_numbers = [i for ((variable, *i), value) in raw_solution.items() if isclose(value, 1) and variable == X]
        _, numbers = zip(*indices_numbers)  # indices of the numbers in the numbers list, actual numbers
        return numbers
