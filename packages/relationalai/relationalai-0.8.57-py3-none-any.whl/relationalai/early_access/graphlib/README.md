# graphlib

This library allows users to define simple graphs, compute relations (algorithms) over those graphs, and work with the results, all in query builder.

This guide assumes you have a functional PyRel environment; to set one up, please see [the README for the relationalai-python repository](https://github.com/RelationalAI/relationalai-python/blob/main/README.md). It also assumes that you are familiar with query builder syntax; if not, please see [this overview of query builder syntax](https://github.com/RelationalAI/relationalai-python/blob/main/examples/builder/examples.py).

For information beyond what exists in this document, every public method (algorithm) of this library's `Graph` class carries a docstring describing its behavior and providing at least one usage example.


# Development status

This library is still in the early stages of development. Please expect to encounter all manner of rough edges. Not all planned functionality is implemented. The graph constructors have only minimal guard rails. The interfaces of several algorithms _will_ change. Performance is appropriate only for exploring with toy graphs; there are known asymptotic catastrophes. For a rough sense of status and roadmap, please see [the Jira initiative tracking this library's development](https://relationalai.atlassian.net/browse/RAI-38809).


## Quick start guide

Let's start with an example of building a toy directed, weighted graph, and compute something over it.

```python
# Import necessary query builder components.
from relationalai.early_access.builder import Model
from relationalai.early_access.builder import Integer, Float
from relationalai.early_access.builder import define, select

# Import necessary graphlib components.
from relationalai.early_access.graphlib import Graph
# The library's main component is the `Graph` class. Construct instances
# of this class to build graphs, and call member methods of instances
# to compute over those graphs.

# Construct an unweighted, directed graph.
graph = Graph(directed=True, weighted=False)

# Instances of the `Graph` class contain `Node` and `Edge` concepts,
# populating which defines the graph.
Node, Edge = graph.Node, graph.Edge

# Define four nodes from integer literals.
n1 = Node.new(id=1)
n2 = Node.new(id=2)
n3 = Node.new(id=3)
n4 = Node.new(id=4)
define(n1, n2, n3, n4)

# Define four edges between those nodes, forming a kite (a triangle with a tail).
define(
    # The triangle.
    Edge.new(src=n1, dst=n2),
    Edge.new(src=n2, dst=n3),
    Edge.new(src=n3, dst=n1),
    # Its tail.
    Edge.new(src=n3, dst=n4),
)

# Compute the outdegree of each node. Note that computations over graphs
# are nominally exposed as `Relationship`s containing the results of
# those computations. For example, here we retrieve the graph's
# `outdegree` `Relationship`, a binary relation mapping
# each node (`Node`) to its outdegree (`Integer`).
outdegree = graph.outdegree()

# Query and inspect the contents of the `degree` `Relationship`.
select(Node.id, Integer).where(outdegree(Node, Integer)).inspect()
# The output will show the degree for each node, roughly:
#    id  int
# 0   1    1
# 1   2    1
# 2   3    2
# 3   4    0
```

Next, let's do nearly the same, but populate the graph from other `Concept`s and `Relationship`s.

```python
from relationalai.early_access.builder import Model
from relationalai.early_access.builder import Integer, Float
from relationalai.early_access.builder import define, select

from relationalai.early_access.graphlib import Graph

model = Model("test")

# Let's suppose we have a knows-network defined via a `Person` `Concept`
# and a `Person.knows` `Relationship`.
Person = model.Concept("Person")
Person.knows = model.Relationship("{Person} knows {Person}")

# Let's suppose our knows-network involves four people.
joe = Person.new(name="Joe")
jane = Person.new(name="Jane")
james = Person.new(name="James")
jennie = Person.new(name="Jennie")
define(joe, jane, james, jennie)

# Somehow their knows-relationship forms a kite!
define(
    # A knows triangle.
    joe.knows(jane),
    jane.knows(james),
    james.knows(joe),
    # The knows-triangle tail.
    james.knows(jennie),
)

# Let's build an unweighted graph from our knows-network, but supposing that
# "know"ing is symmetric, let's make the graph undirected this time.
graph = Graph(directed=False, weighted=False)
Node, Edge = graph.Node, graph.Edge

# Define the graph's nodes from the knows-network's `Person` `Concept`.
define(Node.new(person=Person))
# TODO: Verify after the new model attachment issues have been sorted out.

# Define the graph's edges from the knows-network's `Person.knows` `Relationship`.
node_a, node_b = Node.ref(), Node.ref()
person_a, person_b = Person.ref(), Person.ref()
where(
    person_a.knows(person_b),
    node_a.person == person_a,
    node_b.person == person_b,
    # Alternative:
    #   node_a.person.knows(node_b.person)
    # Alternative:
    #   person_a.knows(person_b),
    #   node_a := Node.new(person=person_a),
    #   node_b := Node.new(person=person_b),
).define(
    Edge.new(src=node_a, dst=node_b)
)
# TODO: Verify after the new model attachment issues have been sorted out.

# Compute the number of other people each person knows,
# or in other words the degree of each node.
degree = graph.degree()

# Query and inspect the contents of the `degree` `Relationship`.
select(Node.person.name, Integer).where(degree(Node, Integer)).inspect()
# The output will show the degree for each person, roughly:
# ("Joe", 2)
# ("Jane", 2)
# ("James", 3)
# ("Jennie", 1)
# TODO: Verify after the new model attachment issues have been sorted out.
```

Finally, let's spice this up a bit by modeling a transactions network, requiring a weighted graph:

```python
from relationalai.early_access.builder import Model
from relationalai.early_access.builder import Integer, Float
from relationalai.early_access.builder import define, select

from relationalai.early_access.graphlib import Graph

model = Model("test")

Person = model.Concept("Person")

joe = Person.new(name="Joe")
jane = Person.new(name="Jane")
james = Person.new(name="James")
jennie = Person.new(name="Jennie")
define(joe, jane, james, jennie)

# Transfers again form a kite!
transfers = model.Relationship("{person_a:Person} sent {person_b:Person} {amount:Float}")
define(
    # A transfer triangle.
    transfers(joe, jane, 12.34),
    transfers(jane, james, 56.78),
    transfers(james, joe, 91.23),
    # The transfer-triangle tail.
    transfers(james, jennie, 45.67),
)

# Let's build a directed, weighted graph from our transfer network.
graph = Graph(directed=True, weighted=True)
Node, Edge = graph.Node, graph.Edge

# Define the graph's nodes from the `Person`s `Concept`.
define(Node.new(person=Person))
# TODO: Verify after the new model attachment issues have been sorted out.

# Define the graph's edges from the transfer network's `transfer` `Relationship`.
amount = Float.ref()
node_a, node_b = Node.ref(), Node.ref()
person_a, person_b = Person.ref(), Person.ref()
where(
    transfer(person_a, person_b, amount),
    node_a.person == person_a,
    node_b.person == person_b,
    # Alternative:
    #   transfer(node_a.person, node_b.person, amount)
    # Alternative:
    #   transfer(person_a, person_b, amount),
    #   node_a := Node.new(person=person_a),
    #   node_b := Node.new(person=person_b),
).define(
    Edge.new(src=node_a, dst=node_b)
)
# TODO: Verify after the new model attachment issues have been sorted out.

# Compute the transfer volume each person has been involved in,
# or in other words the weighted degree of each node.
weighted_degree = weighted_graph.degree()

# Query and inspect the contents of the `weighted_degree` `Relationship`.
select(Node.person.name, Float).where(weighted_degree(Node, Float)).inspect()
# The output will show the weighted degree for each perso, roughly:
# ("Joe", ...)
# ("Jane", ...)
# ("James", ...)
# ("Jennie", ...)
```

# Core concepts

## The `Graph` class

The library's central component is the `Graph` class. Define graphs by
constructing instances of this class, and call member methods on such instances
to compute over those graphs.

`Graph`s may be directed or undirected, and weighted or unweighted. The required
`directed` and `weighted` keyword arguments allow specification of the graph type.
For example, the following constructs a directed, weighted graph:
```
graph = Graph(directed=True, weighted=True)
```
The `Graph` class constructor accepts an optional `aggregator` keyword argument,
which at this time only allows the `None` value; in future, this keyword argument
will allow specification of how multi-edges should be aggregated when projecting
the rich, high-level graph specification in terms of `Node`s and `Edge`s (see below)
to a simple graph over which to compute.

Instances of the `Graph` class contain `Node` and `Edge` concepts, population
of which allows for rich, high-level definition of property multigraphs,
which are projected to simple graphs under the hood:
```
Node, Edge = graph.Node, graph.Edge

# Define three `Node`s from string literals.
joe_node = Node.new(name="Joe")
jane_node = Node.new(name="Jane")
james_node = Node.new(name="James")
define(joe_node, jane_node, james_node)

# Define `Edge`s forming a directed, weighted triangle between those `Node`s.
define(
    Edge.new(src=joe_node, dst=jane_node, weight=1.0),
    Edge.new(src=jane_node, dst=james_node, weight=2.0),
    Edge.new(src=james_node, dst=joe_node, weight=3.0),
)
```
Every `Edge` must have a `src` and `dst`. If the graph is weighted, every edge
must have a `weight`; if the graph is unweighted, no edge may have a `weight`.
`Error`s are derived when these conditions don't hold. `Node`s and `Edge`s
may otherwise have any number and kind of properties attached to them; note that
all properties mentioned in `Node.new(...)` and `Edge.new(...)` get rolled into
the correspondingly defined `Node`'s / `Edge`'s identity, such that, e.g.,
```
define(
    Node.new(id=1, color="pink"),
    Node.new(id=1, color="sky blue"),
)
define(
    Edge.new(src=joe_node, dst=jane_node, weight=1.0, txid=1),
    Edge.new(src=joe_node, dst=jane_node, weight=1.0, txid=2),
)
```
defines two distinct `Node`s and two distinct `Edge`s (a multi-edge).

With `aggregator = None`, multi-edges (express or implied) will result in
derivation of an `Error`; in future, other `aggregator` choices will allow
automatic aggregation of multi-edges in the under-the-hood projection
to simple graphs.

At this time, `weight`s must be non-negative (zero or positive) `Float`s,
and may not be `inf` or `NaN`. In the near future, `Error`s will be derived
when these conditions don't hold.

## Computing over `Graph`s

To compute over a graph, call member methods, for example:
```
degree = graph.degree()
```
Such methods return `Relationship`s that contain the result of the corresponding
computation. For example, in this case `degree` binds an arity-two `Relationship`
that maps from `Node`s to corresponding `Integer` degrees, conceptually:
```
Relationship("{node:Node} has {degree:Integer}")
```
Such `Relationship`s can be used like any other query builder `Relationship`.
For example, we could inspect that `Relationship`'s contents to see the
degrees of the `Node`s in the graph:
```
degree.inspect()
```

There are notable exceptions, namely `is_connected` at time of this writing,
that return a query builder logic `Fragment` instead of a `Relationship`.
In the case of `is_connected`, this `Fragment` is a condition (`where` clause)
that can be uesd as a filter on whether the graph is connected. In future,
other member methods may return other `Fragment`s, for example in-line logic
for relations such as `degree`, as an alternative to receiving a corresponding
`Relationship`.

Some member methods, corresponding to parameterized algorithms, accept
keyword arguments that provide algorithm configuration. (At time of this writing,
none of the relevant algorithms have landed, but all of them have been stubbed
out.) For example, to compute `pagerank` over a graph with given damping
factor and convergence tolerance:
```
pagerank = graph.pagerank(
    damping_factor=0.9,
    tolerance=1e-7
)


# Algorithm implementation status

This list is rapidly evolving; it may be out of date. The most up to date
reference is the set of member methods of the `Graph` class.

**NOTE!** Please note that the interface to some of this functionality _will_ change.
(Notably, as we work to remove demand transformation, the interface for any
relation that was/is on-demand will change. Practically speaking, that includes
any relation that produces more tuples than roughly a linear number
in the number of nodes in the graph. Other interfaces may change in that
process as well.)

As of this writing, the following algorithms are available:
- num_nodes
- num_edges
- neighbor
- inneighbor
- outneighbor
- common_neighbor
- degree
- indegree
- outdegree
- weighted_degree
- weighted_indegree
- weighted_outdegree
- distance
- diameter_range
- reachable_from
- is_connected
- weakly_connected_component
- adamic_adar
- cosine_similarity
- jaccard_similarity
- preferential_attachment
- local_clustering_coefficient
- average_clustering_coefficient
- degree_centrality
- triangle
- num_triangles
- triangle_count
- unique_triangle

The following algorithms are stubbed out, but not yet implemented
(will yield a `NotImplemented` exception when called):
- pagerank
- infomap
- louvain
- label_propagation
- eigenvector_centrality
- betweenness_centrality
- triangle_community


## Testing

Please see the README.md in this package's `tests` subdirectory for
explanation of this package's tests' present location, in
`relationalai-python/tests/early-access/graphlib`.

To run the tests, the relationalai-python repository's virtual environment
must be correctly set up (please see the repository's README.md), and assuming
we are at that repository's top level:
```bash
cd relationalai-python # repository top level
pytest [-s] [--verbose] relationalai-python/tests/early-access/graphlib/[test_${functionality}.py] [-k '${filter}']
```
where `-s`, `--verbose`, specification of a particular test file
`test_${functionality}.py` (e.g. `test_num_nodes.py`), and specification
of a test filter `-k ${filter}` (e.g. `-k 'multiple_self_loops`) are optional.


## Requirements [TODO]

- relationalai
