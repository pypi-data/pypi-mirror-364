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

""" module for the Knapsack instance """

import random

from quark.io import Instance, hdf5_datasets, hdf5_attributes

from .knapsack_constrained_objective import KnapsackConstrainedObjective


ITEMS = "items"
CAPACITY = "capacity"

ERROR_PREFIX = "Instance is not consistent: "
ERROR_EMPTY = "No items given"
ERROR_CAPACITY = "Capacity is not a positive integer"
ERROR_MISSING_ATTRIBUTE = "An item is missing a value or a weight"
ERROR_VALUE_FLOAT_INT = "At least one value is not a float or integer"
ERROR_WEIGHT_INT = "At least one weight is not an integer"


class KnapsackInstance(Instance):
    """ container for all data defining an instance of the Knapsack problem """

    def __init__(self, items=None, capacity=0):
        """
        an instance contains:

        :param(dict) items: dictionary of items where the name of an item points to a (value, weight)-tuple
        :param(int) capacity: the weight capacity of the knapsack
        """
        self.items = items
        self.capacity = capacity
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if not self.items:  # Check: List of items is not empty
            raise ValueError(ERROR_PREFIX + ERROR_EMPTY)
        if not all(len(self.items[name]) == 2 for name in self.items):  # Check: Every item has a value and weight
            raise ValueError(ERROR_PREFIX + ERROR_MISSING_ATTRIBUTE)
        if not all(isinstance((self.items[name][0]), (float, int)) for name in self.items):  # Check: values type
            raise TypeError(ERROR_PREFIX + ERROR_VALUE_FLOAT_INT)
        if not all(isinstance((self.items[name][1]), int) for name in self.items):  # Check: weights type
            raise TypeError(ERROR_PREFIX + ERROR_WEIGHT_INT)
        if not isinstance(self.capacity, int) or self.capacity < 0:  # Check: Weight capacity is positive integer
            raise ValueError(ERROR_PREFIX + ERROR_CAPACITY)

    def get_name(self, digits=3):
        """ get an expressive name representing the instance """
        max_value = max(value for value, _ in self.items.values())
        max_weight = max(weight for _, weight in self.items.values())
        return f"KnapsackInstance_items_{len(self.items):0{digits}}" \
                               f"_capacity_{self.capacity:0{digits}}" \
                               f"_max_value_{max_value:0{digits}}" \
                               f"_max_weight_{max_weight:0{digits}}"

    def get_constrained_objective(self, name=None):
        """ get the objective terms object based on this instance data """
        return KnapsackConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_datasets(group, self, ITEMS)
        hdf5_attributes.write_attributes(group, self, CAPACITY)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        kwargs = hdf5_datasets.read_datasets(group, ITEMS)
        kwargs[ITEMS] = {name: (float(value), int(weight)) for name, (value, weight) in kwargs[ITEMS].items()}
        kwargs.update(hdf5_attributes.read_attributes(group, CAPACITY))
        return kwargs

    @staticmethod
    def get_random(num_items=20, max_value=20, max_weight=20, max_capacity=50):
        """
        get a random knapsack instance

        :param (int) num_items: how many random items to generate
        :param (float) max_value: upper bound on the random item values (inclusive)
        :param (int) max_weight: upper bound on the random item weights (inclusive)
        :param (int) max_capacity: upper bound on the random capacity (inclusive)
        """
        items = {i: (round(random.uniform(0, max_value), 2), random.randint(1, max_weight)) for i in range(num_items)}
        capacity = random.randint(0, max_capacity)

        return KnapsackInstance(items, capacity)
