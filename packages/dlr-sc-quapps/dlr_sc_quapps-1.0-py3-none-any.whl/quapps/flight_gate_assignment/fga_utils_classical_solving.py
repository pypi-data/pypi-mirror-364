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

""" module for helper functions for the classical solving of the FlightGateAssignment problem """

import time
import itertools as it

from quark import Solution


def get_min_gate_num(instance):
    """ get lower bound on number of gates needed to solve the problem """
    max_overlap = 0
    sorted_flights = sorted(instance.flights, key=lambda flight: instance.time_in[flight])
    for index_flight, flight in enumerate(sorted_flights):
        flight_overlap = 1
        for index_successor in range(index_flight + 1, len(sorted_flights)):
            time_in = instance.time_in[sorted_flights[index_successor]]
            time_out_plus_buffer = instance.time_out[flight] + instance.time_buffer
            if time_in <= time_out_plus_buffer:
                flight_overlap += 1
        max_overlap = max(max_overlap, flight_overlap)
    return max_overlap

def get_valid_solution(instance):
    """ get a valid solution """
    start = time.time()
    sorted_flights = sorted(instance.time_out.keys(), key=lambda f: instance.time_out[f])
    colors = {flight : i for i, flight in enumerate(sorted_flights)}

    for i, flight in enumerate(sorted_flights):
        available_colors = list(range(i + 1))
        for already_colored_flight in sorted_flights[:i]:
            # check if flight is neighbored to already colored flights
            if ((already_colored_flight, flight) in instance.forbidden_pairs or
                (flight, already_colored_flight) in instance.forbidden_pairs):
                if colors[already_colored_flight] in available_colors:
                    # remove color of neighbor if still in list
                    available_colors.remove(colors[already_colored_flight])
        colors[flight] = min(available_colors)

    num_colors = len(set(colors.values()))
    solved = num_colors <= len(instance.gates)
    end = time.time()
    sol_time = end - start

    # decode solution and get cost
    var_assignments = None
    obj_value = None
    if solved:
        var_assignments = {(flight, gate) : 0 for flight, gate in it.product(instance.flights, instance.gates)}
        for flight, color in colors.items():
            # color numbers correspond to gates
            var_assignments[(flight, instance.gates[color])] = 1

    return Solution(var_assignments=var_assignments,
                    solving_time=sol_time,
                    solving_success=solved,
                    solving_status="solved" if solved else "unsolved",
                    objective_value=obj_value,
                    name="get_valid_solution")
