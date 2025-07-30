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

""" module for testing the MaxColorableSubgraph Instance """

import os
import pytest

from quapps.max_colorable_subgraph import MCSInstance


TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"
FILENAME_TMP = TEST_DIR + "test_instance.h5"


def get_example_instance():
    """ construct example instance """
    edges = [(1, 2), (2, 3), (3, 4), (2, 4), (2, 1), (3, 4)]
    num_colors = 3
    return MCSInstance(edges, num_colors)

def get_example_instance_color_set():
    """ construct example instance using named colors """
    edges = [(1, 2), (2, 3), (3, 4), (2, 4)]
    colors = ["red", "green", "blue"]
    return MCSInstance(edges, colors)


def test_init():
    """ test initialization of instance """
    mcs_instance = get_example_instance()
    assert mcs_instance.edges == [(1, 2), (2, 3), (2, 4), (3, 4)]
    assert mcs_instance.nodes == [1, 2, 3, 4]
    assert mcs_instance.colors == [0, 1, 2]

def test_consistency():
    """ test consistency of instance data """
    with pytest.raises(ValueError, match="No edges given"):
        MCSInstance([], 3)
    with pytest.raises(ValueError, match="No colors given"):
        MCSInstance([(1, 2), (2, 3)], 0)
    with pytest.raises(ValueError, match="Edges need to have two nodes"):
        MCSInstance([(1, 2, 3)], 3)
    with pytest.raises(ValueError, match="Edges shall not form loops"):
        MCSInstance([(1, 1)], 3)

def test_get_name():
    """ test name of instance """
    instance = get_example_instance()
    assert instance.get_name() == "MCSInstance_nodes_004_density_0.667_colors_003"

def test_get_random():
    """ test random generator """
    random_instance = MCSInstance.get_random(10, 0.6, 4)
    assert len(random_instance.nodes) == 10

    with pytest.raises(ValueError, match="Cannot generate the desired graph"):
        MCSInstance.get_random(10, 0.01, 4)

def test_io():
    """ test read and write of instance """
    mcs_instance = get_example_instance()
    _check_io(mcs_instance)

    mcs_instance = get_example_instance_color_set()
    _check_io(mcs_instance)

def _check_io(mcs_instance):
    mcs_instance.save_hdf5(FILENAME_TMP)
    loaded = MCSInstance.load_hdf5(FILENAME_TMP)

    assert loaded.edges == mcs_instance.edges
    assert loaded.colors == mcs_instance.colors

    os.remove(FILENAME_TMP)

def test_get_graph():
    """ test graph creation """
    mcs_instance = get_example_instance()
    graph = mcs_instance.get_graph()
    assert len(mcs_instance.edges) == len(graph.edges)
    assert all(graph.has_edge(*edge) for edge in mcs_instance.edges)

def test_get_maximum_degree():
    """ test maximum degree """
    mcs_instance = get_example_instance()
    assert mcs_instance.get_maximum_degree() == 3
