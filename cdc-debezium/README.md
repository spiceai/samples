# Streaming changes in real-time with Debezium CDC

Change Data Capture (CDC) is a technique to capture changed rows from a database's transaction log and deliver to consumers with low latency. Leveraging this technique allows Spice to keep locally accelerated datasets up-to-date in real-time with the source data, and is highly efficient by only transferring the changed rows instead of re-fetching the entire dataset on refresh.

In this sample we will have a local Postgres database with a table `customer_addresses` and a Spice runtime that accelerates the data from the `customer_addresses` table. A Debezium connector will capture changes from the `customer_addresses` table and publish them to a Kafka topic called `cdc.public.customer_addresses`. The Spice runtime will consume the changes from the Kafka topic and keep an accelerated dataset updated with the changes, including the initial state.

## Pre-requisites

This sample requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

Also ensure that you have the `spice` CLI installed. You can find instructions on how to install it [here](https://docs.spiceai.org/getting-started).

You will also need `psql` or another Database client (i.e. DBeaver) to connect to the Postgres database.

`curl` is required to register the Debezium Postgres connector.

## How to run

Clone this samples repo locally and navigate to the `cdc-debezium` directory:

```bash
git clone https://github.com/spiceai/samples.git
cd samples/cdc-debezium
```

Start the Docker Compose stack, which includes a Postgres database, a Kafka broker (via Redpanda), and a Debezium connector:

`docker compose up -d`

Navigate to http://localhost:8080 to see the Redpanda console. Notice that no topics are created by Debezium yet. We need to tell Debezium to connect to the Postgres database and create the topics.

`curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-connector.json`

Now the Debezium connector is registered and will start capturing changes from the `customer_addresses` table in the Postgres database. Open http://localhost:8080/topics and see the topic `cdc.public.customer_addresses` created.

This spicepod.yaml shows the config needed to configure Spice to connect to the Kafka topic and consume the Debezium changes:

```yaml
version: v1beta1
kind: Spicepod
name: cdc-debezium

datasets:
  - from: debezium:cdc.public.customer_addresses
    name: cdc
    params:
      debezium_transport: kafka
      debezium_message_format: json
      kafka_bootstrap_servers: localhost:19092
    acceleration:
      enabled: true
      engine: sqlite
      mode: file
      refresh_mode: changes
```

Spice runtime is already configured to run with the debug level of information, with environment variable configured in `cdc-debezium/.env`

```
SPICED_LOG="spiced=DEBUG,runtime=DEBUG,data_components=DEBUG,cache=DEBUG"
```

Ensure the current directory is `cdc-debezium`, and start the spice runtime with the following command

```bash
spice run
```

Observe that it consumes all of the changes. It should look like:

```bash
2024-07-01T12:39:22.207145Z  INFO runtime: Dataset cdc registered (debezium:cdc.public.customer_addresses), acceleration (duckdb:file, changes), results cache enabled.
2024-07-01T12:39:22.677117Z  INFO runtime::accelerated_table::refresh_task::changes: Upserting data row for cdc with id=3
2024-07-01T12:39:22.692018Z  INFO runtime::accelerated_table::refresh_task::changes: Upserting data row for cdc with id=4
...
```

Run `spice sql` in a separate terminal to query the data

```sql
SELECT * FROM cdc;
```

Now let's make some changes to the Postgres database and observe that Spice consumes the changes.

Stop the Spice SQL REPL or open a third terminal and connect to the Postgres database with `psql`:

```bash
PGPASSWORD="postgres" psql -h localhost -U postgres -d postgres -p 15432
```

```sql
INSERT INTO public.customer_addresses (id, first_name, last_name, email)
VALUES
(100, 'John', 'Doe', 'john@doe.com');
```

Notice that the Spice log shows the change.

```
2024-08-26T22:29:48.540739Z DEBUG runtime::accelerated_table::refresh_task::changes: Upserting data row for cdc with id=100
```

Querying the data again from the `spice sql` REPL will show the new record.

```sql
SELECT * FROM cdc;
```

Now let's see what happens when we stop Spice and restart it. The data should still be there and it should not replay all of the changes from the beginning.

```
2024-08-26T22:30:16.715586Z  INFO runtime: Dataset cdc registered (debezium:cdc.public.customer_addresses), acceleration (sqlite:file, changes), results cache enabled.
```

Stop spice with `Ctrl+C`

Restart Spice with `spice run`

Observe that it doesn't replay the changes and the data is still there. Only new changes will be consumed.

```
Spice.ai runtime starting...
2024-07-29T23:22:04.303861Z  INFO runtime::flight: Spice Runtime Flight listening on 127.0.0.1:50051
2024-07-29T23:22:04.303925Z  INFO runtime::metrics_server: Spice Runtime Metrics listening on 127.0.0.1:9090
2024-07-29T23:22:04.304011Z  INFO runtime::http: Spice Runtime HTTP listening on 127.0.0.1:8090
2024-07-29T23:22:04.303850Z  INFO runtime: Initialized results cache; max size: 128.00 MiB, item ttl: 1s
2024-07-29T23:22:04.306271Z  INFO runtime::opentelemetry: Spice Runtime OpenTelemetry listening on 127.0.0.1:50052
2024-07-29T23:22:04.331209Z  INFO runtime: Dataset cdc registered (debezium:cdc.public.customer_addresses), acceleration (duckdb:file, changes), results cache enabled.
```

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`

If you don't have the `make` command available, you can run the following commands:

```bash
docker compose down
docker volume prune -f
docker image prune -f
```
