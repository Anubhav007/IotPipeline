# Import Streamlit and cassandra-driver modules
import streamlit as st
import datetime
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

# Connect to the cassandra database using your credentials and keyspace name
auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['127.0.0.1'], port=9042, auth_provider=auth_provider)
session = cluster.connect('test')

# Create a Streamlit app title and a sidebar for user inputs
st.title('Cassandra IoT Data Web Service')
st.sidebar.header('Query Parameters')

with open("config/device_ids.txt", "r") as f:
    devices = list(set(line.strip() for line in f.readlines()))

# Create a multi-select widget for selecting device ids
device_ids = st.sidebar.multiselect(
    'Select device ids',
    options=devices, # You can replace these options with your actual device ids
    default=[devices[0]] # You can change the default option as well
    )

# Create a date input widget for selecting the start date of the query window
start_date = st.sidebar.date_input(
    'Select start date',
    value=datetime.date.today() - datetime.timedelta(days=7) # You can change the default value as well
    )

# Create a time input widget for selecting the start time of the query window
start_time = st.sidebar.time_input(
    'Select start time',
    value=datetime.time(0, 0, 0) # You can change the default value as well
    )

# Create a date input widget for selecting the end date of the query window
end_date = st.sidebar.date_input(
    'Select end date',
    value=datetime.date.today() # You can change the default value as well
    )

# Create a time input widget for selecting the end time of the query window
end_time = st.sidebar.time_input(
    'Select end time',
    value=datetime.time(23, 59, 59) # You can change the default value as well
    )

# Create a selectbox widget for choosing the reading type (e.g average, median, max, min values)
reading_type = st.sidebar.multiselect(
    'Select reading types',
    options=['avg_value', 'median_value', 'max_value', 'min_value'], # You can add more options if you have more reading types in your table schema
    default=['avg_value', 'median_value', 'max_value', 'min_value']# You can change the default index as well
    )

# Convert the user inputs to datetime objects and format them as strings for the query statement
start_datetime = datetime.datetime.combine(start_date, start_time).strftime('%Y-%m-%d %H:%M:%S')
end_datetime = datetime.datetime.combine(end_date, end_time).strftime('%Y-%m-%d %H:%M:%S')

# Construct the query statement based on the user inputs
query_statement = f"""
    SELECT device_id, device_type, window_start_timestamp, window_end_timestamp, {reading_type}
    FROM test.iot_results
    WHERE device_id IN {tuple(device_ids)}
    AND window_start_timestamp >= '{start_datetime}'
    AND window_end_timestamp <= '{end_datetime}'
    ALLOW FILTERING;
    """

# # Execute the query statement and fetch the results
query_results = session.execute(SimpleStatement(query_statement))

# # Display a message indicating how many rows were returned by the query
st.write(f'Query returned {query_results.rowcount} rows.')

# # Display a data table showing the query results
st.dataframe(query_results._current_rows)