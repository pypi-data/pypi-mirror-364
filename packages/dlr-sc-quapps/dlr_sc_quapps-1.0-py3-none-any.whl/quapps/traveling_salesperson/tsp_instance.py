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

""" module for the TravelingSalesperson Instance """

from functools import cached_property
import networkx as nx
import numpy as np

from quark.io import Instance, hdf5_datasets, hdf5_attributes

from .tsp_constrained_objective import TSPConstrainedObjective


WEIGHT = "weight"
GRAPH = "graph"
START_NODE = "start_node"

ERROR_PREFIX   = "Instance is not consistent: "
ERROR_NX       = "The input should be a networkx graph"
ERROR_EMPTY    = "The graph is empty"
ERROR_COMPLETE = "The graph is not complete"
ERROR_START    = "The start node not in the graph"
ERROR_WEIGHT   = "All edges of the graph should have a weight attribute"


class TSPInstance(Instance):
    """ container for all data defining an instance of the TravelingSalesperson problem """

    def __init__(self, graph, start_node=None):
        """
        an instance contains

        :param (nx.Graph) graph: a networkx graph or digraph
        :param start_node: a node from the graph, where the path shall start, by default the first node in the graph
        """
        if not isinstance(graph, nx.Graph):
            raise ValueError(ERROR_NX)

        self.graph = graph if isinstance(graph, nx.DiGraph) else graph.to_directed()
        self.start_node = start_node or list(self.graph.nodes)[0]
        super().__init__()

    @classmethod
    def get_from_weights_dict(cls, weights_dict, start_node=None):
        """
        initialize the instance from the mapping of nodes to weights

        :param weights_dict: the mapping from tuples of nodes to weights
        :param start_node: a node from the graph, where the path shall start, by default the first node in the graph
        """
        graph = nx.DiGraph()
        graph.add_weighted_edges_from([(node1, node2, weight) for (node1, node2), weight in weights_dict.items()])
        return cls(graph, start_node)

    @cached_property
    def num_nodes(self):
        """ the number of nodes in the graph """
        return len(self.graph.nodes)

    @cached_property
    def weights(self):
        """ the weights on the edges of the graph """
        return nx.get_edge_attributes(self.graph, WEIGHT)

    def check_consistency(self):
        """ check if the data is consistent """
        if not self.graph.nodes:
            raise ValueError(ERROR_PREFIX + ERROR_EMPTY)
        if nx.density(self.graph) < 1:
            raise ValueError(ERROR_PREFIX + ERROR_COMPLETE)
        if self.start_node not in self.graph.nodes:
            raise ValueError(ERROR_PREFIX + ERROR_START)
        if len(self.weights) != len(self.graph.edges):
            raise ValueError(ERROR_PREFIX + ERROR_WEIGHT)

    def get_name(self, digits=3):
        """ get an expressive name representing the instance """
        return f"TSPInstance_nodes_{len(self.graph.nodes):0{digits}}"

    def get_constrained_objective(self, name=None):
        """ get the constrained objective object based on this instance data """
        return TSPConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_dataset(group, WEIGHT, dataset=self.weights)
        hdf5_attributes.write_attribute(group, START_NODE, self)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        edges = hdf5_datasets.read_dataset(group, WEIGHT)
        start_node = hdf5_attributes.read_attribute(group, START_NODE)
        graph = nx.DiGraph()
        graph.add_weighted_edges_from(edge + (weight,) for edge, weight in edges.items())
        return {GRAPH: graph, START_NODE: start_node}

    @classmethod
    def get_random(cls, num_nodes=6, weight_generation_func=np.random.randint, **kwargs):
        """
        get a random graph instance

        :param (int) num_nodes: the number of nodes in the constructed graph
        :param (func) weight_generation_func: function for generation of the edge weights
        :param kwargs: keyword arguments for weight generation function
        """
        graph = nx.complete_graph(num_nodes, nx.DiGraph())

        # Set defaults. If non-default is used, user has to deal with upcoming exceptions
        if weight_generation_func is np.random.randint:
            kwargs['low'] = kwargs.get('low', 1)
            kwargs['high'] = kwargs.get('high', 10)

        for (u, v) in graph.edges():
            graph.edges[u, v][WEIGHT] = weight_generation_func(**kwargs)
        return cls(graph=graph)

    def draw_graph(self):
        """ draw the graph with its weights as edge labels """
        pos = nx.spring_layout(self.graph, seed=2)
        nx.draw(self.graph, pos, with_labels=True)
        nx.draw_networkx_edge_labels(self.graph, pos, self.weights, label_pos=0.3)
