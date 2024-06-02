from typing import Iterable, Union

from rdflib import Graph, Namespace
from rdflib.graph import _GraphT, _TripleType

ex = Namespace("KEA")


class GraphExt(Graph):
    def add(self: _GraphT, triple: Union[list["_TripleType"], "_TripleType"]) -> _GraphT:
        if not isinstance(triple, list):
            triple = [triple]

        for t in triple:
            super().add(t)

        return self


def save_graph_to_file(g: Graph, filename: str):
    # Serialize RDF graph to Turtle format
    ttl_data = g.serialize(format='turtle')

    # Save RDF Turtle data to a file
    with open(filename, "w") as f:
        f.write(ttl_data)

    print(f"All data saved to {filename}")
