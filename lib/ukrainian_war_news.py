from collections import namedtuple
import pandas as pd

from rdflib import RDF, Literal, URIRef
from tqdm import tqdm

from utils import GraphExt, ex


def add_row_to_graph(graph_ref: GraphExt, row: namedtuple):
    date_str = row.date.strftime("%Y-%m-%d")

    news_uri = URIRef(f"WarNews/{date_str}/{row.group_id}/{row.id}")

    # Add the news article to the graph
    graph_ref.add([
        (news_uri, RDF.type, ex.WarNews),
        (news_uri, ex.source, Literal(row.group_name)),
        (news_uri, ex.content, Literal(row.text)),
        (news_uri, ex.sentiment, Literal(row.sentiment)),
        (news_uri, ex.onDay, URIRef(f"Date/{date_str}")),
    ])


def import_war_news(
    graph_ref: GraphExt, *,
    pre_processed_data_path: str = 'datasets/preprocessed_war_news.csv',
):
    war_news = pd.read_csv(pre_processed_data_path)
    war_news['date'] = pd.to_datetime(war_news['date'])

    print("Adding war news to graph...")
    with tqdm(war_news.itertuples()) as pbar:
        for row in pbar:
            pbar.set_description(f"Processing {row.id}")
            add_row_to_graph(graph_ref, row)

