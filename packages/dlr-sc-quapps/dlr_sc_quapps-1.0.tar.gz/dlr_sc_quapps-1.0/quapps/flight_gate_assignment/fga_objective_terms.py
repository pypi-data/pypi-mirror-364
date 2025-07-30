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

"""
module for the FlightGateAssignment ObjectiveTerms

THIS IMPLEMENTATION ONLY SERVES AS AN EXAMPLE.
To run the FGA problem productively, use the FGAConstrainedObjective.
"""

from itertools import product

from quark import PolyBinary, ObjectiveTerms


ONE_GATE_PER_FLIGHT = "one_gate_per_flight"
FLIGHTS_TIME_OVERLAP = "flights_time_overlap"
TRANSIT = "transit"


class FGAObjectiveTerms(ObjectiveTerms):
    """ implementation of the objective terms for the FlightGateAssignment problem """

    @staticmethod
    def _get_constraint_terms_names():
        """
        get the names of the objective terms whose value must be zero to have the corresponding constraints fulfilled,
        which need to be a subset of all objective terms names
        """
        return [ONE_GATE_PER_FLIGHT, FLIGHTS_TIME_OVERLAP]

    # pylint: disable=duplicate-code
    @staticmethod
    def _get_objective_terms(instance):
        """ get the objective terms from the instance data """
        objective_terms = {TRANSIT: get_objective_poly(instance),
                           ONE_GATE_PER_FLIGHT: PolyBinary(),
                           FLIGHTS_TIME_OVERLAP: PolyBinary()}
        weights = get_penalty_weights(instance)

        # objective terms from the constraints
        # sum_[f in Flights] (sum_[g in Gates] x_f_g - 1)^2
        for flight in instance.flights:
            poly = PolyBinary({((flight, gate),): 1 for gate in instance.gates}) - 1
            objective_terms[ONE_GATE_PER_FLIGHT] += poly * poly
        objective_terms[ONE_GATE_PER_FLIGHT] *= weights[ONE_GATE_PER_FLIGHT]

        # sum_[(f1, f2) in ForbiddenFlights] sum_[g in Gates]] x_f1_g x_f2_g
        objective_terms[FLIGHTS_TIME_OVERLAP] += PolyBinary({((flight1, gate), (flight2, gate)): 1
                                                             for gate in instance.gates
                                                             for (flight1, flight2) in instance.forbidden_pairs})
        objective_terms[FLIGHTS_TIME_OVERLAP] *= weights[FLIGHTS_TIME_OVERLAP]

        return objective_terms


def get_objective_poly(instance):
    """ construct the polynomial representing the objective """
    # sum_[f in Flights} sum_[g in Gates] n^a_f t^in_g x_f_g
    objective_poly = PolyBinary({((flight, gate),): passengers_in * time_arrival
                                 for flight, passengers_in in instance.passengers_in.items()
                                 for gate, time_arrival in instance.time_arrival.items()})

    # sum_[f in Flights} sum_[g in Gates] n^d_f t^out_g x_f_g
    objective_poly += PolyBinary({((flight, gate),): passengers_out * time_departure
                                  for flight, passengers_out in instance.passengers_out.items()
                                  for gate, time_departure in instance.time_departure.items()})

    # sum_[(f1, f2) in TransferFlights} sum_[(g1, g2) in Gates^2]  n_f1_f2 t_g1_g2 x_f1_g1 x_f2_g2
    objective_poly += PolyBinary({((flight1, gate1), (flight2, gate2)): passengers_transfer * time_transfer
                                  for (flight1, flight2), passengers_transfer in instance.passengers_transfer.items()
                                  for (gate1, gate2), time_transfer in instance.time_transfer.items()})

    return objective_poly

def get_penalty_weights(instance):
    """ precalculate upper bounds for minimal sufficient penalty weights """
    return {TRANSIT             : 1,
            ONE_GATE_PER_FLIGHT : _get_max_weight_one_gate_per_flight(instance),
            FLIGHTS_TIME_OVERLAP: _get_max_weight_flights_time_overlap(instance)}

def _get_max_weight_one_gate_per_flight(instance):
    max_weight = 1
    for flight, gate in product(instance.flights, instance.gates):
        weight = 0
        if flight in instance.passengers_out:
            weight += instance.passengers_out[flight] * instance.time_departure[gate]
        if flight in instance.passengers_in:
            weight += instance.passengers_in[flight] * instance.time_arrival[gate]

        max_time = 0
        for gate2 in instance.gates:
            time = instance.time_transfer[(gate, gate2)]
            max_time = max(max_time, time)

        passenger_sum = 0
        for flight2 in instance.flights:
            if (flight, flight2) in instance.passengers_transfer:
                passenger_sum += instance.passengers_transfer[(flight, flight2)]
        weight += max_time * passenger_sum
        max_weight = max(max_weight, weight)
    return max_weight

def _get_max_weight_flights_time_overlap(instance):
    max_weight = 1
    for flight, gate1, gate2 in product(instance.flights, instance.gates, instance.gates):
        weight = 0
        if flight in instance.passengers_out:
            weight += instance.passengers_out[flight] * instance.time_departure[gate2]
            weight -= instance.passengers_out[flight] * instance.time_departure[gate1]
        if flight in instance.passengers_in:
            weight += instance.passengers_in[flight] * instance.time_arrival[gate2]
            weight -= instance.passengers_in[flight] * instance.time_arrival[gate1]

        max_time = 0
        for gate3 in instance.gates:
            time = instance.time_transfer[(gate2, gate3)]
            max_time = max(max_time, time)

        min_time = float("inf")
        for gate3 in instance.gates:
            time = instance.time_transfer[(gate1, gate3)]
            min_time = min(min_time, time)

        passenger_sum = 0
        for flight2 in instance.flights:
            if (flight, flight2) in instance.passengers_transfer:
                passenger_sum += instance.passengers_transfer[(flight, flight2)]
        weight += (max_time - min_time) * passenger_sum
        max_weight = max(max_weight, weight)
    return max_weight
