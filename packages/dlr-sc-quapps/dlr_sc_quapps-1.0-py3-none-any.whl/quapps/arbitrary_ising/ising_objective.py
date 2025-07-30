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

""" module for the Ising Objective """

from quark import Objective, PolyIsing


class IsingObjective(Objective):
    """ implementation of the objective for the Ising problem """

    @staticmethod
    def _get_polynomial(instance):
        """ get the polynomial from the instance data """
        # convert local fields and coupling matrix to the objective polynomial (the single objective term here)
        num_spins = len(instance.local_fields)
        poly = PolyIsing(dict(enumerate(instance.local_fields)))
        poly += PolyIsing({(i, j): instance.couplings[i, j] for i in range(num_spins) for j in range(num_spins)})
        return poly
