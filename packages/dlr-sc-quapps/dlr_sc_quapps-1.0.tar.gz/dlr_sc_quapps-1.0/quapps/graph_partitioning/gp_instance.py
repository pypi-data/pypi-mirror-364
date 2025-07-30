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

""" module for the GraphPartitioning Instance """

import random
import networkx as nx

from quark.io import Instance, hdf5_datasets, hdf5_attributes

from .gp_constrained_objective import GPConstrainedObjective


EDGES = "edges"
NUMBER_OF_SUBGRAPHS = "number_of_subgraphs"

ERROR_PREFIX   = "Instance is not consistent: "
ERROR_EMPTY    = "No edges given"
ERROR_TWO      = "Edges need to have two nodes"
ERROR_NEGATIVE = "Number of subgraphs must be positive"
ERROR_INTEGER  = "Number of subgraphs must be an integer"
ERROR_RANDOM = "Cannot generate the desired graph"


class GPInstance(Instance):
    """ container for all data defining an instance of the GraphPartitioning problem """

    def __init__(self, edges, number_of_subgraphs=2):
        """
        an instance contains

        :param (dict): mapping of undirected edges to weights
        :param (int): the number of subgraphs that the graph shall be partitioned into
        """
        self.edges = {tuple(sorted(edge)): weight for edge, weight in edges.items() if weight != 0}
        self.nodes = set(node for edge in edges.keys() for node in edge)
        self.number_of_subgraphs = number_of_subgraphs
        super().__init__()

    def check_consistency(self):
        """ check if the data is consistent """
        if not self.edges or len(self.edges) == 0:  # Check: Set of edges is not empty
            raise ValueError(ERROR_PREFIX + ERROR_EMPTY)
        if not all(len(edge) == 2 for edge in self.edges.keys()):  # Check: All edges consist of 2 elements
            raise ValueError(ERROR_PREFIX + ERROR_TWO)
        if not isinstance(self.number_of_subgraphs, int):  # Check: number_of_subgraphs is an integer
            raise TypeError(ERROR_PREFIX + ERROR_INTEGER)
        if self.number_of_subgraphs <= 1:  # Check: number_of_subgraphs is > 1
            raise ValueError(ERROR_PREFIX + ERROR_NEGATIVE)

    def get_name(self, digits=3, density_decimals=3):
        """ get an expressive name representing the instance """
        density = len(self.edges) / len(self.nodes) / (len(self.nodes) - 1) * 2
        return f"GPInstance_nodes_{len(self.nodes):0{digits}}" \
                         f"_density_{round(density, density_decimals):.{density_decimals}f}" \
                         f"_subgraphs_{self.number_of_subgraphs:0{digits}}"

    def get_constrained_objective(self, name=None):
        """ get the constrained objective object based on this instance data """
        return GPConstrainedObjective.get_from_instance(self, name)

    def write_hdf5(self, group):
        """
        write data in attributes and datasets in the opened group of the HDF5 file

        :param (h5py.Group) group: the group to store the data in
        """
        hdf5_datasets.write_datasets(group, self, EDGES)
        hdf5_attributes.write_attributes(group, self, NUMBER_OF_SUBGRAPHS)

    @staticmethod
    def read_hdf5(group):
        """
        read data from attributes and datasets of the opened group of the HDF5 file

        :param (h5py.Group) group: the group to read the data from
        :return: the data as keyword arguments
        """
        kwargs = hdf5_datasets.read_datasets(group, EDGES)
        kwargs.update(hdf5_attributes.read_attributes(group, NUMBER_OF_SUBGRAPHS))
        return kwargs

    def get_graph(self):
        """ get a networkx graph constructed from the edges """
        graph = nx.Graph()
        graph.add_weighted_edges_from([(i, j, weight) for (i, j), weight in self.edges.items()])
        return graph

    # pylint: disable=duplicate-code
    @classmethod
    def get_random(cls, num_nodes=64, density=0.8, number_of_subgraphs=7, max_weight=10, digits=2, retries=10):
        """
        generate a random weighted graph and return a random Graph Partitioning instance

        :param (int) num_nodes: the number of nodes in the constructed graph
        :param (float) density: the ratio of the number of edges to the maximally possible number of edges
        :param (int) number_of_subgraphs: the number of subgraphs for the graph partitioning
        :param (float) max_weight: the upper bound on the random edge weights
        :param (int) digits: desired decimal places of the random edge weights
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

        # generate dict of weighted edges with weights in [0, max_weight)
        weighted_edges = {tuple(sorted(edge)): round(random.random() * max_weight, digits)
                          for edge in list(graph.edges)}

        return cls(weighted_edges, number_of_subgraphs)
