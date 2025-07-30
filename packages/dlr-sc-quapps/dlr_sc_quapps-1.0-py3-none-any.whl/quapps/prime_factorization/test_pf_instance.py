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

""" module for testing the PrimeFactorization Instance """

import os
import pytest
import sympy.core.random

from quapps.prime_factorization import PFInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"


def get_example_instance():
    """ construct example instance """
    return PFInstance(11, 11)


def test_init():
    """ test initialization of instance """
    pf_instance = get_example_instance()
    assert pf_instance.bit_length1 == 4
    assert pf_instance.bit_length2 == 4
    assert pf_instance.bit_length_product == 7
    assert pf_instance.product == 121
    assert pf_instance.product_bits == [1, 0, 0, 1, 1, 1, 1]

    pf_instance = PFInstance(product=21, bit_length1=3)
    assert pf_instance.bit_length1 == 3
    assert pf_instance.bit_length2 == 3
    assert pf_instance.bit_length_product == 5
    assert pf_instance.product == 21
    assert pf_instance.product_bits == [1, 0, 1, 0, 1]

def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="Either provide the two prime factors or the product and the bit length"):
        PFInstance(prime2=3, product=9)
    with pytest.raises(ValueError, match="The first factor should be prime"):
        PFInstance(prime1=4, prime2=7)
    with pytest.raises(ValueError, match="The second factor should be prime"):
        PFInstance(prime1=7, prime2=4)
    with pytest.raises(ValueError, match="The product should not be prime"):
        PFInstance(product=11, bit_length1=2)
    with pytest.raises(ValueError, match="The bit_length1 should be an integer larger than 1"):
        PFInstance(product=12, bit_length1=1)
    with pytest.raises(ValueError, match="The bit_length2 should be an integer larger than 1"):
        PFInstance(product=4, bit_length1=3)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "PFInstance_prime1_011_prime2_011"

    instance = PFInstance(product=121, bit_length1=4)
    assert instance.get_name(digits=5) == "PFInstance_product_00121_bit_length1_04"

def test_io():
    """ test read and write of instance """
    pf_instance = get_example_instance()
    pf_instance.save_hdf5(FILENAME_TMP)
    loaded = PFInstance.load_hdf5(FILENAME_TMP)

    assert loaded.prime1 == pf_instance.prime1
    assert loaded.prime2 == pf_instance.prime2
    assert loaded.product == pf_instance.product
    assert loaded.bit_length1 == pf_instance.bit_length1
    assert loaded.bit_length2 == pf_instance.bit_length2
    assert loaded.bit_length_product == pf_instance.bit_length_product
    assert loaded.product_bits == pf_instance.product_bits

    os.remove(FILENAME_TMP)

def test_get_random():
    """ test random instance """
    pf_instance = PFInstance.get_random(4, 5)
    assert pf_instance.prime1 in range(8, 16)
    assert pf_instance.prime2 in range(16, 32)
    assert pf_instance.bit_length_product in [8, 9]

    sympy.core.random.seed(1)
    pf_instance = PFInstance.get_random(7, 7)
    print(pf_instance.get_name())
    assert pf_instance.prime1 in range(64, 128)
    assert pf_instance.prime2 in range(64, 128)
    assert pf_instance.bit_length_product in [13, 14]
