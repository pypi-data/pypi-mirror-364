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

""" module for the MinKUnion Instance """

import random

from quark.io import Instance, hdf5_attributes, hdf5_datasets

from .mku_constrained_objective import MKUConstrainedObjective


SUBSETS = "subsets"
K = "k"

ERROR_SUBSETS = "There are not enough subsets"
ERROR_RANDOM = "Cannot generate desired subsets"


class MKUInstance(Instance):
    """ container for all data defining an instance of the MinKUnion problem """

    def __init__(self, subsets, k):
        """
        an instance contains

        :param (list or set) subsets: a collection of subsets
        :param (int) k: the number of subsets to be taken
        """
        self.subsets = sorted(tuple(sorted(subset)) for subset in subsets)
        self.k = k
        self.all_elements = set(element for subset in self.subsets for element in subset)
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if self.k >= len(self.subsets):
            raise ValueError(ERROR_SUBSETS)

    def get_name(self, digits=3):
        """ get an expressive name representing the instance """
        max_subset_size = max(len(subset) for subset in self.subsets)
        return f"MKUInstance_subsets_{len(self.subsets):0{digits}}" \
                          f"_elements_{len(self.all_elements):0{digits}}" \
                          f"_k_{self.k:0{digits}}" \
                          f"_max_subset_size_{max_subset_size:0{digits}}"

    def get_constrained_objective(self, name=None):
        """ get the constrained objective object based on this instance data """
        return MKUConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_dataset(group, SUBSETS, self)
        hdf5_attributes.write_attribute(group, K, self)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        subsets = hdf5_datasets.read_dataset(group, SUBSETS)
        k = hdf5_attributes.read_attribute(group, K)
        return {SUBSETS: subsets, K: k}

    @classmethod
    def get_random(cls, elements, num_subsets=15, k=10, biggest_subset_size=8, retries=10):
        """
        get a random mku_instance

        :param (iterable or int) elements: iterable of elements to generate random subsets from,
                                           if an int is provided, then range(elements) is used
        :param (int) num_subsets: number of subsets to generate
        :param (int) k: how many elements the union should cover
        :param (int) biggest_subset_size: bound on how many elements a subset may contain at max
        :param (int) retries: the number of repetitions to try to create the desired collection
        :return: a new MKUInstance object with random subsets
        """
        if isinstance(elements, int):
            elements = range(elements)

        # Generate random subsets until desired amount is reached. If a k-union is not possible, retry.
        # End early if a valid collection of subset is found.
        for _ in range(retries):
            subsets = [random.sample(elements, random.randint(1,
                       biggest_subset_size)) for _ in range(num_subsets)]
            covered_elements = set().union(*subsets)

            # If the collection has enough elements, leave the loop and keep the collection.
            if len(covered_elements) == len(elements):
                return cls(subsets, k)

        # did not find a valid subset coverage in the above loop
        raise ValueError(ERROR_RANDOM)
