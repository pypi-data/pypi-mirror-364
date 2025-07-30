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

""" module for the MaxCut Instance """

import random
import networkx as nx

from quark.io import Instance, hdf5_datasets

from .max_cut_objective import MaxCutObjective


EDGES = "edges"
WEIGHT = "weight"
GRAPH = "graph"
NODES = "nodes"
INDEX = "index"
DENSITY = "density"

ERROR_PREFIX = "Instance is not consistent: "
ERROR_GRAPH  = "No networkx graph given"
ERROR_EMPTY  = "Graph is empty"
ERROR_WEIGHT = "Either provide no weight or weights for all edges"
ERROR_RANDOM = "Cannot generate the desired graph"


class MaxCutInstance(Instance):
    """ container for all data defining an instance of the MaxCut problem """

    def __init__(self, graph):
        """
        an instance contains

        :param (nx.Graph) graph: a networkx graph with nodes and edges
        """
        self.graph = graph
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if not isinstance(self.graph, nx.Graph):
            raise ValueError(ERROR_PREFIX + ERROR_GRAPH)
        if len(self.graph.nodes) == 0:
            raise ValueError(ERROR_PREFIX + ERROR_EMPTY)

        weights = self.get_weights()
        if weights and len(weights) != len(self.graph.edges):
            raise ValueError(ERROR_PREFIX + ERROR_WEIGHT)

    def get_name(self, digits=3, density_decimals=3):
        """ get an expressive name representing the instance """
        return f"MaxCutInstance_nodes_{len(self.graph.nodes):0{digits}}" \
                             f"_density_{round(nx.density(self.graph), density_decimals):.{density_decimals}f}"

    def get_weights(self):
        """ get the weights associated with the edges in the graph """
        return nx.get_edge_attributes(self.graph, WEIGHT)

    # pylint: disable=arguments-differ  # no other arguments are needed here to get the objective
    def get_objective(self, name=None):
        """ get the objective object based on this instance data """
        return MaxCutObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        weights = self.get_weights() or list(self.graph.edges())
        hdf5_datasets.write_dataset(group, EDGES, dataset=weights)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        edges = hdf5_datasets.read_dataset(group, EDGES)
        if isinstance(edges, dict):
            graph = nx.Graph()
            # sometimes edges seem to be swapped at this point - not clear why
            graph.add_weighted_edges_from(edge + (weight,) for edge, weight in edges.items())
        else:
            graph = get_graph(edges)
        return {GRAPH: graph}

    # pylint: disable=duplicate-code
    @classmethod
    def get_random(cls, num_nodes=64, density=0.8, weight_range=None, retries=10):
        """
        get a random graph instance

        :param (int) num_nodes: the number of nodes in the constructed graph
        :param (float) density: the ratio of the number of edges to the maximally possible number of edges
        :param (list or range) weight_range: the weights from which the edge weights are randomly chosen from,
                                             if None, the instance is unweighted
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

        if weight_range:
            weights = {edge: random.choice(weight_range) for edge in graph.edges}
            nx.set_edge_attributes(graph, weights, WEIGHT)
        return cls(graph=graph)


def get_graph(edges):
    """
    construct a networkx graph from the edges

    :param (list or set) edges: collection of pairs of nodes
    """
    graph = nx.Graph()
    graph.add_edges_from(edges)
    return graph
