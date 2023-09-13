CREATE KEYSPACE test WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};

CREATE TABLE test.iot_results (
device_id text,
device_type text,
window_start_timestamp timestamp,
window_end_timestamp timestamp,
avg_value double,
median_value double,
max_value double,
min_value double,
PRIMARY KEY (device_id, window_start_timestamp, window_end_timestamp)
);

