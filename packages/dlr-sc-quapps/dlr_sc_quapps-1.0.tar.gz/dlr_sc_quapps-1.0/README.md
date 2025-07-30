# quapps - QUantum APPlicationS

[![pipeline status](https://gitlab.com/quantum-computing-software/quapps//badges/development/pipeline.svg)](https://gitlab.com/quantum-computing-software/quapps/-/commits/development)

This is a software package containing a collection of exemplary application implementations based on ``quark``.

## Documentation

The full documentation can be found [here](https://quantum-computing-software.gitlab.io/quapps/).

## Description

List of applications implemented based on [``quark``](https://gitlab.com/quantum-computing-software/quark):

* [Max Cut](../quapps/max_cut/README.md)
* [Maximum Colorable Subgraph](../quapps/max_colorable_subgraph/README.md)
* [Flight Gate Assignment](../quapps/flight_gate_assignment/README.md)
* [Ising Model](../quapps/arbitrary_ising/README.md)
* [Prime Factorization](../quapps/prime_factorization/README.md)
* [Minimum k-Union](../quapps/min_k_union/README.md)
* [Traveling Salesperson](../quapps/traveling_salesperson/README.md)
* [Graph Partition](../quapps/graph_partitioning/README.md)
* [Knapsack](../quapps/knapsack/README.md)
* [Subset Sum](../quapps/subset_sum/README.md)


Structure:

Each application subfolder contains

* a ``README.md`` containing the problem description,
* a class derived from ``quark.io.Instance``, 
  serving as a container for all the data defining an instance of the specific problem, 
* a class derived from ``quark.ConstrainedObjective``, ``quark.ObjectiveTerms`` and/or ``quark.Objective`` 
  (although only one of them is required, we added in most cases more, serving as examples), and
* corresponding tests also serving as demonstrators how to use the classes.

All other code for scripts, instance generation, analysis, etc. is placed in different repositories.

## License

This project is [Apache-2.0](https://gitlab.com/quantum-computing-software/quapps/-/blob/development/LICENSE) licensed.

Copyright © 2025 German Aerospace Center (DLR) - Institute of Software Technology (SC). 

Please find the individual contributors [here](https://gitlab.com/quantum-computing-software/quapps/-/blob/development/CONTRIBUTORS) 
and information for citing this package [here](https://gitlab.com/quantum-computing-software/quapps/-/blob/development/CITATION.cff).
