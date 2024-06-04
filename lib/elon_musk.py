import pandas as pd
from textblob import TextBlob
from rdflib import Graph, URIRef, Literal, RDF, Namespace

from utils import GraphExt, ex


def import_elon_graph(g: GraphExt, start_date, end_date):
    df = pd.read_csv('data/elon_with_companies.csv')

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Extract tweet data
        tweet_text = row['Tweets']
        date = row['Date Created']
        likes = row['Number of Likes']
        source = row['Source of Tweet']
        companies_mentioned = row['Companies']

        # Check if tweet date is within the specified range
        if start_date <= date <= end_date:

            # Perform sentiment analysis
            sentiment = TextBlob(tweet_text).sentiment

            # date_str = row.name.strftime("%Y-%m-%d")

            # Add nodes for tweet, date, and sentiment
            tweet_node = URIRef(ex[f'tweet_{index}'.strip()])
            date_node = URIRef(ex[f'date_{index}'.strip()])
            g.add((tweet_node, RDF.type, ex.Tweet))
            g.add((tweet_node, ex.hasText, Literal(tweet_text)))
            g.add((tweet_node, ex.onDay, Literal(date)))
            g.add((tweet_node, ex.hasLikes, Literal(likes)))
            g.add((tweet_node, ex.hasSource, Literal(source)))

            # # adds the information related to the dates to the date nodes already existing in the graph
            # date_node = None
            # for s, p, o in g.triples((None, ex.hasDate, Literal(date))):
            #     if (s, RDF.type, ex.Date) in g:
            #         date_node = s
            #         break
            #
            # # If the date node does not exist, create a new one
            # if date_node is None:
            #     date_node = URIRef(ex[f'date_{date}'])
            #     g.add((date_node, RDF.type, ex.Date))
            #     g.add((date_node, ex.hasDate, Literal(date)))

            g.add((tweet_node, ex.onDay, date_node))

            g.add((tweet_node, ex.hasSentiment, Literal(sentiment.polarity)))
            g.add((tweet_node, ex.hasSubjectivity, Literal(sentiment.subjectivity)))

            # Extract companies mentioned and add as nodes
            # Assuming you have a function to extract companies mentioned
            # companies_mentioned = extract_companies_mentioned(tweet_text)
            for company in companies_mentioned:
                company_node = URIRef(ex[company.split()])
                g.add((company_node, RDF.type, ex.Company))
                g.add((tweet_node, ex.mentions, company_node))
