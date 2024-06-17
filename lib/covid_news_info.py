from rdflib import Graph, URIRef, Literal, RDF, Namespace
from datetime import datetime
from dateutil.rrule import rrule, DAILY
from SPARQLWrapper import SPARQLWrapper, JSON
from transformers import pipeline
from tqdm import tqdm
from utils import GraphExt, ex
import pandas as pd


# Convert data to RDF Turtle and add to graph
def add_vaccination_news_to_graph(g: GraphExt, news_data):
    """Add the RDF triples for each vaccination news coverage data and additional information to the same graph"""
    for index, article in tqdm(news_data.iterrows(), desc="Vaccination News Coverage", total=news_data.shape[0]):
        date = article["date"].strftime('%Y-%m-%d')
        
        article_uri = URIRef(ex[f'article_{index}'])
        date_uri = URIRef(ex[f"Date/{date}"])
        avg_sentiment_uri = URIRef(ex[f"AverageVaccinationSentiment/{date}"])

        # Add vaccination news coverage data
        g.add((article_uri, RDF.type, ex.VaccinationNewsCoverage))
        g.add((article_uri, ex.hasDate, date_uri))
        g.add((article_uri, ex.inCountry, Literal(article["country"])))
        g.add((article_uri, ex.atMedia, Literal(article["media"])))
        g.add((article_uri, ex.hasSentiment, Literal(article["sentiment"])))
        g.add((article_uri, ex.hasMentionedCompany, Literal(article["Security"])))

        # Link to Average Vaccination Sentiment node
        g.add((avg_sentiment_uri, RDF.type, ex.AverageVaccinationSentiment))
        g.add((avg_sentiment_uri, ex.hasDate, date_uri))
        g.add((avg_sentiment_uri, ex.hasAverageSentiment, Literal(article["day_sent_cat"])))
        g.add((avg_sentiment_uri, ex.hasDayBefore, Literal(article["daybefore"])))
        g.add((avg_sentiment_uri, ex.hasDayAfter, Literal(article["dayafter"])))
        g.add((avg_sentiment_uri, ex.hasDayBeforeSentiment, Literal(article["dayBefore_sent_cat"])))
        g.add((avg_sentiment_uri, ex.hasDayAfterSentiment, Literal(article["dayAfter_sent_cat"])))
        g.add((avg_sentiment_uri, ex.composedOf, article_uri))


def import_vaccination_news_data(g: Graph, start_date, end_date):
    """Fetch and import vaccination news data into the RDF graph."""
    file_path = 'datasets/df_covid.csv'
    df_covid = pd.read_csv(file_path)
    df_covid['date'] = pd.to_datetime(df_covid['date'], format='%Y-%m-%d')

    # Filter the data based on the provided date range
    mask = (df_covid['date'] >= start_date) & (df_covid['date'] <= end_date)
    filtered_data = df_covid.loc[mask]

    # Add data to RDF graph
    add_vaccination_news_to_graph(g, filtered_data)