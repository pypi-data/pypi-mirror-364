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

""" module for testing the FlightGateAssignment ConstrainedObjective """
import pytest

from quark import PolyBinary

from quapps.flight_gate_assignment.fga_objective_terms import ONE_GATE_PER_FLIGHT, FLIGHTS_TIME_OVERLAP, TRANSIT, \
    get_penalty_weights
from quapps.flight_gate_assignment.test_fga_objective_terms import get_example_instance, get_example_objective_terms, \
    EXPECTED_OBJECTIVE_POLY


def get_example_constrained_objective(fga_instance=None):
    """ construct example constrained_objective """
    if not fga_instance:
        fga_instance = get_example_instance()

    with pytest.warns(UserWarning, match="The two variables"):
        fga_constrained_objective = fga_instance.get_constrained_objective()
    return fga_constrained_objective

def test_constrained_objective_creation():
    """ test constrained_objective creation """
    fga_constrained_objective = get_example_constrained_objective()
    assert fga_constrained_objective.objective_poly == EXPECTED_OBJECTIVE_POLY
    assert len(fga_constrained_objective) == 4

    for flight in [1, 2]:
        const_name = ONE_GATE_PER_FLIGHT + f"_{flight}"
        assert fga_constrained_objective[const_name].polynomial == PolyBinary({((flight, 1),): 1, ((flight, 2),): 1})
        assert fga_constrained_objective[const_name].upper_bound == 1
        assert fga_constrained_objective[const_name].lower_bound == 1

    expected_flights_time_overlap = PolyBinary({((1, 1), (2, 1)): 1, ((1, 2), (2, 2)): 1,
                                                ((2, 1), (3, 1)): 1, ((2, 2), (3, 2)): 1})
    assert fga_constrained_objective[FLIGHTS_TIME_OVERLAP].polynomial == expected_flights_time_overlap
    assert fga_constrained_objective[FLIGHTS_TIME_OVERLAP].upper_bound == 0
    assert fga_constrained_objective[FLIGHTS_TIME_OVERLAP].lower_bound == 0

def test_objective_terms_creation():
    """ test objective_terms creation via the constrained_objective with combining equally prefixed terms """
    fga_instance = get_example_instance()
    fga_constrained_objective = get_example_constrained_objective(fga_instance)
    fga_objective_terms = get_example_objective_terms(fga_instance)

    # combining all terms that start with the prefix
    with pytest.warns(UserWarning, match="The two variables"):
        fga_ots_from_co = fga_constrained_objective.get_objective_terms(TRANSIT, combine_prefixes=ONE_GATE_PER_FLIGHT)
    # and multiply with the introduced factors
    bounds = get_penalty_weights(fga_instance)
    for name in fga_ots_from_co.keys():
        fga_ots_from_co[name] *= bounds[name]

    assert fga_ots_from_co == fga_objective_terms

def test_objective_terms_creation_without_combine():
    """ test objective_terms creation via the constrained_objective not combining equally prefixed terms"""
    fga_constrained_objective = get_example_constrained_objective()
    fga_objective_terms = get_example_objective_terms()

    with pytest.warns(UserWarning, match="The two variables"):
        fga_ots_from_co = fga_constrained_objective.get_objective_terms(TRANSIT)
    assert len(fga_ots_from_co) > len(fga_objective_terms)
