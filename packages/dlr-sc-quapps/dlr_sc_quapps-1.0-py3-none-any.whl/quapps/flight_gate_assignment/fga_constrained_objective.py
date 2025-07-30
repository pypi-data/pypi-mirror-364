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

""" module for the FlightGateAssignment ConstrainedObjective """

from math import isclose

from quark import PolyBinary, ConstraintBinary, ConstrainedObjective


ONE_GATE_PER_FLIGHT = "one_gate_per_flight"
FLIGHTS_TIME_OVERLAP = "flights_time_overlap"


class FGAConstrainedObjective(ConstrainedObjective):
    """
    implementation of the objective and the constraints for the FlightGateAssignment problem

    The binary variable x_f_g is 1 if flight f is assigned to gate g and 0 otherwise.
    """

    # pylint: disable=duplicate-code
    @staticmethod
    def _get_objective_poly(instance):
        """ get the objective polynomial from the instance data """
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
                                      for (flight1, flight2), passengers_transfer in
                                      instance.passengers_transfer.items()
                                      for (gate1, gate2), time_transfer in instance.time_transfer.items()})

        return objective_poly

    @staticmethod
    def _get_constraints(instance):
        """ get the constraints from the instance data """
        constraints = {}

        # every flight should get exactly one gate:
        # for all f in Flights: sum_[g in Gates] x_f_g == 1
        for flight in instance.flights:
            poly = PolyBinary({((flight, gate),): 1 for gate in instance.gates})
            name = ONE_GATE_PER_FLIGHT + f"_{flight}"
            constraints[name] = ConstraintBinary(poly, 1, 1)

        # if the standing intervals overlap the flights cannot be assigned to the same gate:
        # for all (f1, f2) in ForbiddenFlights: for all g in Gates: x_f1_g x_f2_g == 0
        # <=> sum_[(f1, f2) in ForbiddenFlights] sum_[g in Gates] x_f1_g x_f2_g == 0
        poly = PolyBinary()
        for (flight1, flight2) in instance.forbidden_pairs:
            poly += PolyBinary({((flight1, gate), (flight2, gate)): 1 for gate in instance.gates})
        constraints[FLIGHTS_TIME_OVERLAP] = ConstraintBinary(poly, 0, 0)

        return constraints

    @staticmethod
    def get_flight_gate_assignment(raw_solution):
        """ extract the actual solution from the variable assignment """
        return {flight : gate for (flight, gate), value in raw_solution.items() if isclose(value, 1)}
