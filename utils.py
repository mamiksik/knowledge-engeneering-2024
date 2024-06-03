from datetime import datetime
from typing import Iterable, Union

from dateutil.rrule import DAILY, rrule
from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.graph import _GraphT, _TripleType

ex = Namespace("KEA")


class GraphExt(Graph):
    def add(self: _GraphT, triple: Union[list["_TripleType"], "_TripleType"]) -> _GraphT:
        if not isinstance(triple, list):
            triple = [triple]

        for t in triple:
            super().add(t)

        return self


def add_dates_to_graph(graph_ref: Graph, *, start_date, end_date):
    # Initialize nodes for all days between the specified start date and end date
    dates = [dt.date() for dt in rrule(
        DAILY,
        dtstart=datetime.strptime(start_date, '%Y-%m-%d'),
        until=datetime.strptime(end_date, '%Y-%m-%d')
    )]

    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        date_uri = URIRef(f"Date/{date_str}")
        graph_ref.add((date_uri, RDF.type, ex.Date))
        graph_ref.add((date_uri, ex.timestamp, Literal(date_str)))

    return graph_ref, dates


def save_graph_to_file(g: Graph, filename: str):
    # Serialize RDF graph to Turtle format
    ttl_data = g.serialize(format='turtle')

    # Save RDF Turtle data to a file
    with open(filename, "w") as f:
        f.write(ttl_data)

    print(f"All data saved to {filename}")
