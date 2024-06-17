import os
import pandas as pd
from rdflib import Graph, Namespace, URIRef, RDF, Literal, XSD
from utils import GraphExt, ex, add_dates_to_graph, save_graph_to_file


# Define the artifacts directory
artifacts_dir = '/Users/surenskardova/PycharmProjects/knowledge-engeneering-2024/artifacts'
os.makedirs(artifacts_dir, exist_ok=True)

# Load the CSV file
df = pd.read_csv('/Users/surenskardova/Downloads/owid-covid-data.csv')

# Display the first few rows of the DataFrame
print(df.head())
# Display the column names
print(df.columns)

# Display a summary of the DataFrame (including column types and non-null counts)
print(df.info())

# Display descriptive statistics for numerical columns
print(df.describe())

# Filter columns to keep only the necessary ones
columns_needed = ['date', 'location', 'new_vaccinations_smoothed']
filtered_df = df[columns_needed]

# Convert 'Date_reported' to datetime format
filtered_df['date'] = pd.to_datetime(filtered_df['date'], format='%Y-%m-%d')

# Filter rows to include only dates until 30th December 2022
date_cutoff = pd.to_datetime('2022-12-30')
filtered_df = filtered_df[filtered_df['date'] <= date_cutoff]

# Rename columns
filtered_df = filtered_df.rename(columns={
    'date': 'atDate',
    'location': 'country'
})

# Convert 'atDate' back to datetime for new columns calculation
filtered_df['atDate'] = pd.to_datetime(filtered_df['atDate'], format='%Y-%m-%d')

# Create 'dayBefore' and 'dayAfter' columns
filtered_df['dayBefore'] = filtered_df['atDate'] - pd.Timedelta(days=1)
filtered_df['dayAfter'] = filtered_df['atDate'] + pd.Timedelta(days=1)

# Fill NaN values and convert 'amount' to integers
filtered_df['new_vaccinations_smoothed'] = filtered_df['new_vaccinations_smoothed'].fillna(0)
filtered_df['new_vaccinations_smoothed'] = filtered_df['new_vaccinations_smoothed'].astype(int)

# Calculate the cumulative sum of vaccinations for each country
filtered_df['amount'] = filtered_df.groupby('country')['new_vaccinations_smoothed'].cumsum()

# Display the filtered DataFrame
print("\nFiltered DataFrame:")
print(filtered_df.head())

# save to artifacts dir
filtered_csv_path = os.path.join(artifacts_dir, 'filtered_vaccination_data.csv')
filtered_df.to_csv(filtered_csv_path, index=False)


# to RDF
# Load the CSV file
df = pd.read_csv(filtered_csv_path)


# Convert 'atDate' back to datetime for internal processing
df['atDate_dt'] = pd.to_datetime(df['atDate'], format='%Y-%m-%d')
df['dayBefore_dt'] = pd.to_datetime(df['dayBefore'], format='%Y-%m-%d')
df['dayAfter_dt'] = pd.to_datetime(df['dayAfter'], format='%Y-%m-%d')

# Create a new RDF graph using the extended class
g = GraphExt()
g.bind("ex", ex)

# Add date nodes to the graph
start_date = df['atDate_dt'].min().strftime('%Y-%m-%d')
end_date = df['atDate_dt'].max().strftime('%Y-%m-%d')
g, dates = add_dates_to_graph(g, start_date=start_date, end_date=end_date)

# Define RDF classes and properties
Country = URIRef(ex.Country)
VaccinationRecord = URIRef(ex.VaccinationRecord)

hasAmount = URIRef(ex.hasAmount)
hasDate = URIRef(ex.hasDate)
hasDayBefore = URIRef(ex.hasDayBefore)
hasDayAfter = URIRef(ex.hasDayAfter)

# Iterate over the DataFrame and add triples to the graph
for index, row in df.iterrows():
    country_uri = URIRef(ex[row['country'].replace(" ", "_")])
    record_uri = URIRef(ex[f"record_{index}"])
    date_uri = URIRef(f"{ex}Date/{row['atDate_dt'].strftime('%Y-%m-%d')}")
    day_before_uri = URIRef(f"{ex}Date/{row['dayBefore_dt'].strftime('%Y-%m-%d')}")
    day_after_uri = URIRef(f"{ex}Date/{row['dayAfter_dt'].strftime('%Y-%m-%d')}")

    g.add((country_uri, RDF.type, Country))
    g.add((record_uri, RDF.type, VaccinationRecord))
    g.add((record_uri, hasAmount, Literal(row['amount'], datatype=XSD.integer)))
    g.add((record_uri, hasDate, date_uri))
    g.add((record_uri, hasDayBefore, day_before_uri))
    g.add((record_uri, hasDayAfter, day_after_uri))
    g.add((record_uri, ex.country, country_uri))

# Serialize the graph to a file in the artifacts directory
rdf_file_path = os.path.join(artifacts_dir, "vaccination_data.rdf")
save_graph_to_file(g, rdf_file_path)

# Print the graph to the console
print(g.serialize(format="turtle"))
