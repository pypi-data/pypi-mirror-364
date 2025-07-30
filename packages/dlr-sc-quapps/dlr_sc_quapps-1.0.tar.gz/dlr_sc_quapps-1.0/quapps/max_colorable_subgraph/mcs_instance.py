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

""" module for the MaxColorableSubgraph Instance """

import networkx as nx

from quark.io import Instance, hdf5_datasets

from .mcs_constrained_objective import MCSConstrainedObjective


EDGES = "edges"
COLORS = "colors"

ERROR_PREFIX = "Instance is not consistent: "
ERROR_EDGES  = "No edges given"
ERROR_COLORS = "No colors given"
ERROR_TWO    = "Edges need to have two nodes"
ERROR_LOOPS  = "Edges shall not form loops"
ERROR_RANDOM = "Cannot generate the desired graph"


class MCSInstance(Instance):
    """ container for all data defining an instance of the MaxColorableSubgraph problem """

    def __init__(self, edges=None, colors=None):
        """
        an instance contains

        :param (list or set) edges: undirected edges of the graph -> implicitly define the set of nodes
        :param (list or set or int) colors: colors or number of colors defining a range
        """
        self.edges = sorted(set(tuple(sorted(edge)) for edge in edges))
        self.nodes = sorted(set(node for edge in self.edges for node in edge))
        self.colors = list(range(colors)) if isinstance(colors, int) else sorted(set(colors))
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if len(self.edges) == 0:
            raise ValueError(ERROR_PREFIX + ERROR_EDGES)
        if len(self.colors) == 0:
            raise ValueError(ERROR_PREFIX + ERROR_COLORS)
        if not all(len(edge) == 2 for edge in self.edges):
            raise ValueError(ERROR_PREFIX + ERROR_TWO)
        if any(node1 == node2 for node1, node2 in self.edges):
            raise ValueError(ERROR_PREFIX + ERROR_LOOPS)

    def get_name(self, digits=3, density_decimals=3):
        """ get an expressive name representing the instance """
        density = len(self.edges) / len(self.nodes) / (len(self.nodes) - 1) * 2
        return f"MCSInstance_nodes_{len(self.nodes):0{digits}}" \
                          f"_density_{round(density, density_decimals):.{density_decimals}f}" \
                          f"_colors_{len(self.colors):0{digits}}"

    def get_constrained_objective(self, name=None):
        """ get the objective terms object based on this instance data """
        return MCSConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_datasets(group, self, EDGES, COLORS)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        kwargs = hdf5_datasets.read_datasets(group, EDGES, COLORS)
        kwargs[EDGES] = [tuple(edge) for edge in kwargs[EDGES]]
        kwargs[COLORS] = list(kwargs[COLORS])
        return kwargs

    def get_graph(self):
        """ get a networkx graph constructed from the edges """
        graph = nx.Graph()
        graph.add_edges_from(self.edges)
        return graph

    def get_maximum_degree(self):
        """ get the maximum degree """
        return max(len([edge for edge in self.edges if node in edge]) for node in self.nodes)

    # pylint: disable=duplicate-code
    @classmethod
    def get_random(cls, num_nodes=64, density=0.8, num_colors=10, retries=10):
        """
        get a random graph instance

        :param (int) num_nodes: the number of nodes in the constructed graph
        :param (float) density: the ratio of the number of edges to the maximally possible number of edges
        :param (int) num_colors: the number of colors
        :param (int) retries: the number of repetitions to try to create the desired graph
        """
        num_edges = round(density * num_nodes * (num_nodes - 1) / 2)
        graph = nx.generators.gnm_random_graph(num_nodes, num_edges)

        # the graph shall be connected
        count = 0
        while (len(graph.nodes) < num_nodes or not nx.is_connected(graph)) and count <= retries:
            if count == retries:
                raise ValueError(ERROR_RANDOM)
            count += 1
            graph = nx.generators.gnm_random_graph(num_nodes, num_edges)

        colors = [chr(97 + i) for i in range(num_colors)]
        return cls(list(graph.edges), colors)
