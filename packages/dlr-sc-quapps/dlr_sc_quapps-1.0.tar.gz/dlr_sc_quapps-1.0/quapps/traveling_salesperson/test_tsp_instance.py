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

""" module for testing the TravelingSalesperson Instance """

import os
import pytest
import networkx as nx

from quapps.traveling_salesperson import TSPInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"

WEIGHTS_DICT = {('a', 'b'): 8, ('b', 'a'): 4, ('a', 'c'): 1, ('c', 'a'): 2, ('a', 'd'): 1, ('d', 'a'): 7,
                ('b', 'c'): 1, ('c', 'b'): 4, ('b', 'd'): 6, ('d', 'b'): 1, ('c', 'd'): 9, ('d', 'c'): 5}


def get_example_instance():
    """ construct an example instance using networkx graph with 4 nodes """
    return TSPInstance.get_from_weights_dict(WEIGHTS_DICT)


def test_init():
    """ test initialization of instance """
    tsp_instance = get_example_instance()
    assert tsp_instance.start_node == 'a'
    assert tsp_instance.weights == {('a', 'b'): 8, ('a', 'c'): 1, ('a', 'd'): 1,
                                    ('b', 'a'): 4, ('b', 'c'): 1, ('b', 'd'): 6,
                                    ('c', 'a'): 2, ('c', 'b'): 4, ('c', 'd'): 9,
                                    ('d', 'a'): 7, ('d', 'b'): 1, ('d', 'c'): 5}

def test_consistency():
    """ test all consistency checks """
    with pytest.raises(ValueError, match="The input should be a networkx graph"):
        TSPInstance([], 'a')
    with pytest.raises(ValueError, match="Instance is not consistent: The graph is empty"):
        graph = nx.Graph()
        TSPInstance(graph, 'a')
    with pytest.raises(ValueError, match="All edges of the graph should have a weight attribute"):
        graph = nx.Graph()
        graph.add_edge('a', 'b')
        TSPInstance(graph)
    with pytest.raises(ValueError, match="Instance is not consistent: The graph is not complete"):
        graph = nx.Graph()
        graph.add_weighted_edges_from([('a', 'b', 8.0), ('a', 'c', 2.0)])
        TSPInstance(graph, 'a')
    with pytest.raises(ValueError, match="The start node not in the graph"):
        graph = nx.Graph()
        graph.add_weighted_edges_from([('a', 'b', 8.0), ('a', 'c', 2.0), ('b', 'c', 2.0)])
        TSPInstance(graph, 'd')

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "TSPInstance_nodes_004"

def test_io_with_weights():
    """ test read and write of instance with weights """
    tsp_instance = get_example_instance()
    tsp_instance.save_hdf5(FILENAME_TMP)
    loaded = TSPInstance.load_hdf5(FILENAME_TMP)

    assert loaded.graph.edges == tsp_instance.graph.edges
    assert loaded.weights == tsp_instance.weights
    assert loaded.start_node == tsp_instance.start_node

    os.remove(FILENAME_TMP)

def test_get_random():
    """ test random instance """
    random_instance = TSPInstance.get_random(8)
    assert len(random_instance.graph.nodes) == 8
    assert len(random_instance.graph.edges) == 56
    assert max(random_instance.weights.values()) < 10
    assert min(random_instance.weights.values()) >= 1

def test_draw():
    """ test drawing of instance """
    tsp_instance = get_example_instance()
    tsp_instance.draw_graph()
