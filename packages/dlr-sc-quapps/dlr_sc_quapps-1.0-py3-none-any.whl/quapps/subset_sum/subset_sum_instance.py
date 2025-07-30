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

""" module for the SubsetSum instance """

import warnings
from random import randint

from quark.io import Instance, hdf5_datasets, hdf5_attributes

from .subset_sum_objective import SubsetSumObjective


NUMBERS = "numbers"
TARGET_SUM = "target_sum"

ERROR_PREFIX = "Instance is not consistent: "
ERROR_EMPTY = "No numbers given"
ERROR_LIMIT_TYPE_T = "The target_sum is not an integer"
ERROR_LIMIT_TYPE_N = "The numbers is not a collection of integers"
WARNING_NUMBERS_DICT = "Only the keys of the dictionary will be used"


class SubsetSumInstance(Instance):
    """ container for all data defining an instance of the SubsetSum problem """

    def __init__(self, numbers, target_sum):
        """
        an instance contains:

        :param (list or set) numbers: list of the numbers from which the sum is built
        :param (int) target_sum: the targeted sum
        """
        if isinstance(numbers, dict):
            warnings.warn(WARNING_NUMBERS_DICT)
        self.numbers = sorted(numbers)
        self.num_numbers = len(self.numbers)
        self.target_sum = target_sum
        super().__init__()
        self.min_number = min(self.numbers)
        self.max_number = max(self.numbers)

    def check_consistency(self):
        """ check if the data is consistent """
        if self.num_numbers == 0:    # Check: List of numbers is not empty
            raise ValueError(ERROR_PREFIX + ERROR_EMPTY)
        if not isinstance(self.target_sum, int):      # Check: target-sum is an integer
            raise TypeError(ERROR_PREFIX + ERROR_LIMIT_TYPE_T)
        for x in self.numbers: # check: self.numbers is list of numbers
            if not isinstance(x, int):
                raise TypeError(ERROR_PREFIX + ERROR_LIMIT_TYPE_N)

    def get_name(self):
        """ get an expressive name representing the instance """
        return f"SubsetSumInstance_numbers_{self.num_numbers}" \
                                f"_min_{self.min_number}" \
                                f"_max_{self.max_number}" \
                                f"_target_sum_{self.target_sum}"

    # pylint: disable=arguments-differ  # no other arguments are needed here to get the objective
    def get_objective(self, name=None):
        """ get the objective object obtained directly from the ssp instance """
        return SubsetSumObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_datasets(group, self, NUMBERS)
        hdf5_attributes.write_attributes(group, self, TARGET_SUM)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        kwargs = hdf5_datasets.read_datasets(group, NUMBERS)
        kwargs[NUMBERS] = [ int(val) for val in kwargs[NUMBERS] ]
        kwargs.update(hdf5_attributes.read_attributes(group, TARGET_SUM))

        return kwargs

    @staticmethod
    def get_random(num_numbers=20, max_number=200, max_target_sum=2000):
        """
        get a random SubsetSum instance

        :param (int) num_numbers: length of the list of numbers
        :param (int) max_number: the upper bound on the numbers to be generated (inclusive)
        :param (int) max_target_sum: the maximum target_sum to be generated (inclusive)
        :return: the random SubsetSum instance
        """
        numbers = [randint(0, max_number) for _ in range(num_numbers)]
        target_sum = randint(min(numbers), min(max_target_sum, sum(numbers)))
        return SubsetSumInstance(numbers, target_sum)
