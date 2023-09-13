# IoT Pipeline

The purpose of this project is to simulate 3 IoT devices namely - Thermostat, Heart Rate meter and Fuel Gauge, emitting data continuously at every 5 second interval. The project contains a realtime streaming pipeline which processes this data, compute aggregates and stores it on a scalable datastore. Lastly it also exposes a web service to query the aggregated data for a given device_id and timeframe. 

Get started:
1. Installation Process
2. Prepare docker-compose file
3. Running docker-compose file
4. Simulating the IoT sensors through Kafka.
5. Apache Spark structured streaming
6. Web Service for querying results

### 1. Installation Processes
You are able to install all required components to realize this project using the given steps.

#### Installation of Docker on Ubuntu
You can utilize this [URL](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)

#### Installation of Libraries on Local system
>:exclamation: You should have Python 3 installed on your machine
```
Go to IotPipeline folder and run the below command
pip install -r requirements.txt
```

### 2. Prepare Docker-Compose File
First of all, we generated a network called datapipeline for the architecture. The architecture consists of 4 services and each has a static IP address and uses the default port as the given below:
- Spark: 172.18.0.2
- Zookeeper: 172.18.0.3
- Kafka: 172.18.0.4
- Cassandra : 172.18.0.5

We use "volumes" to import our scripts to containers.
>:exclamation: You have to implement " ../IotPipeline:/home"  part for your system.
>:exclamation: You have to create two volumes on your local system namely "/opt/spark/conf/spark-default.conf" and "/opt/spark/jars part. You can do so by running the following command
```
sudo mkdir -p /opt/spark/conf/
sudo cp spark-default.conf /opt/spark/conf/
sudo mkdir -p /opt/spark/jars/ 
``` 

### 3. Running docker-compose file
Open your workspace folder which includes all files provided and run the given command as below.
```
# run docker-compose file
docker-compose up

# check if all 4 containers are running
docker ps
```
After all container is running, you can proceed with the next steps.

#### 4. Prepare Kafka for Use Case
First of all, we will create a new Kafka topic namely *iot_data* for IoT sensors data using the given commands:
```
# Execute kafka container with container id given above
docker exec -it 1c31511ce206 bash

# Create Kafka "iot_data" topic
kafka$ kafka-topics.sh --create --topic iot_data --partitions 1 --replication-factor 1 -bootstrap-server localhost:9092
```
#### Check Kafka setup through Zookeeper
```
# Execute zookeeper container with container id given above
docker exec -it 1c31511ce206 bash

# run command
opt/bitnami/zookeeper/bin/zkCli.sh -server localhost:2181

# list all brokers running
ls /brokers/ids

You will see 1 as one of the broker ids since we have mentioned KAFKA_BROKER_ID=1 in our docker_compose.yml

# list all brokers topic
ls /brokers/topics
```
You will see iot_data as one of the topics.

#### 5. Prepare Cassandra for Use Case
Initially, we will create a *keyspace* and then a *table* in it using given command:
```
# Execute cassandra container with container id given above
docker exec -it 1c31511ce206 bash

# Open the cqlsh and run CreateTable.cql to create iot_results table under test keyspace
cqlsh -u cassandra -p cassandra -f CreateTable.cql

# Check if your setup is correct
cqlsh> DESCRIBE test.iot_results
```

### 6. Execution
If you are sure that all preparations are done, you can start a demo. You have to follow the given steps .

#### Start Kafka Producer locally and publish IoT data to Kafka.
```
# open terminal on your local system and run KafkaProducer.py
python3 KafkaProducer.py
```
This will start printing the sensor data continuously on the terminal at an interval of 5 seconds.

#### Start Streaming to Cassandra
```
# Execute spark container with container id given above
docker exec -it e3080e48085c bash

# go to /home/src/processor and run given command
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0,com.datastax.spark:spark-cassandra-connector_2.12:3.0.0 StreamingKafka2Cassandra.py
```
After the Spark packages are downloaded and spark context is run, you will see schema of the data printed on screen

After all the process is done, we got the data in our Cassandra table

You can query the given command to see your table:
```
# Then write select query to see content of the table, you should see some data after 60 seconds
cqlsh> select * from test.iot_results
```

#### Start the Web service to query results

```
# Go to IotPipeline/src/service folder and execute the below command to run the web service
streamlit run AppServer.py
```

The app will get open in the browser. Adjust the Query parameters i.e device ids, start date & time, end date & time, and reading type and you will see the selected reading types for the specified time range in 1 minute intervals. 
