# Sales BI Dashboard

## Context

This sample will show how to configure a BI dashboard (Apache Superset) to use Spice.ai as the data source for sales data. The sales data is stored in a PostgreSQL server. This PostgreSQL server is used by downstream sales applications to record new transactions. There is a requirement to run analytics on this data to power a BI dashboard to understand sales trends - but the operations team doesn't want to add any additional load to the production database.

Spice.ai can be used to accelerate data from connected data sources by keeping an automatically updated copy of the data in an optimized format. This data can be used to power a BI dashboard without adding any additional load to the production database.

## Pre-requisites

This sample requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to be installed.

## Running the sample

![](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/c16c7dda-c403-4c71-0d6d-066005dd0e00/public)

This sample consists of a Docker Compose file with the following components:
- A PostgreSQL server loaded with some sample sales data (`public.cleaned_sales_data`).
- A Spice.ai runtime accelerating the data from the PostgreSQL server.
- An Apache Superset instance to visualize the data, connected to the Spice.ai instance.

Clone the `spiceai/samples` repository and navigate to the `sales-bi` directory:

```bash
git clone https://github.com/spiceai/samples.git
cd samples/sales-bi
```

Run the following command to start the 3 components in the Docker Compose file:

`make`

This will start the PostgreSQL server, Spice.ai runtime, and Apache Superset. The Spice.ai runtime will automatically start locally accelerating the data from the PostgreSQL server, based on the following spicepod:

```yaml
version: v1beta1
kind: Spicepod
name: sales-bi

datasets:
  - from: postgres:public.cleaned_sales_data
    name: cleaned_sales_data
    params:
      pg_host: postgres
      pg_db: postgres
      pg_user: postgres
      pg_pass: postgres
    acceleration:
      enabled: true
      refresh_interval: 10s
      refresh_mode: full
```

The output of the `make` command should look like:

```bash
 ✔ Container superset-sales-bi-demo  Started                                                                                                                                           0.0s
 ✔ Container sales-bi-postgres-1     Started                                                                                                                                           0.0s
 ✔ Container spiceai-sales-bi-demo   Started                                                                                                                                           0.0s
Connection to localhost port 8088 [tcp/radan-http] succeeded!
Initializing Superset...

Superset is running at http://localhost:8088, login with admin/admin
```

Navigate to [http://localhost:8088](http://localhost:8088) to access the Apache Superset dashboard. The login credentials are `admin/admin`.

Once logged in, navigate to the `Sales Dashboard` to view the sales data.

![sales-bi-Sales-Dashboard.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/0c066733-4701-4407-be42-a913f315a500/public)

Click on a product line to view the sales data for that product line, i.e. for `Vintage Cars`:

![sales-bi-Sales-Dashboard-Vintage-Cars.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/c6a1be9c-a7c8-4ac4-d5d5-06514164d600/public)

In the top navigation bar, hover over the `SQL` menu and click on `SQL Lab` to view a query editor. Explore the data from the Spice.ai runtime by running SQL queries, i.e. `SELECT * FROM cleaned_sales_data LIMIT 10`:

![sales-bi-SQL-Lab.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/c90376cf-d56e-49a7-09f1-a1e53979b500/public)

View the connection details for the Spice.ai runtime, hover over the `Settings` menu and click on `Database Connections`. Hover over the `Spice.ai` entry and click the pencil icon. The connection details for the Spice.ai runtime are shown:

![sales-bi-DB-Conn.png](https://imagedelivery.net/HyTs22ttunfIlvyd6vumhQ/6ba7b08c-fa78-4613-646d-c07d9cd4ab00/public)

## Spice SQL REPL
In addition to Apache Superset, run queries using the Spice SQL REPL to explore the data in the Spice.ai runtime.

`docker exec -it spiceai-sales-bi-demo spiced --repl`

```bash
Welcome to the interactive Spice.ai SQL Query Utility! Type 'help' for help.

show tables; -- list available tables
sql> show tables
+---------------+--------------------+--------------------+------------+
| table_catalog | table_schema       | table_name         | table_type |
+---------------+--------------------+--------------------+------------+
| datafusion    | public             | cleaned_sales_data | BASE TABLE |
| datafusion    | information_schema | tables             | VIEW       |
| datafusion    | information_schema | views              | VIEW       |
| datafusion    | information_schema | columns            | VIEW       |
| datafusion    | information_schema | df_settings        | VIEW       |
+---------------+--------------------+--------------------+------------+

Query took: 0.008933628 seconds
sql> select * from cleaned_sales_data limit 1;
sql> select order_date, sales from cleaned_sales_data limit 3;
+---------------------+---------+
| order_date          | sales   |
+---------------------+---------+
| 2003-02-24T00:00:00 | 2871.0  |
| 2003-05-07T00:00:00 | 2765.9  |
| 2003-07-01T00:00:00 | 3884.34 |
+---------------------+---------+

Query took: 0.012897393 seconds
```

## Clean up

To stop and remove the Docker containers/volumes that were created, run:

`make clean`
