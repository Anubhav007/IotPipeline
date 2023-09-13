# from pyspark import SparkContext
# sc = SparkContext("master", "KafkaSendStream") 
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# Define constants
BROKER = 'localhost:9092'
TOPIC = 'iot_data'

# Improvement: Keep the devices and ranges in a config file for easy add/remove without changing the producer
with open("config/device_ids.txt", "r") as f:
    devices = list(set(line.strip() for line in f.readlines()))

# Add range of values for all sensors
device_value_range = {
    "thermostat" : [15, 25],
    "heart_rate_meter" : [60, 120],
    "fuel_gauge" : [0, 100]
}

# Create producer object
# producer = KafkaProducer(bootstrap_servers=BROKER,
# value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Generate and send data for each device every 5 second
while True:
    for i in range(len(devices)):

        device_type = devices[i].split("_")[0]

        # Generate random value within range
        if device_type in device_value_range:
            value = random.randint(device_value_range[device_type][0], device_value_range[device_type][1])
        else:
            value = random.randint(0, 100)

        # Create message with device id, timestamp, and value
        message = {
        'device_id': devices[i],
        'device_type': device_type,
        'timestamp': datetime.now().isoformat(),
        'value': value
        }

        # Send message to topic
        # producer.send(TOPIC, message)

        # Print message for debugging purposes
        print(message)

        # Wait one second before next iteration
        time.sleep(5)