import click
from lib import stock_info, elon_musk
from utils import GraphExt, save_graph_to_file, add_dates_to_graph


@click.group()
def cli_app():
    pass


@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for stock data")
@click.option("--end-date", default="2020-01-31", help="End date for stock data")
def stock_data_to_ttl(start_date, end_date):
    g = GraphExt()
    add_dates_to_graph(g, start_date=start_date, end_date=end_date)
    stock_info.import_sp_stock_data(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/stock_data.ttl")

@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for stock data")
@click.option("--end-date", default="2020-01-31", help="End date for stock data")
def elon_tweets_to_ttl(start_date, end_date):
    g = GraphExt()
    add_dates_to_graph(g, start_date=start_date, end_date=end_date)
    elon_musk.import_elon_graph(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/elon_musk.ttl")



if __name__ == "__main__":
    cli_app()

