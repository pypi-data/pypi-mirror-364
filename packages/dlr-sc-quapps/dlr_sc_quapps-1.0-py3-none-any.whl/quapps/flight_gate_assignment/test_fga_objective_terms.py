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

""" module for testing the FlightGateAssignment ObjectiveTerms """

from quark import PolyBinary

from quapps.flight_gate_assignment.fga_objective_terms import FGAObjectiveTerms
from quapps.flight_gate_assignment.fga_objective_terms import TRANSIT, ONE_GATE_PER_FLIGHT, FLIGHTS_TIME_OVERLAP
from quapps.flight_gate_assignment.test_fga_instance import get_example_instance


EXPECTED_OBJECTIVE_POLY = PolyBinary({((1, 1),): 180,
                                      ((1, 2),): 195,
                                      ((2, 1),): 125,
                                      ((2, 2),): 100,
                                      ((3, 1),): 445,
                                      ((3, 2),): 430,
                                      ((1, 1), (1, 2)): 160,
                                      ((1, 1), (2, 1)): 100,
                                      ((1, 1), (2, 2)): 180,
                                      ((1, 1), (3, 1)): 200,
                                      ((1, 1), (3, 2)): 320,
                                      ((1, 2), (2, 1)): 140,
                                      ((1, 2), (2, 2)): 100,
                                      ((1, 2), (3, 1)): 320,
                                      ((1, 2), (3, 2)): 200,
                                      ((2, 1), (2, 2)): 160,
                                      ((3, 1), (3, 2)): 160})

def get_example_objective_terms(fga_instance=None):
    """ construct example objective_terms """
    if not fga_instance:
        fga_instance = get_example_instance()
    return FGAObjectiveTerms.get_from_instance(fga_instance)


def test_objective_terms_creation():
    """ test objective_terms creation """
    fga_objective_terms = get_example_objective_terms()
    assert len(fga_objective_terms) == 3
    assert fga_objective_terms[TRANSIT] == EXPECTED_OBJECTIVE_POLY

    expected_one_gate_per_flight = PolyBinary({(): 1950,
                                               ((1, 1),): -650,
                                               ((1, 2),): -650,
                                               ((2, 1),): -650,
                                               ((2, 2),): -650,
                                               ((3, 1),): -650,
                                               ((3, 2),): -650,
                                               ((1, 1), (1, 2)): 1300,
                                               ((2, 1), (2, 2)): 1300,
                                               ((3, 1), (3, 2)): 1300})
    assert fga_objective_terms[ONE_GATE_PER_FLIGHT] == expected_one_gate_per_flight

    expected_flights_time_overlap = PolyBinary({((1, 1), (2, 1)): 135, ((1, 2), (2, 2)): 135,
                                                ((2, 1), (3, 1)): 135, ((2, 2), (3, 2)): 135})
    assert fga_objective_terms[FLIGHTS_TIME_OVERLAP] == expected_flights_time_overlap
