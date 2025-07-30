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

""" module for testing the Ising Instance """

import os
import pytest
import numpy as np

from quapps.arbitrary_ising import IsingInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"

LOCAL_FIELDS = np.array([1, 2, 3])
COUPLINGS = 0.5 * np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]])


def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="local_fields and couplings need to be numpy arrays"):
        # noinspection PyTypeChecker
        IsingInstance([], [])
    with pytest.raises(ValueError, match="local_fields have to be a 1d array"):
        IsingInstance(COUPLINGS, COUPLINGS)
    with pytest.raises(ValueError, match="couplings have to be a 2d array"):
        IsingInstance(LOCAL_FIELDS, LOCAL_FIELDS)
    with pytest.raises(ValueError, match="dimensions of the local_fields and couplings do not match"):
        IsingInstance(np.array([1, 2]), COUPLINGS)

def test_get_name():
    """ test name """
    ising_instance = IsingInstance(LOCAL_FIELDS, COUPLINGS)
    assert ising_instance.get_name() == "IsingInstance_spins_003_density_1.000"

    random_ising = IsingInstance.get_random(3, coupling_density=0.5)
    assert random_ising.get_name(digits_spins=1) == "IsingInstance_spins_3_density_0.667"
    assert random_ising.get_name(density_decimals=1) == "IsingInstance_spins_003_density_0.7"

def test_get_coupling_density():
    """ test recovery of density """
    ising_instance = IsingInstance(LOCAL_FIELDS, COUPLINGS)
    assert ising_instance.get_coupling_density() == 1

    random_ising = IsingInstance.get_random(10, coupling_density=0.6)
    assert random_ising.get_coupling_density() == 0.6

    random_ising = IsingInstance.get_random(3, coupling_density=0.5)
    assert random_ising.get_coupling_density() == 0.6666666666666666  # we round to integer number of couplings

    random_ising = IsingInstance.get_random(3, coupling_density=0.49)
    assert random_ising.get_coupling_density() == 0.3333333333333333  # we round to integer number of couplings

def test_io():
    """ test read and write of instance """
    ising_instance = IsingInstance(LOCAL_FIELDS, COUPLINGS)
    ising_instance.save_hdf5(FILENAME_TMP)
    loaded = IsingInstance.load_hdf5(FILENAME_TMP)

    assert np.array_equal(loaded.local_fields, ising_instance.local_fields)
    assert np.array_equal(loaded.couplings, ising_instance.couplings)

    os.remove(FILENAME_TMP)

def test_get_random():
    """ test random instance """
    random_ising = IsingInstance.get_random(3)
    assert random_ising.couplings.shape == (3,3)
    assert all(np.tril(random_ising.couplings).flatten() == 0)
    assert sum(random_ising.couplings.flatten() != 0) == 3

    random_ising = IsingInstance.get_random(3, coupling_density=0.6)
    assert random_ising.couplings.shape == (3,3)
    assert all(np.tril(random_ising.couplings).flatten() == 0)
    assert sum(random_ising.couplings.flatten() != 0) == 2  # only two couplings should be nonzero

def test_get_rounded():
    """ test random generator """
    couplings = np.array([[ 0. , 1.09441776, -0.58811007],
                          [ 0. , 0.        ,  0.31719341],
                          [ 0. , 0.        ,  0.        ]])
    local_fields = np.array([0.52726941, -2.34376273, 0.81624021])
    ising_instance = IsingInstance(local_fields, couplings)
    exp_couplings = [[ 0. , 1.09, -0.59],
                     [ 0. , 0.  ,  0.32],
                     [ 0. , 0.  ,  0.  ]]
    exp_local_fields = [0.53, -2.34, 0.82]

    rounded_instance = ising_instance.round(2)
    assert np.array_equal(rounded_instance.couplings, exp_couplings)
    assert np.array_equal(rounded_instance.local_fields, exp_local_fields)
