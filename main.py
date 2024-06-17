import click
from lib import stock_info, elon_musk, covid_news_info
from tqdm import tqdm

from lib import stock_info, ukrainian_war_news
from utils import GraphExt, save_graph_to_file, add_dates_to_graph, ex


@click.group()
def cli_app():
    pass


@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for stock data")
@click.option("--end-date", default="2022-12-31", help="End date for stock data")
def stock_data_to_ttl(start_date, end_date):
    g = GraphExt()
    add_dates_to_graph(g, start_date=start_date, end_date=end_date)
    stock_info.import_sp_stock_data(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/stock_data.ttl")


@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for stock data")
@click.option("--end-date", default="2022-12-31", help="End date for stock data")
def elon_tweets_to_ttl(start_date, end_date):
    g = GraphExt()
    add_dates_to_graph(g, start_date=start_date, end_date=end_date)
    elon_musk.import_elon_graph(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/elon_musk.ttl")


@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for stock data")
@click.option("--end-date", default="2022-12-31", help="End date for stock data")
@click.option("--path", default="datasets/preprocessed_war_news.csv", help="Path to preprocessed data")
def war_news_to_ttl(start_date, end_date, path):
    g = GraphExt()
    g, dates = add_dates_to_graph(g, start_date=start_date, end_date=end_date)
    ukrainian_war_news.import_war_news(g, pre_processed_data_path=path)
    save_graph_to_file(g, "artifacts/war_news.ttl")


@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for vaccination news data")
@click.option("--end-date", default="2022-12-31", help="End date for vaccination news data")
def vaccination_news_to_ttl(start_date, end_date):
    g = GraphExt()
    covid_news_info.import_vaccination_news_data(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/vaccination_news_data.ttl")


@cli_app.command()
def combine_graphs():
    graphs: [str] = [
        'artifacts/stock_data.ttl',
        'artifacts/war_news.ttl',
        'artifacts/elon_musk.ttl',
        'artifacts/vaccination_news_data.ttl'
    ]

    print("Loading graphs...")
    combined_graph = GraphExt()
    for graph in tqdm(graphs):
        g = GraphExt().parse(graph, format='ttl')
        combined_graph += g

    save_graph_to_file(combined_graph, "artifacts/combined_data.ttl")


if __name__ == "__main__":
    cli_app()

