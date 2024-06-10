# Adding spice as Grafana datasource

## Context

This sample will show how to configure a Grafana dashboard to use Spice as the data source using [FlightSQL](https://grafana.com/grafana/plugins/influxdata-flightsql-datasource/) and [Infinity](https://grafana.com/docs/plugins/yesoreyeram-infinity-datasource/latest/) plugins.

## Pre-requisites

This sample requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## Running the sample

Clone the `spiceai/samples` repository and navigate to the `grafana-datasource` directory:

```bash
git clone https://github.com/spiceai/samples.git
cd samples/grafana-datasource
```

Run the following command to start the components in the Docker Compose file:

`make`

This will start the Spice runtime and Grafana server. The Spice runtime will load two datasets based on the parquet file in S3.

## Setup with FlightSQL Grafana plugin

1. Open Grafana in your browser at [http://localhost:3000](http://localhost:3000).
2. Log in with the default credentials `admin`/`admin`, skip the password change prompt.

![screenshot](./img/grafana-datasource-1.png)

3. Navigate to Administation -> Plugins and data -> Plugins.
4. Select "State: All", and search for "FlightSQL".

![screenshot](./img/grafana-datasource-2.png)

5. Click on the "Install" button to install the plugin, and then "Add new data source".

![screenshot](./img/grafana-datasource-3.png)

6. Fill in the following fields:
   - Name: `Spice`
   - Host:Port: `spice:50051`
   - Auth Type: `None`

![screenshot](./img/grafana-datasource-4.png)

7. Click on "Save & Test" to save the data source, then click on "Build a dashboard".
8. Click on "Add visualization" and select "Spice" from the list of data sources.

![screenshot](./img/grafana-datasource-5.png)

9. Switch to SQL query editor and paste the following query:
   ```sql
   SELECT to_timestamp(tpep_dropoff_datetime), fare_amount FROM public.taxi_trips LIMIT 100
   ```

![screenshot](./img/grafana-datasource-6.png)

### Setup with Infinity Grafana plugin

Follow steps 1-3 from the previous section.

4. Select "State: All", and search for "Infinity". Install and click on "Add new data source".

![screenshot](./img/grafana-datasource-7.png)

5. Leave the default values and click on "Save & Test".

![screenshot](./img/grafana-datasource-8.png)

6. Click on "Build a dashboard" and add a new visualization. Select "Infinity" from the list of data sources.

7. Change "Method" to "POST" and "URL" to `http://spice:5000/v1/sql`. Add SQL query in body, using "Raw" mode:
    ```sql
    SELECT to_timestamp(tpep_dropoff_datetime), fare_amount FROM public.taxi_trips LIMIT 100
    ```

![screenshot](./img/grafana-datasource-9.png)

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`