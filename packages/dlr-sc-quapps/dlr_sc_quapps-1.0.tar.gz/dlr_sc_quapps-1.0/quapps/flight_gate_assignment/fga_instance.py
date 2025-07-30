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

""" module for the FlightGateAssignment Instance """

from itertools import product, combinations
from functools import cached_property

from quark.io import Instance, hdf5_attributes, hdf5_datasets

from .fga_constrained_objective import FGAConstrainedObjective


TIME_BUFFER = "time_buffer"
DATASETS = ["flights",
            "gates",
            "time_arrival",
            "time_departure",
            "passengers_in",
            "passengers_out",
            "passengers_transfer",
            "time_in",
            "time_out",
            "time_transfer"]

ERROR_PREFIX              = "Instance is not consistent: "
ERROR_TIME_DEPARTURE      = "time_departure does not exist for all gates"
ERROR_TIME_ARRIVAL        = "time_arrival does not exist for all gates"
ERROR_TIME_TRANSFER       = "time_transfer does not exist for all gate combinations"
ERROR_PASSENGERS_IN       = "There are passengers_in values for flights that do not exist"
ERROR_PASSENGERS_OUT      = "There are passengers_out values for flights that do not exist"
ERROR_PASSENGERS_TRANSFER = "There are passengers_transfer values for flight combinations that do not exist"
ERROR_TIME_IN             = "There are time_in values for flight combinations that do not exist"
ERROR_TIME_OUT            = "There are time_out values for flight combinations that do not exist"


class FGAInstance(Instance):
    """ container for all data defining an instance of the FlightGateAssignment problem """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self,
                 flights=None,
                 gates=None,
                 time_buffer=None,
                 time_arrival=None,
                 time_departure=None,
                 time_transfer=None,
                 passengers_in=None,
                 passengers_out=None,
                 passengers_transfer=None,
                 time_in=None,
                 time_out=None):
        """
        an instance contains

        :param (list) flights: collection of flights
        :param (list) gates: collection of gates
        :param (int) time_buffer: time buffer in seconds
        :param (dict) time_arrival: gate -> time in seconds to reach gate from check-in
        :param (dict) time_departure: gate -> time in seconds to reach baggage claim from gate
        :param (dict) time_transfer: (gate1, gate2) -> time in seconds to get from gate1 to gate 2 and vice versa
        :param (dict) passengers_in: flight -> passengers staying at the airport after arriving with the flight
        :param (dict) passengers_out: flight -> passengers departing from the airport with the flight
        :param (dict) passengers_transfer: (flight1, flight2) -> passengers arriving with flight1 and
                                                                 departing with flight2
        :param (dict) time_in: flight -> arrival time of the flight in seconds
        :param (dict) time_out: flight -> departure time of the flight in seconds
        """
        self.flights = flights
        self.gates = gates
        self.time_buffer = time_buffer
        self.time_arrival = time_arrival
        self.time_departure = time_departure
        self.time_transfer = time_transfer
        self.passengers_in = passengers_in
        self.passengers_out = passengers_out
        self.passengers_transfer = passengers_transfer
        self.time_in = time_in
        self.time_out = time_out
        super().__init__()

    @cached_property
    def forbidden_pairs(self):
        """ forbidden flight pairs due to overlapping on-block times """
        forbidden_pairs = []
        for flight1, flight2 in combinations(self.flights, 2):
            if (self.time_in[flight1] - self.time_out[flight2] < self.time_buffer and
                self.time_in[flight2] - self.time_out[flight1] < self.time_buffer):
                forbidden_pairs.append((flight1, flight2))
        return forbidden_pairs

    def check_consistency(self):
        """ check if the data is consistent """
        for error, check in self._get_inconsistencies().items():
            if not check:
                raise ValueError(ERROR_PREFIX + error)

    def _get_inconsistencies(self):
        return {ERROR_TIME_DEPARTURE:      set(self.time_departure.keys()) == set(self.gates),
                ERROR_TIME_ARRIVAL:        set(self.time_arrival.keys()) == set(self.gates),
                ERROR_TIME_TRANSFER:       set(self.time_transfer.keys()) == set(product(self.gates, repeat=2)),
                ERROR_PASSENGERS_IN:       set(self.passengers_in.keys()) <= set(self.flights),
                ERROR_PASSENGERS_OUT:      set(self.passengers_out.keys()) <= set(self.flights),
                ERROR_PASSENGERS_TRANSFER: set(self.passengers_transfer.keys()) <= set(product(self.flights, repeat=2)),
                ERROR_TIME_IN:             set(self.time_in.keys()) <= set(self.flights),
                ERROR_TIME_OUT:            set(self.time_out.keys()) <= set(self.flights)}

    def get_name(self, digits=3):
        """ get an expressive name representing the instance """
        return f"FGAInstance_flights_{len(self.flights):0{digits}}" \
                          f"_gates_{len(self.gates):0{digits}}"

    def get_constrained_objective(self, name=None):
        """ get the constrained objective object based on this instance data """
        return FGAConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_attributes.write_attribute(group, TIME_BUFFER, self)
        hdf5_datasets.write_datasets(group, self, *DATASETS)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        time_buffer = hdf5_attributes.read_attribute(group, TIME_BUFFER)
        datasets = hdf5_datasets.read_datasets(group, *DATASETS)
        return {"time_buffer": time_buffer, **datasets}
