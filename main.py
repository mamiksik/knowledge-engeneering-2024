import click
from lib import stock_info, covid_news_info 
from utils import GraphExt, save_graph_to_file, add_dates_to_graph


@click.group()
def cli_app():
    pass


@cli_app.command()
@click.option("--start-date", default="2020-12-12", help="Start date for stock data")
@click.option("--end-date", default="2021-01-31", help="End date for stock data")
def stock_data_to_ttl(start_date, end_date):
    g = GraphExt()
    add_dates_to_graph(g, start_date=start_date, end_date=end_date)
    stock_info.import_sp_stock_data(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/stock_data.ttl")



@cli_app.command()
@click.option("--start-date", default="2020-01-01", help="Start date for vaccination news data")
@click.option("--end-date", default="2020-12-31", help="End date for vaccination news data")
def vaccination_news_to_ttl(start_date, end_date):
    g = GraphExt()
    covid_news_info.import_vaccination_news_data(g, start_date=start_date, end_date=end_date)
    save_graph_to_file(g, "artifacts/vaccination_news_data.ttl")

if __name__ == "__main__":
    cli_app()

