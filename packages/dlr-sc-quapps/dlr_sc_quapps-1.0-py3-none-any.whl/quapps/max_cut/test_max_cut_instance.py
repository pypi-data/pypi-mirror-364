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

""" module for testing the MaxCut Instance """

import os
import pytest
import networkx as nx

from quapps.max_cut import MaxCutInstance
from quapps.max_cut.max_cut_instance import get_graph


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"

EXP_NAME = "MaxCutInstance_nodes_005_density_0.600"


def get_example_max_cut_instance():
    """ construct example instance """
    edges = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "a"), ("b", "e")]
    graph = get_graph(edges)
    return MaxCutInstance(graph)

def get_example_weighted_max_cut_instance():
    """ construct example instance with weights """
    graph = nx.Graph()
    graph.add_weighted_edges_from([("a", "b", 0.5),
                                   ("a", "e", 3.0),
                                   ("b", "c", 1.0),
                                   ("b", "e", 1.0),
                                   ("c", "d", 2.0),
                                   ("d", "e", 1.5)])
    return MaxCutInstance(graph)


def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="No networkx graph given"):
        MaxCutInstance([])
    with pytest.raises(ValueError, match="Graph is empty"):
        MaxCutInstance(nx.Graph())

    max_cut_instance = get_example_max_cut_instance()
    max_cut_instance.graph.edges[("a", "b")]["weight"] = 1
    with pytest.raises(ValueError, match="Either provide no weight or weights for all edges"):
        MaxCutInstance(max_cut_instance.graph)

def test_get_name():
    """ test name of instance """
    max_cut_instance = get_example_max_cut_instance()
    assert max_cut_instance.get_name() == EXP_NAME

def test_io():
    """ test read and write of instance """
    max_cut_instance = get_example_max_cut_instance()
    max_cut_instance.save_hdf5(FILENAME_TMP)
    loaded = MaxCutInstance.load_hdf5(FILENAME_TMP)

    assert loaded.graph.edges == max_cut_instance.graph.edges

    os.remove(FILENAME_TMP)

def test_io_with_weights():
    """ test read and write of instance with weights """
    max_cut_instance = get_example_weighted_max_cut_instance()
    max_cut_instance.save_hdf5(FILENAME_TMP)
    loaded = MaxCutInstance.load_hdf5(FILENAME_TMP)

    assert loaded.graph.edges == max_cut_instance.graph.edges
    assert loaded.get_weights() == max_cut_instance.get_weights()

    os.remove(FILENAME_TMP)

def test_get_random():
    """ test random instance """
    random_instance = MaxCutInstance.get_random(10, 0.8)
    assert len(random_instance.graph.nodes) == 10
    assert len(random_instance.graph.edges) == 36

    with pytest.raises(ValueError, match="Cannot generate the desired graph"):
        MaxCutInstance.get_random(10, 0.01)

    random_instance = MaxCutInstance.get_random(10, 0.8, weight_range=range(1, 6))
    weights = random_instance.get_weights()
    assert len(weights) == len(random_instance.graph.edges)
    assert set(weights.values()) > {1}
