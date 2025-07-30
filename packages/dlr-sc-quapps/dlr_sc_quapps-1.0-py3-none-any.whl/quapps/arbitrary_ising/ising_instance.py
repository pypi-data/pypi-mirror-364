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

""" module for the Ising Instance """

import numpy as np

from quark.io import Instance, hdf5_datasets

from .ising_objective import IsingObjective


DATASETS = ["local_fields", "couplings"]

ERROR_PREFIX       = "Instance is not consistent: "
ERROR_NUMPY_ARRAYS = "The local_fields and couplings need to be numpy arrays"
ERROR_LOCAL_FIELDS = "The local_fields have to be a 1d array"
ERROR_COUPLINGS    = "The couplings have to be a 2d array"
ERROR_DIMENSIONS   = "The dimensions of the local_fields and couplings do not match"


class IsingInstance(Instance):
    """
    container for all data defining an instance of the Ising problem,
    where an Ising model is defined with

            I(s) = sum_{i = 1}^n h_i s_i + sum_{i,j = 1}^n J_ij s_i s_j = h^T s + s^T J s

    note that
        - the matrix J does not need to be upper triangular but can be to save storage,
        - the diagonal entries of J introduce a constant
    """

    def __init__(self, local_fields, couplings):
        """
        an instance contains

        :param (np.ndarray) local_fields: the local field array with entries h_i of an Ising spin glass Hamiltonian
        :param (np.ndarray) couplings: the coupling matrix with entries J_ij of an Ising spin glass Hamiltonian
        """
        self.local_fields = local_fields
        self.couplings = couplings
        super().__init__()
        self.num_spins = self.local_fields.shape[0]

    def check_consistency(self):
        """ check if the data is consistent """
        if not isinstance(self.local_fields, np.ndarray) or not isinstance(self.couplings, np.ndarray):
            raise ValueError(ERROR_PREFIX + ERROR_NUMPY_ARRAYS)
        if len(self.local_fields.shape) != 1:
            raise ValueError(ERROR_PREFIX + ERROR_LOCAL_FIELDS)
        if len(self.couplings.shape) !=2:
            raise ValueError(ERROR_PREFIX + ERROR_COUPLINGS)
        if self.couplings.shape != (self.local_fields.shape[0], self.local_fields.shape[0]):
            raise ValueError(ERROR_PREFIX + ERROR_DIMENSIONS)

    def get_name(self, digits_spins=3, density_decimals=3):
        """ get an expressive name representing the instance """
        return f"IsingInstance_spins_{len(self.local_fields):0{digits_spins}}" \
                            f"_density_{round(self.get_coupling_density(), density_decimals):.{density_decimals}f}"

    def get_coupling_density(self):
        """ recover the density of the graph defined by nonzero elements in the coupling matrix """
        J_upper_triangular = np.triu(self.couplings, 1) + np.tril(self.couplings, -1).transpose()
        nonzero = sum(J_upper_triangular.flatten() != 0)
        return nonzero / (self.num_spins * (self.num_spins - 1)) * 2

    # pylint: disable=arguments-differ  # no other arguments are needed here to get the objective
    def get_objective(self, name=None):
        """ get the objective object based on this instance data """
        return IsingObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_datasets(group, self, *DATASETS)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        return hdf5_datasets.read_datasets(group, *DATASETS)

    @classmethod
    def get_random(cls, num_spins, coupling_density=1, random_generator=np.random.default_rng().standard_normal):
        """
        get an Ising model with a random upper triangular coupling matrix

        :param (int) num_spins: the size of the local field and coupling matrices
        :param (float) coupling_density: the density of the graph defined by nonzero elements in the coupling matrix
        :param random_generator: the random number generator function, by default normal gaussian distribution
        """
        local_fields = random_generator(num_spins)
        couplings = np.triu(random_generator((num_spins, num_spins)), 1)

        if coupling_density < 1:
            rng = np.random.default_rng()
            num_all_couplings = int(num_spins * (num_spins - 1) / 2)
            num_zero_couplings = num_all_couplings - round(coupling_density * num_all_couplings)
            zeros = rng.choice(list(zip(*np.triu_indices(num_spins, 1))), num_zero_couplings, replace=False)
            for indices in zeros:
                couplings[tuple(indices)] = 0
        return cls(local_fields, couplings)

    def round(self, decimals=2):
        """
        get the corresponding Ising model with rounded matrices

        :param (int or None) decimals: the number of decimals
        """
        return self.__class__(self.local_fields.round(decimals=decimals), self.couplings.round(decimals=decimals))
