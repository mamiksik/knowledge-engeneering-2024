import warnings
from datetime import datetime, timedelta
from typing import Union

import torch
from dateutil.rrule import DAILY, rrule
from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.graph import _GraphT, _TripleType

ex = Namespace("")


class GraphExt(Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, base="http://kea.local/")

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

        # Add reference to the previous day and the next day for each date node if they exist
        if date - dates[0] > timedelta(0):
            previous_date = dates[dates.index(date) - 1].strftime('%Y-%m-%d')
            previous_date_uri = URIRef(f"Date/{previous_date}")
            graph_ref.add((date_uri, ex.previousDay, previous_date_uri))

        if date - dates[-1] < timedelta(0):
            next_date = dates[dates.index(date) + 1].strftime('%Y-%m-%d')
            next_date_uri = URIRef(f"Date/{next_date}")
            graph_ref.add((date_uri, ex.nextDay, next_date_uri))

    return graph_ref, dates


def save_graph_to_file(g: Graph, filename: str):
    # Serialize RDF graph to Turtle format
    ttl_data = g.serialize(format='turtle')

    # Save RDF Turtle data to a file
    with open(filename, "w", encoding='utf-8') as f:
        f.write(ttl_data)

    print(f"All data saved to {filename}")


def get_available_device():
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(torch.ones(1, device=device), "MPS device found")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(torch.ones(1, device=device), "CUDA device found")
    else:
        device = torch.device("cpu")
        warnings.warn(f"MPS and CUDA not available, CPU used. {torch.ones(1, device=device)}")

    return device
