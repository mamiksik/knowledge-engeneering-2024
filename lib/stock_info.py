import yfinance as yf
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from dateutil.rrule import rrule, DAILY
from datetime import datetime
from tqdm import tqdm

from utils import GraphExt, ex


def fetch_sp500_companies():
    """Retrieves a list of S&P 500 companies from Wikipedia"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    sp500_table = pd.read_html(url)[0]
    return sp500_table[['Symbol', 'Security']]


def fetch_stock_data(ticker, start_date, end_date):
    """Uses yfinance to download historical stock prices"""
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


def fetch_company_info(company_name):
    """Sends a SPARQL query to DBpedia to get additional information about the company"""
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = f"""
    SELECT ?location ?industry ?foundingYear ?ceo ?numEmployees WHERE {{
      ?company a dbo:Company ;
               rdfs:label "{company_name}"@en ;
               dbo:location ?location ;
               dbo:industry ?industry ;
               dbo:foundingYear ?foundingYear ;
               dbo:ceo ?ceo ;
               dbo:numberOfEmployees ?numEmployees .
      FILTER (lang(?location) = 'en' && lang(?industry) = 'en')
    }} LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results['results']['bindings']


# Convert data to RDF Turtle and add to graph
def add_stock_to_graph(g: GraphExt, ticker, company_info, stock_data):
    """Add the RDF triples for each company's stock data and additional information to the same graph"""

    stock_uri = URIRef(f"Stock/{ticker}")
    g.add([
        (stock_uri, RDF.type, ex.Stock),
        (stock_uri, ex.ticker, Literal(ticker))
    ])

    for index, row in stock_data.iterrows():
        date_str = row.name.strftime("%Y-%m-%d")
        price_point_uri = URIRef(f"PricePoint/{ticker}/{date_str}")
        date_node = URIRef(f"Date/{date_str}")
        g.add([
            (price_point_uri, RDF.type, ex.PricePoint),
            (stock_uri, ex.hasPrice, price_point_uri),
            (price_point_uri, ex.hasTickerSymbol, Literal(ticker)),
            (price_point_uri, ex.onDay, date_node),
            (price_point_uri, ex.hasClosingPrice, Literal(row['Close']))
        ])


def import_sp_stock_data(
        graph_ref: GraphExt, *,
        start_date,
        end_date
):
    """Coordinates the data fetching, enrichment, and serialization processes"""
    # Fetch S&P 500 companies
    sp500_companies = fetch_sp500_companies()

    with tqdm(list(sp500_companies.iterrows())) as pbar:
        for _, row in pbar:
            ticker = row['Symbol']
            company_name = row['Security']

            pbar.set_description(f"Processing {ticker} - {company_name}")

            # Fetch stock data
            stock_data = fetch_stock_data(ticker, start_date, end_date)
            if stock_data.empty:
                print(f"No data for {ticker}")
                continue

            # Fetch additional info from DBpedia
            company_info = fetch_company_info(company_name)
            company_info_dict = {}
            if company_info:
                company_info_dict = {k: v['value'] for k, v in company_info[0].items()}

            # Add data to RDF graph
            add_stock_to_graph(graph_ref, ticker, company_info_dict, stock_data)
