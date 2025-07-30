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

""" module for the PrimeFactorization Instance """

import sympy

from quark.io import Instance, hdf5_attributes

from .pf_constrained_objective import PFConstrainedObjectiveTable


INPUT_ATTRS = ["prime1", "prime2", "product", "bit_length1"]
ATTRS = ["bit_length2", "bit_length_product", "product_bits"]

ERROR_INPUT   = "Either provide the two prime factors or the product and the bit length of the first factor"
ERROR_PREFIX  = "Instance is not consistent: "
ERROR_PRIME1  = "The first factor should be prime"
ERROR_PRIME2  = "The second factor should be prime"
ERROR_PRODUCT = "The product should not be prime"
ERROR_LENGTH1 = "The bit_length1 should be an integer larger than 1"
ERROR_LENGTH2 = "The bit_length2 should be an integer larger than 1"


class PFInstance(Instance):
    """ container for all data defining an instance of the PrimeFactorization problem """

    def __init__(self, prime1=None, prime2=None, product=None, bit_length1=None):
        """
        an instance contains

        :param (int) prime1: the first prime factor
        :param (int) prime2: the second prime factor
        :param (int) product: the product of the two prime factors
        :param (int) bit_length1: the bit_length of the first prime factor
        """
        if not ((prime1 and prime2) or (product and bit_length1)):
            raise ValueError(ERROR_INPUT)

        self.prime1 = prime1
        self.prime2 = prime2
        self.product = product or self.prime1 * self.prime2
        self.bit_length_product = self.product.bit_length()
        self.product_bits = [int(bit) for column, bit in enumerate(bin(self.product)[:1:-1])]
        self.bit_length1 = bit_length1 if not self.prime1 else self.prime1.bit_length()
        self.bit_length2 = self.bit_length_product-self.bit_length1+1 if not self.prime1 else self.prime2.bit_length()
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if self.prime1 and not sympy.isprime(self.prime1):
            raise ValueError(ERROR_PREFIX + ERROR_PRIME1)
        if self.prime2 and not sympy.isprime(self.prime2):
            raise ValueError(ERROR_PREFIX + ERROR_PRIME2)
        if sympy.isprime(self.product):
            raise ValueError(ERROR_PREFIX + ERROR_PRODUCT)
        if not (isinstance(self.bit_length1, int) and self.bit_length1 > 1):
            raise ValueError(ERROR_PREFIX + ERROR_LENGTH1)
        if not (isinstance(self.bit_length2, int) and self.bit_length2 > 1):
            raise ValueError(ERROR_PREFIX + ERROR_LENGTH2)

        # check calculated values
        assert not self.prime2 or self.prime2.bit_length() <= self.bit_length2
        assert self.bit_length_product >= self.bit_length1 + self.bit_length2 - 1
        assert self.bit_length_product == len(self.product_bits)

    def get_name(self, digits=3, digits_bit_length=2):
        """ get an expressive name representing the instance """
        if self.prime1 and self.prime2:
            return f"PFInstance_prime1_{self.prime1:0{digits}}" \
                             f"_prime2_{self.prime2:0{digits}}"
        return f"PFInstance_product_{self.product:0{digits}}" \
                         f"_bit_length1_{self.bit_length1:0{digits_bit_length}}"

    def get_constrained_objective(self, name=None):
        """ get the constrained objective object based on this instance data """
        return PFConstrainedObjectiveTable.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_attributes.write_attributes(group, self, *INPUT_ATTRS, *ATTRS)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        return {name : int(value) for name, value in hdf5_attributes.read_attributes(group, *INPUT_ATTRS).items()}

    @classmethod
    def get_random(cls, bit_length1, bit_length2=None):
        """
        produce random factors with the given bit lengths

        :param (int) bit_length1: the number of bits of the first factor
        :param (int or None) bit_length2: the number of bits of the second factor,
                                          by default equal to bit_length1
        """
        bit_length2 = bit_length2 or bit_length1
        prime1 = sympy.randprime(2**(bit_length1 - 1), 2**bit_length1)
        prime2 = sympy.randprime(2**(bit_length2 - 1), 2**bit_length2)
        if bit_length1 == bit_length2 and prime1 > prime2:
            prime1, prime2 = prime2, prime1
        return cls(prime1, prime2)
