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

""" module for testing the GraphPartitioning instance """

import os
import pytest

from quapps.graph_partitioning import GPInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"


def get_example_instance():
    """ construct example instance """
    edges = {(1, 2): 5, (2, 3): 4, (4, 2): 5, (5, 1): 4, (5, 6): 2, (5, 7): 3}
    number_of_subgraphs = 3
    return GPInstance(edges, number_of_subgraphs)


def test_init():
    """ test initialization of instance """
    gp_instance = get_example_instance()
    assert gp_instance.edges == {(1, 2): 5, (2, 3): 4, (2, 4): 5, (1, 5): 4, (5, 6): 2, (5, 7): 3}
    assert gp_instance.nodes == {1, 2, 3, 4, 5, 6, 7}
    assert gp_instance.number_of_subgraphs == 3

def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="No edges given"):
        GPInstance({}, 3)
    with pytest.raises(ValueError, match="Edges need to have two nodes"):
        GPInstance({(1, 2, 6): 4, (2, 3): 1}, 4)
    with pytest.raises(ValueError, match="Number of subgraphs must be positive"):
        GPInstance({(2, 3): 5, (1, 4): 2}, -1)
    with pytest.raises(TypeError, match="Number of subgraphs must be an integer"):
        GPInstance({(2, 3): 5, (1, 4): 2}, 4.3)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "GPInstance_nodes_007_density_0.286_subgraphs_003"

def test_io():
    """ test read and write of instance """
    gp_instance = get_example_instance()
    gp_instance.save_hdf5(FILENAME_TMP)
    loaded = GPInstance.load_hdf5(FILENAME_TMP)

    assert loaded.edges == gp_instance.edges
    assert loaded.number_of_subgraphs == gp_instance.number_of_subgraphs

    os.remove(FILENAME_TMP)

def test_get_graph():
    """ test graph creation """
    gp_instance = get_example_instance()
    graph = gp_instance.get_graph()
    assert len(gp_instance.edges.keys()) == len(graph.edges)
    assert all(graph.has_edge(*edge) for edge in gp_instance.edges.keys())

def test_get_random():
    """ test random generator """
    random_instance = GPInstance.get_random(10, 0.6, 3, 10, 2, 6)
    assert len(random_instance.nodes) == 10

    # Check whether all weights are less than the max_weight
    for edge in random_instance.edges.keys():
        assert random_instance.edges[edge] < 10

    with pytest.raises(ValueError, match="Cannot generate the desired graph"):
        GPInstance.get_random(10, 0.01, 4, 10, 2, 4)
